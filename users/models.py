from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('department_encharge', 'Department Encharge'),
        ('el_coordinator', 'E & L Coordinator'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_registered = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    def __str__(self):
        return f"{self.username} - {self.role}"
    
    def get_full_name(self):
        """Get full name from SchemeApplication if available, otherwise from User model"""
        if self.role == 'student':
            scheme_app = self.get_scheme_application()
            if scheme_app:
                middle_name = f" {scheme_app.middle_name}" if scheme_app.middle_name else ""
                return f"{scheme_app.first_name}{middle_name} {scheme_app.last_name}".strip()
        
        # Fallback to User model's default behavior
        return super().get_full_name() or self.username
    
    def get_display_name(self):
        """Get display name prioritizing SchemeApplication data"""
        return self.get_full_name()
    
    def has_approved_scheme_application(self):
        """Check if the student has an approved scheme application"""
        if self.role != 'student':
            return False
        
        from scheme.models import SchemeApplication
        return SchemeApplication.objects.filter(
            student=self,
            status='Approved'
        ).exists()
    
    def get_scheme_application(self):
        """Get the student's scheme application if it exists"""
        if self.role != 'student':
            return None
            
        from scheme.models import SchemeApplication
        try:
            return SchemeApplication.objects.get(student=self)
        except SchemeApplication.DoesNotExist:
            return None

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    is_registered = models.BooleanField(default=False)  
