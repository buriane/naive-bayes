"""
URL configuration for liver_disease project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from diagnosis import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),  # <- Ini halaman utama
    path('login/', views.login, name='login'),  # <- Ini halaman login
    path('konsultasi/', views.konsultasi, name='konsultasi'),  # <- Ini halaman konsultasi
    path('register/', views.register, name='register'),  # <- Ini halaman register
    path ('tentang/', views.tentang, name='tentang'),  # <- Ini halaman tentang
    path ('hasil/', views.hasil, name='hasil'),  # <- Ini halaman hasil
    path ('riwayat/', views.riwayat, name='riwayat'),  # <- Ini halaman riwayat
]