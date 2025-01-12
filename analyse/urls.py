# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "analyse"
urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.custom_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("upload/", views.upload_file, name="upload"),
    path("results/<int:file_id>/", views.results, name="results"),
    path("profile/", views.profile, name="profile"),
    path("analysis/history/", views.analysis_history, name="analysis_history"),
    path(
        "analysis/download_csv/<int:analysis_id>/",
        views.download_csv,
        name="download_csv",
    ),
    path(
        "analysis/download_pdf/<int:analysis_id>/",
        views.download_pdf,
        name="download_pdf",
    ),
    path(
        "analysis/data_table/<int:file_id>/", views.data_table_view, name="data_table"
    ),
    path(
        "analysis/correlation/<int:file_id>/",
        views.correlation_analysis,
        name="correlation_analysis",
    ),
    path(
        "analysis/customize/<int:file_id>/",
        views.customize_analysis,
        name="customize_analysis",
    ),
    path(
        "visualizations/<int:file_id>/",
        views.visualization_options,
        name="visualization_options",
    ),
    path(
        "analysis/delete/<int:analysis_id>/",
        views.delete_analysis,
        name="delete_analysis",
    ),
    path("delete_file/<int:file_id>/", views.delete_file, name="delete_file"),
    path("correlation_analysis/", views.correlation_view, name="correlation_view"),
    path("visualization/", views.visualization_view, name="visualization"),
    path("export/csv/", views.export_csv_view, name="export_csv"),
    path("export/pdf/", views.export_pdf_view, name="export_pdf"),
    path("correlation/", views.correlation_view, name="correlation"),
    path("visualization/", views.visualization_view, name="visualization"),
    path("export/csv/", views.export_csv_view, name="export_csv"),
    path("export/pdf/", views.export_pdf_view, name="export_pdf"),
]