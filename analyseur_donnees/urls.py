# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyseur_donnees/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path(
#         "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
#     ),
#     path("logout/", auth_views.LogoutView.as_view(), name="logout"),
#     path("", include("analyse.urls", namespace="analyse")),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# analyseur_donnees/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analyse.urls', namespace='analyse')),  # Inclure avec namespace
    path('accounts/', include('django.contrib.auth.urls')),  # Ajouter les URLs d'authentification
]