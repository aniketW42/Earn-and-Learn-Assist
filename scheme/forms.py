from django import forms
from .models import (SchemeApplication, WorkLog, Department, DepartmentIncharge, 
                    StudentDepartmentAssignment, PaymentRate, PaymentCalculation)
from users.models import User
import re
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from decimal import Decimal

class SchemeApplicationForm(forms.ModelForm):
    class Meta:
        model = SchemeApplication
        fields = [
            "first_name", "middle_name", "last_name",
            "address", "state", "dob", "annual_income",
            "fathers_occupation", "caste_category",
            "college_name", "department", "prn_number",

            "photo", "application_form", "income_certificate",
            "caste_certificate", "last_year_marksheet",
            "domicile_certificate", "admission_receipt",
            "aadhar_card", "bank_passbook", "caste_validity_certificate"
        ]
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "annual_income": forms.NumberInput(attrs={"min": 0}),
            "prn_number": forms.TextInput(attrs={"placeholder": "e.g. 124M1H029"}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'application_form': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'income_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caste_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'last_year_marksheet': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'domicile_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'admission_receipt': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'aadhar_card': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bank_passbook': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caste_validity_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_prn_number(self):
        prn = self.cleaned_data.get('prn_number', '').strip().upper()
        if not prn:
            raise forms.ValidationError("PRN number is required.")
        
        # Validate PRN format (e.g., 124M1H029)
        prn_pattern = r'^\d{2,3}[A-Z]\d[A-Z]\d{3}$'
        if not re.match(prn_pattern, prn):
            raise forms.ValidationError("PRN number format is invalid. Example: 124M1H029")
        
        return prn

    def clean_annual_income(self):
        income = self.cleaned_data.get('annual_income')
        if income is None:
            raise forms.ValidationError("Annual income is required.")
        if income < 0:
            raise forms.ValidationError("Annual income cannot be negative.")
        if income > 10000000:  # 1 crore limit
            raise forms.ValidationError("Annual income seems too high. Please verify.")
        return income



class WorkLogForm(forms.ModelForm):
    class Meta:
        model = WorkLog
        fields = ["hours_worked", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "hours_worked": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "3"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_hours_worked(self):
        hours = self.cleaned_data.get('hours_worked')
        if hours is None:
            raise forms.ValidationError("Hours worked is required.")
        if hours < 1 or hours > 3:
            raise forms.ValidationError("Hours worked must be between 1 and 3 hours per day.")
        return hours

    def clean(self):
        cleaned_data = super().clean()
        hours_worked = cleaned_data.get('hours_worked')
        
        if self.user and hours_worked:
            from django.utils import timezone
            from django.db.models import Sum
            
            # Check if today is Sunday
            today = timezone.now().date()
            if today.weekday() == 6:  # Sunday is weekday 6
                raise forms.ValidationError("Work logs cannot be added on Sundays.")
            
            # Check if user already has a work log for today
            existing_worklog = WorkLog.objects.filter(
                student=self.user,
                date=today
            )
            
            # If this is an update, exclude the current instance
            if self.instance and self.instance.pk:
                existing_worklog = existing_worklog.exclude(pk=self.instance.pk)
            
            if existing_worklog.exists():
                raise forms.ValidationError("You can only submit one work log per day.")
            
            # Check monthly hours limit
            current_month_hours = WorkLog.objects.filter(
                student=self.user,
                date__year=today.year,
                date__month=today.month,
                is_rejected=False
            )
            
            # Exclude current instance if updating
            if self.instance and self.instance.pk:
                current_month_hours = current_month_hours.exclude(pk=self.instance.pk)
            
            total_hours = current_month_hours.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
            
            if total_hours + hours_worked > 30:
                remaining_hours = 30 - total_hours
                if remaining_hours <= 0:
                    raise forms.ValidationError("Monthly limit of 30 hours has been reached for this month.")
                else:
                    raise forms.ValidationError(f"Adding {hours_worked} hours would exceed monthly limit. You can only add {remaining_hours} more hours this month.")
        
        return cleaned_data

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise forms.ValidationError("Work description is required.")
        if len(description) < 10:
            raise forms.ValidationError("Please provide a more detailed description (at least 10 characters).")
        return description

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Engineering'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CSE', 'style': 'text-transform: uppercase'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department description...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        if not code:
            raise forms.ValidationError("Department code is required.")
        if len(code) > 10:
            raise forms.ValidationError("Department code should be 10 characters or less.")
        return code

class DepartmentInchargeCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True, incharge__isnull=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select a department that doesn't have an incharge assigned"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'department']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

class StudentDepartmentAssignmentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role='student', is_registered=True, studentdepartmentassignment__isnull=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select a student who hasn't been assigned to any department"
    )
    
    class Meta:
        model = StudentDepartmentAssignment
        fields = ['student', 'department']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)

class BulkStudentAssignmentForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='student', is_registered=True, studentdepartmentassignment__isnull=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        help_text="Select students to assign to the department"
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )


# Payment Module Forms

class PaymentRateForm(forms.ModelForm):
    """Form for E&L Coordinator to set/update payment rates"""
    
    class Meta:
        model = PaymentRate
        fields = ['rate_per_hour', 'notes']
        widgets = {
            'rate_per_hour': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Enter rate per hour (₹)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this rate change...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If updating an existing rate, show current value
        if self.instance and self.instance.pk:
            self.fields['rate_per_hour'].help_text = f"Current rate: ₹{self.instance.rate_per_hour}/hour"
        
        # Mark required fields
        self.fields['rate_per_hour'].required = True
        self.fields['notes'].required = False


class PaymentReportFilterForm(forms.Form):
    """Form for filtering payment reports"""
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    year = forms.ChoiceField(
        choices=[(year, year) for year in range(2023, timezone.now().year + 2)],
        initial=timezone.now().year,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        initial=timezone.now().month,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role='student', is_registered=True),
        required=False,
        empty_label="All Students",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is department incharge, filter students by their department
        if user and hasattr(user, 'departmentincharge'):
            department = user.departmentincharge.department
            self.fields['student'].queryset = User.objects.filter(
                role='student',
                is_registered=True,
                studentdepartmentassignment__department=department,
                studentdepartmentassignment__is_active=True
            )
            # Hide department field for department incharge
            self.fields['department'].widget = forms.HiddenInput()
            self.fields['department'].initial = department


# PaymentRecordUpdateForm removed - no longer tracking payment status


class PaymentCalculationForm(forms.Form):
    """Form for bulk payment calculation"""
    year = forms.ChoiceField(
        choices=[(year, year) for year in range(2023, timezone.now().year + 2)],
        initial=timezone.now().year,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    month = forms.ChoiceField(
        choices=PaymentReportFilterForm.MONTH_CHOICES,
        initial=timezone.now().month,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    recalculate_existing = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Check to recalculate existing payment records"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is department incharge, limit to their department
        if user and hasattr(user, 'departmentincharge'):
            department = user.departmentincharge.department
            self.fields['department'].widget = forms.HiddenInput()
            self.fields['department'].initial = department


class StudentPaymentSearchForm(forms.Form):
    """Form for student to search their payment history"""
    year = forms.ChoiceField(
        choices=[('', 'All Years')] + [(year, year) for year in range(2023, timezone.now().year + 2)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    month = forms.ChoiceField(
        choices=[('', 'All Months')] + PaymentReportFilterForm.MONTH_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Status field removed - no longer tracking payment status
