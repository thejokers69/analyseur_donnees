# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/admin.py

from django.contrib import admin
from .models import UploadedFile, AnalysisHistory
from datetime import datetime, timedelta


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "uploaded_at")
    search_fields = ("file",)
    list_filter = ("uploaded_at",)
    ordering = ("-uploaded_at",)


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file_name", "upload_date", "status")
    search_fields = ("file_name", "user__username")
    list_filter = ("upload_date", "status")
    ordering = ("-upload_date",)
    readonly_fields = ("mean", "median", "mode", "variance", "std_dev")

    actions = ["mark_as_completed", "delete_old_analyses"]

    @admin.action(description="Mark as Completed")
    def mark_as_completed(self, request, queryset):
        updated_count = queryset.update(status="completed")
        self.message_user(request, f"{updated_count} analyses marked as completed.")

    @admin.action(description="Delete Obsolete Analyses")
    def delete_old_analyses(self, request, queryset):
        one_year_ago = datetime.now() - timedelta(days=365)
        old_analyses = queryset.filter(upload_date__lt=one_year_ago)
        count = old_analyses.count()
        old_analyses.delete()
        self.message_user(request, f"{count} obsolete analyses have been deleted.")
