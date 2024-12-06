# ANALYSEUR_DONNEES/analyse/admin.py

from django.contrib import admin
from .models import UploadedFile, AnalysisHistory

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at')  
    search_fields = ('file',)  
    list_filter = ('uploaded_at',)
    ordering = ('-uploaded_at',)


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file_name', 'upload_date', 'status')
    search_fields = ('file_name', 'user__username')
    list_filter = ('upload_date', 'status')
    ordering = ('-upload_date',)
    readonly_fields = ('mean', 'median', 'mode', 'variance', 'std_dev') 

    actions = ['mark_as_completed', 'delete_old_analyses']

    @admin.action(description="Marquer comme terminées")
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')

    @admin.action(description="Supprimer les analyses obsolètes")
    def delete_old_analyses(self, request, queryset):
        from datetime import datetime, timedelta
        one_year_ago = datetime.now() - timedelta(days=365)
        old_analyses = queryset.filter(upload_date__lt=one_year_ago)
        count = old_analyses.count()
        old_analyses.delete()
        self.message_user(request, f"{count} analyses obsolètes supprimées.")