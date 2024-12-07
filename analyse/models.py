# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/models.py
from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
from django.utils.translation import gettext_lazy as _


# Upload files
class UploadedFile(models.Model):
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


# Analyse History and Results
class AnalysisHistory(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="analysis_histories"
    )
    uploaded_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analyses",
    )
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    mean = models.FloatField(null=True, blank=True)
    median = models.FloatField(null=True, blank=True)
    mode = models.CharField(max_length=255, null=True, blank=True)
    variance = models.FloatField(null=True, blank=True)
    std_dev = models.FloatField(null=True, blank=True)
    range_values = models.CharField(max_length=255, null=True, blank=True)
    data_range = models.CharField(max_length=255, null=True, blank=True)
    histograms = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = _("Analysis History")
        verbose_name_plural = _("Analysis Histories")
        ordering = ["-upload_date"]
        indexes = [
            models.Index(fields=["upload_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Analysis of {self.file_name} by {self.user.username}"
