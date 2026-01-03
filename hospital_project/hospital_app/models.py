from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


# Create your models here.
class CustomUser(AbstractUser):
    user_type=models.IntegerField(default=1)

class Department(models.Model):
    Dept_name = models.CharField(max_length=100)

class Doctor(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    dep = models.ForeignKey(Department,on_delete=models.CASCADE,null=True)
    Phone_number = models.CharField(max_length=11)
    Address = models.CharField(max_length=100,null=True)
    Profile = models.ImageField(upload_to='images/', null=True)
    # 0 = pending
    # 1 = approved
    # 2 = rejected
    status = models.IntegerField(default=0)

class Patient(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    p_id = models.IntegerField()
    Phone_number = models.CharField(max_length=11)
    Address = models.CharField(max_length=100,null=True)
    age = models.IntegerField()

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    date = models.DateField(default=date.today)
    time = models.CharField(max_length=50, null=True)
    Description = models.CharField(max_length=100, null = True)

    # Status:
    # 0 = Pending (waiting for doctor approval)
    # 1 = Approved
    # 2 = Disapproved
    # 3 = Consulted (doctor completed consultation)
    # 4 = Not Consulted (patient missed / cancelled)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
