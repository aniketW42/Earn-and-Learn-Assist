from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_file_size(file):
    """ Limit file size to 2 MB (2 * 1024 * 1024 bytes) """
    max_size = 2 * 1024 * 1024 
    if file.size > max_size:
        raise ValidationError(f"File size should be less than {max_size / (1024 * 1024):.2f} MB")

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
    photo = models.FileField(upload_to='scheme_documents/photos/', validators=[validate_file_size])
    application_form = models.FileField(upload_to='scheme_documents/forms/', validators=[validate_file_size])
    income_certificate = models.FileField(upload_to='scheme_documents/certificates/', validators=[validate_file_size])
    caste_certificate = models.FileField(upload_to='scheme_documents/certificates/', blank=True, null=True, validators=[validate_file_size])
    last_year_marksheet = models.FileField(upload_to='scheme_documents/marksheets/', validators=[validate_file_size])
    domicile_certificate = models.FileField(upload_to='scheme_documents/certificates/', validators=[validate_file_size])
    admission_receipt = models.FileField(upload_to='scheme_documents/receipts/', validators=[validate_file_size])
    aadhar_card = models.FileField(upload_to='scheme_documents/identity/', validators=[validate_file_size])
    bank_passbook = models.FileField(upload_to='scheme_documents/passbooks/', validators=[validate_file_size])
    caste_validity_certificate = models.FileField(upload_to='scheme_documents/certificates/', blank=True, null=True, validators=[validate_file_size])

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

    def __str__(self):
        return f"{self.student} - ({self.hours_worked} hrs)"