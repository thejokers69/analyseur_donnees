# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "analyse"

urlpatterns = [
    # Accueil et Authentification
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.custom_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),

    # Gestion des fichiers
    path("upload/", views.upload_file, name="upload"),
    path("delete_file/<int:file_id>/", views.delete_file, name="delete_file"),

    # Résultats et analyses
    path("results/<int:file_id>/", views.results, name="results"),
    path("analysis/history/", views.analysis_history, name="analysis_history"),
    path("analysis/customize/<int:file_id>/", views.customize_analysis, name="customize_analysis"),
    path("analysis/data_table/<int:file_id>/", views.data_table_view, name="data_table"),
    path("analysis/missing_values/<int:file_id>/", views.missing_values_analysis, name="missing_values"),
    path("analysis/linear_regression/<int:file_id>/", views.linear_regression_analysis, name="linear_regression_analysis"),
    path("analysis/delete/<int:analysis_id>/", views.delete_analysis, name="delete_analysis"),

    # Visualisations
    path("visualizations/<int:file_id>/", views.visualization_options, name="visualization_options"),
    path("visualization/", views.visualization_view, name="visualization"),
    path("analysis/interactive_visualization/<int:file_id>/", views.interactive_visualization, name="interactive_visualization"),

    # Exportations
    path("export/csv/<int:file_id>/", views.export_csv_view, name="export_csv"),
    path("export/pdf/<int:file_id>/", views.export_pdf_view, name="export_pdf"),
    path(
    "visualization/<int:file_id>/",
    views.correlation_and_regression_visualization,
    name="correlation_regression_visualization",
),
    path('loi_probability/', views.loi_probability, name='loi_probability'),
]