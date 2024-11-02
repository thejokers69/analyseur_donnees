# ANALYSEUR_DONNEES/analyse/models.py
from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
# Upload files
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# Analyse History and Results
class AnalysisHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    mean = models.FloatField(null=True, blank=True)
    median = models.FloatField(null=True, blank=True)
    mode = models.CharField(max_length=255, null=True, blank=True)
    variance = models.FloatField(null=True, blank=True)
    std_dev = models.FloatField(null=True, blank=True)
    data_range = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    histograms = JSONField(null=True, blank=True)

    def __str__(self):
        return f"Analysis of {self.file_name} by {self.user.username}"