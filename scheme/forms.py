from django import forms
from .models import SchemeApplication
from .models import WorkLog

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



class WorkLogForm(forms.ModelForm):
    class Meta:
        model = WorkLog
        fields = ["hours_worked", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "hours_worked": forms.NumberInput(attrs={"class": "form-control"}),
        }
