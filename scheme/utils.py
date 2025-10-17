"""
Utility functions for pagination and filtering
"""
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def get_paginated_queryset(request, queryset, per_page_default=10, per_page_options=None):
    """
    Utility function to handle pagination with consistent behavior
    
    Args:
        request: Django request object
        queryset: QuerySet to paginate
        per_page_default: Default number of items per page
        per_page_options: List of allowed per_page values
        
    Returns:
        tuple: (page_obj, per_page_value, per_page_options)
    """
    if per_page_options is None:
        per_page_options = [5, 10, 15, 25, 50]
    
    # Get and validate per_page parameter
    per_page = request.GET.get('per_page', str(per_page_default))
    try:
        per_page = int(per_page)
        if per_page not in per_page_options:
            per_page = per_page_default
    except (ValueError, TypeError):
        per_page = per_page_default
    
    # Create paginator
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj, per_page, per_page_options


def apply_search_filter(queryset, search_term, search_fields):
    """
    Apply search filter to queryset
    
    Args:
        queryset: QuerySet to filter
        search_term: Search term from request
        search_fields: List of fields to search in
        
    Returns:
        QuerySet: Filtered queryset
    """
    if not search_term or not search_fields:
        return queryset
    
    # Build Q object for OR search across multiple fields
    search_query = Q()
    for field in search_fields:
        search_query |= Q(**{f"{field}__icontains": search_term})
    
    return queryset.filter(search_query)


def apply_date_range_filter(queryset, date_from, date_to, date_field='date'):
    """
    Apply date range filter to queryset
    
    Args:
        queryset: QuerySet to filter
        date_from: Start date
        date_to: End date
        date_field: Field name to filter on
        
    Returns:
        QuerySet: Filtered queryset
    """
    if date_from:
        queryset = queryset.filter(**{f"{date_field}__gte": date_from})
    if date_to:
        queryset = queryset.filter(**{f"{date_field}__lte": date_to})
    return queryset


def get_filter_context(request, **kwargs):
    """
    Get context for filter template
    
    Args:
        request: Django request object
        **kwargs: Additional context variables
        
    Returns:
        dict: Context for filter template
    """
    context = {
        'show_search': kwargs.get('show_search', False),
        'show_status_filter': kwargs.get('show_status_filter', False),
        'show_department_filter': kwargs.get('show_department_filter', False),
        'show_date_filter': kwargs.get('show_date_filter', False),
        'show_export': kwargs.get('show_export', False),
        'status_options': kwargs.get('status_options', []),
        'departments': kwargs.get('departments', []),
        'per_page_options': kwargs.get('per_page_options', [5, 10, 15, 25, 50]),
    }
    return context
