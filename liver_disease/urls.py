"""
URL configuration for liver_disease project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
from diagnosis import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),  # Halaman utama
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('konsultasi/', views.konsultasi, name='konsultasi'),
    path('register/', views.register, name='register'),
    path('tentang/', views.tentang, name='tentang'),
    path('hasil/', views.hasil, name='hasil'),
    path('riwayat/', views.riwayat, name='riwayat'),
    path('testing/', views.testing_view, name='testing'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "diagnosis" / "static")
