from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class DataSet(models.Model):
    STATUS_CHOICES = (
        ('Approved', 'Approved'),
        ('Not yet Approved', 'Not yet Approved'),
    )

    DataSet_Title = models.CharField(max_length=100)
    DataSet_Description = models.TextField()
    DataSet_Poster = models.ForeignKey(User)
    DataSet_Posted = models.DateTimeField(default=datetime.now)
    DataSet_Status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Not yet Approved')
    Data = models.TextField(blank=True)
    jsonifiedData_url = models.CharField(max_length=100, blank=True)
    csvfiedData_url = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.DataSet_Title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    associated_with = models.TextField(blank=True)

    def __str__(self):
        return self.bio

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
