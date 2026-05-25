"""
URL configuration for setup project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Rota padrão do painel de administração do Django
    path('admin/', admin.site.urls),
    
    # Rota que encaminha a página inicial para o seu app core
    path('', include('core.urls')), 
]