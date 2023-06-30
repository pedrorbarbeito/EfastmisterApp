"""efastmister URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import UsersApp.views
import WebScrapingApp.views
from EFastMisterApp import views
from efastmister import settings

urlpatterns = [
    path('', UsersApp.views.loginUser),
    path('admin/', admin.site.urls),
    path('users/', include('UsersApp.urls')),
    path('comunidades/', include('EFastMisterApp.urls')),
    path('scrapeo/', WebScrapingApp.views.webscraping, name='webscraping'),
    path('error403/', views.error_403, name='error403'),
    path('administracion/', views.panel_administracion, name="panel_administracion")

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)