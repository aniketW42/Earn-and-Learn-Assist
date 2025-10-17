from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import os
import datetime

def validate_file_size(file):
    """ Limit file size to 2 MB (2 * 1024 * 1024 bytes) """
    max_size = 2 * 1024 * 1024 
    if file.size > max_size:
        raise ValidationError(f"File size should be less than {max_size / (1024 * 1024):.2f} MB")

def validate_image_file(file):
    """ Validate that uploaded file is an image """
    validate_file_size(file)
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Only image files (JPG, PNG, GIF, BMP) are allowed.")

def validate_pdf_file(file):
    """ Validate that uploaded file is a PDF """
    validate_file_size(file)
    valid_extensions = ['.pdf']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Only PDF files are allowed.")

class SchemeApplication(models.Model):
    CASTE_CATEGORIES = [
        ('General', 'General'),
        ('OBC', 'Other Backward Class (OBC)'),
        ('SC', 'Scheduled Caste (SC)'),
        ('ST', 'Scheduled Tribe (ST)'),
        ('NT', 'Nomadic Tribes (NT)'),
        ('VJNT', 'Vimukta Jati Nomadic Tribes (VJNT)'),
        ('EWS', 'Economically Weaker Section (EWS)'),
        ('SBC', 'Special Backward Class (SBC)'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Student Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    address = models.TextField()
    state = models.CharField(max_length=100)
    dob = models.DateField()
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    fathers_occupation = models.CharField(max_length=255)
    caste_category = models.CharField(max_length=20, choices=CASTE_CATEGORIES)

    # College Details
    COLLEGE_NAME = "Pimpri Chinchwad College of Engineering Nigdi, Pune"
    college_name = models.CharField(max_length=255, default=COLLEGE_NAME)
    department = models.CharField(max_length=100)
    prn_number = models.CharField(max_length=20, unique=True)

    # Document Uploads
    photo = models.FileField(upload_to='scheme_documents/photos/', validators=[validate_image_file])
    application_form = models.FileField(upload_to='scheme_documents/forms/', validators=[validate_pdf_file])
    income_certificate = models.FileField(upload_to='scheme_documents/certificates/', validators=[validate_pdf_file])
    caste_certificate = models.FileField(upload_to='scheme_documents/certificates/', blank=True, null=True, validators=[validate_pdf_file])
    last_year_marksheet = models.FileField(upload_to='scheme_documents/marksheets/', validators=[validate_pdf_file])
    domicile_certificate = models.FileField(upload_to='scheme_documents/certificates/', validators=[validate_pdf_file])
    admission_receipt = models.FileField(upload_to='scheme_documents/receipts/', validators=[validate_pdf_file])
    aadhar_card = models.FileField(upload_to='scheme_documents/identity/', validators=[validate_pdf_file])
    bank_passbook = models.FileField(upload_to='scheme_documents/passbooks/', validators=[validate_pdf_file])
    caste_validity_certificate = models.FileField(upload_to='scheme_documents/certificates/', blank=True, null=True, validators=[validate_pdf_file])

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Correction Required", "Correction Required"),
        ("Completed", "Completed")
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.first_name} {self.middle_name if self.middle_name else ''} {self.last_name} - {self.prn_number}"

class WorkLog(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    hours_worked = models.PositiveIntegerField()
    description = models.TextField()
    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_logs')

    class Meta:
        # Ensure one work log per student per day
        unique_together = ['student', 'date']
        
    def clean(self):
        if self.hours_worked and (self.hours_worked < 1 or self.hours_worked > 8):
            raise ValidationError("Hours worked must be between 1 and 8.")

    def __str__(self):
        return f"{self.student} - ({self.hours_worked} hrs)"

class Department(models.Model):
    """Model to represent college departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Department code (e.g., CSE, IT, MECH)")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_departments')
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class DepartmentIncharge(models.Model):
    """Model to link users with departments as incharges"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'department_encharge'})
    department = models.OneToOneField(Department, on_delete=models.CASCADE, related_name='incharge')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_incharges')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Department Incharge"
        verbose_name_plural = "Department Incharges"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name}"

class StudentDepartmentAssignment(models.Model):
    """Model to assign students to departments"""
    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='assigned_students')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='student_assignments')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Student Department Assignment"
        verbose_name_plural = "Student Department Assignments"
    
    def __str__(self):
        return f"{self.student.get_full_name()} → {self.department.name}"


class PaymentRate(models.Model):
    """Model to manage the single hourly payment rate set by E&L Coordinator"""
    rate_per_hour = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Payment rate per hour in INR"
    )
    set_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'role': 'el_coordinator'},
        related_name='payment_rates_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about this rate change")

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Payment Rate"
        verbose_name_plural = "Payment Rate"

    def save(self, *args, **kwargs):
        """Override save to ensure only one rate exists"""
        # Delete any existing rates before saving this one
        if not self.pk:
            PaymentRate.objects.all().delete()
        super().save(*args, **kwargs)

    @classmethod
    def get_current_rate(cls):
        """Get the current payment rate"""
        return cls.objects.first()

    def __str__(self):
        return f"₹{self.rate_per_hour}/hour (Set on {self.updated_at.strftime('%Y-%m-%d')})"


class PaymentCalculation(models.Model):
    """Model to store calculated payment amounts for students based on verified work hours"""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='payment_calculations'
    )
    department = models.ForeignKey(
        'Department', 
        on_delete=models.CASCADE,
        related_name='payment_calculations'
    )
    calculation_month = models.DateField(help_text="Month for which payment is calculated (stored as first day of month)")
    total_hours = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Total verified hours for the month"
    )
    rate_per_hour = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        help_text="Rate per hour used for calculation"
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Total calculated amount (hours × rate)"
    )
    calculated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payment_calculations_made'
    )
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about the calculation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'calculation_month']
        ordering = ['-calculation_month', 'student__first_name']
        verbose_name = "Payment Calculation"
        verbose_name_plural = "Payment Calculations"

    def clean(self):
        """Validate payment calculation data"""
        if self.total_amount != (self.total_hours * self.rate_per_hour):
            raise ValidationError("Total amount must equal hours × rate per hour.")

    @property
    def month_year_display(self):
        """Return formatted month/year for display"""
        return self.calculation_month.strftime("%B %Y")

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.month_year_display} - ₹{self.total_amount}"

    @classmethod
    def calculate_for_student_month(cls, student, year, month):
        """Calculate payment amount for a specific student and month based on verified work hours"""
        # Get all verified work logs for the student in the specified month
        work_logs = WorkLog.objects.filter(
            student=student,
            date__year=year,
            date__month=month,
            is_verified=True,
            is_rejected=False
        )

        if not work_logs.exists():
            return None

        # Calculate total hours
        total_hours = sum(log.hours_worked for log in work_logs)
        
        # Get current payment rate
        rate = PaymentRate.get_current_rate()
        
        if not rate:
            raise ValidationError("No payment rate has been set. Please contact EL Coordinator.")

        # Get student's department
        try:
            assignment = StudentDepartmentAssignment.objects.get(student=student, is_active=True)
            department = assignment.department
        except StudentDepartmentAssignment.DoesNotExist:
            raise ValidationError(f"Student {student} is not assigned to any department")

        # Calculate total amount
        calculation_date = datetime.date(year, month, 1)
        total_amount = Decimal(str(total_hours)) * rate.rate_per_hour

        # Create or update payment calculation
        calculation, created = cls.objects.get_or_create(
            student=student,
            calculation_month=calculation_date,
            defaults={
                'department': department,
                'total_hours': total_hours,
                'rate_per_hour': rate.rate_per_hour,
                'total_amount': total_amount,
                'calculated_by': None,  # Will be set by the view
            }
        )

        if not created:
            # Update existing calculation
            calculation.total_hours = total_hours
            calculation.rate_per_hour = rate.rate_per_hour
            calculation.total_amount = total_amount
            calculation.department = department
            calculation.save()

        return calculation


class DepartmentPaymentSummary(models.Model):
    """Model to store department-wise payment summaries"""
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='calculation_summaries'
    )
    calculation_month = models.DateField(help_text="Month for which summary is calculated")
    total_students = models.PositiveIntegerField(help_text="Number of students who worked")
    total_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Total verified hours for all students"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total payment amount for the department"
    )
    average_hours_per_student = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Average hours worked per student"
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_summaries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['department', 'calculation_month']
        ordering = ['-calculation_month', 'department__name']
        verbose_name = "Department Calculation Summary"
        verbose_name_plural = "Department Calculation Summaries"

    @property
    def month_year_display(self):
        """Return formatted month/year for display"""
        return self.calculation_month.strftime("%B %Y")

    @classmethod
    def generate_for_department_month(cls, department, year, month):
        """Generate payment summary for a department and month"""
        calculation_date = datetime.date(year, month, 1)
        
        # Get all payment calculations for the department in the specified month
        payment_calculations = PaymentCalculation.objects.filter(
            department=department,
            calculation_month=calculation_date
        )

        if not payment_calculations.exists():
            return None

        # Calculate totals
        total_students = payment_calculations.count()
        total_hours = sum(calc.total_hours for calc in payment_calculations)
        total_amount = sum(calc.total_amount for calc in payment_calculations)
        average_hours = total_hours / total_students if total_students > 0 else 0

        # Create or update summary
        summary, created = cls.objects.get_or_create(
            department=department,
            calculation_month=calculation_date,
            defaults={
                'total_students': total_students,
                'total_hours': total_hours,
                'total_amount': total_amount,
                'average_hours_per_student': average_hours,
            }
        )

        if not created:
            # Update existing summary
            summary.total_students = total_students
            summary.total_hours = total_hours
            summary.total_amount = total_amount
            summary.average_hours_per_student = average_hours
            summary.save()

        return summary

    def __str__(self):
        return f"{self.department.name} - {self.month_year_display} - ₹{self.total_amount}"


class PaymentExport(models.Model):
    """Model to track payment report exports"""
    EXPORT_TYPE_CHOICES = [
        ('student', 'Individual Student'),
        ('department', 'Department Report'),
        ('all_departments', 'All Departments'),
        ('monthly_summary', 'Monthly Summary'),
    ]

    export_type = models.CharField(max_length=20, choices=EXPORT_TYPE_CHOICES)
    export_month = models.DateField(help_text="Month for which export was generated")
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Department (if applicable)"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        limit_choices_to={'role': 'student'},
        help_text="Student (if applicable)"
    )
    file_name = models.CharField(max_length=255, help_text="Generated file name")
    file_path = models.CharField(max_length=500, help_text="Path to the exported file")
    exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payment_exports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Export"
        verbose_name_plural = "Payment Exports"

    @property
    def month_year_display(self):
        """Return formatted month/year for display"""
        return self.export_month.strftime("%B %Y")

    def __str__(self):
        return f"{self.get_export_type_display()} - {self.month_year_display} - {self.file_name}"