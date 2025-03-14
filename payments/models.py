from django.db import models
from django.conf import settings
# Create your models here.
class Salary(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_hours = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - ₹{self.amount} ({'Paid' if self.is_paid else 'Pending'})"