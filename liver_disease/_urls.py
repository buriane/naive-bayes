"""
URL configuration for liver_disease project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/XX.X/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
# Asumsikan nama file views Anda adalah views.py, bukan _views.py
# Jika memang _views.py, ganti kembali ke "from diagnosis import _views as diagnosis_views"
from diagnosis import views as diagnosis_views # Memberi alias agar lebih jelas
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # Halaman admin Django bawaan

    # URL untuk aplikasi diagnosis
    path('', diagnosis_views.homepage, name='homepage'),  # Halaman utama
    path('login/', diagnosis_views.login, name='login'),
    path('logout/', diagnosis_views.logout, name='logout'),
    path('register/', diagnosis_views.register, name='register'),
    path('konsultasi/', diagnosis_views.konsultasi, name='konsultasi'),
    path('hasil/', diagnosis_views.hasil, name='hasil'),
    path('riwayat/', diagnosis_views.riwayat, name='riwayat'),
    path('riwayat/hasil/<int:laporan_id>/', diagnosis_views.detail_hasil, name='detail_hasil'), # Path yang lebih deskriptif
    path('tentang/', diagnosis_views.tentang, name='tentang'),

    # URL untuk admin panel custom (jika ada dan didefinisikan di views.py)
    # Pastikan nama view 'admin_panel' ada di diagnosis_views
    path('panel-admin/', diagnosis_views.admin_panel, name='admin_panel'), # Tambahkan ini

    # URL untuk testing (jika masih digunakan)
    path('testing/', diagnosis_views.testing_view, name='testing'),
]

# Konfigurasi untuk menyajikan file statis selama pengembangan
if settings.DEBUG:
    # Ini akan menyajikan file dari direktori static di dalam aplikasi 'diagnosis'
    # Pastikan BASE_DIR sudah benar dan struktur direktori static/diagnosis/static ada
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "diagnosis" / "static")
    # Jika Anda juga memiliki direktori media untuk file yang diunggah pengguna:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)