# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyse/urls.py
from django.urls import path
from . import views
from analyse import views as analyse_views
from django.contrib.auth import views as auth_views

app_name = "analyse"
urlpatterns = [
    path("some-view/", views.some_view, name="some_view"),
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.custom_login, name="login"),
    path("upload/", views.upload_file, name="upload"),
    path("results/<int:file_id>/", views.results, name="results"),
    path("profile/", views.profile, name="profile"),
    path("analysis_history/", views.analysis_history, name="analysis_history"),
    path("download_csv/<int:analysis_id>/", views.download_csv, name="download_csv"),
    path("download_pdf/<int:analysis_id>/", views.download_pdf, name="download_pdf"),
    path("data_table/<int:file_id>/", views.data_table_view, name="data_table"),
    path(
        "correlation_analysis/<int:file_id>/",
        views.correlation_analysis,
        name="correlation_analysis",
    ),
    path(
        "visualization/<int:file_id>/",
        views.visualization_options,
        name="visualization_options",
    ),
    path(
        "customize_analysis/<int:file_id>/",
        views.customize_analysis,
        name="customize_analysis",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "visualization_options/<int:file_id>/",
        views.visualization_options,
        name="visualization_options",
    ),
]
