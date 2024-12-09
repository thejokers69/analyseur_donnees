# /Users/thejoker/Documents/GitHub/analyseur_donnees/analyseur_donnees/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# URL patterns for the project
urlpatterns = [
    # Admin site URL
    path('admin/', admin.site.urls),
    
    # Include URLs from the 'analyse' app
    path('', include('analyse.urls', namespace='analyse')),
    
    # Authentication URLs (login, logout, password management)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Custom login and logout views
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)