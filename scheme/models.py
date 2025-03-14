from django.db import models
from django.conf import settings

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
    photo = models.FileField(upload_to='scheme_documents/photos/')
    application_form = models.FileField(upload_to='scheme_documents/forms/')
    income_certificate = models.FileField(upload_to='scheme_documents/certificates/')
    caste_certificate = models.FileField(upload_to='scheme_documents/certificates/', blank=True, null=True)
    last_year_marksheet = models.FileField(upload_to='scheme_documents/marksheets/')
    domicile_certificate = models.FileField(upload_to='scheme_documents/certificates/')
    admission_receipt = models.FileField(upload_to='scheme_documents/receipts/')
    aadhar_card = models.FileField(upload_to='scheme_documents/identity/')
    bank_passbook = models.FileField(upload_to='scheme_documents/passbooks/')
    caste_validity_certificate = models.FileField(upload_to='scheme_documents/certificates/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')

    def __str__(self):
        return f"{self.first_name} {self.middle_name if self.middle_name else ''} {self.last_name} - {self.prn_number}"

class WorkLog(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    hours_worked = models.PositiveIntegerField()
    description = models.TextField()
    is_verified = models.BooleanField(default=False)  # Verified by Department Encharge

    def __str__(self):
        return f"{self.student} - ({self.hours_worked} hrs)"