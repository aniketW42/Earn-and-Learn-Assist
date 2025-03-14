from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class StudentSignupForm(UserCreationForm):
    roll_number = forms.CharField(max_length=20, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'roll_number', 'password1', 'password2']
