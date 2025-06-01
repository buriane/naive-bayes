from django.contrib import admin
from django.urls import path
from diagnosis import views as diagnosis_views # Menggunakan alias
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls), # Path Django Admin bawaan

    # --- URL Pengguna Biasa (TIDAK DIUBAH dari versi Anda) ---
    path('', diagnosis_views.homepage, name='homepage'),
    path('login/', diagnosis_views.login, name='login'),
    path('logout/', diagnosis_views.logout, name='logout'),
    path('konsultasi/', diagnosis_views.konsultasi, name='konsultasi'),
    path('register/', diagnosis_views.register, name='register'),
    path('tentang/', diagnosis_views.tentang, name='tentang'),
    path('hasil/', diagnosis_views.hasil, name='hasil'),
    path('riwayat/', diagnosis_views.riwayat, name='riwayat'),
    path('hasil/<int:laporan_id>/', diagnosis_views.detail_hasil, name='detail_hasil'),
    path('testing/', diagnosis_views.testing_view, name='testing'),

    # --- URL Admin Panel Kustom ---
    path('admin-panel/', diagnosis_views.admin_beranda, name='admin_beranda'),
    path('admin-panel/riwayat/', diagnosis_views.admin_riwayat, name='admin_riwayat'),
    path('admin-panel/pengguna/', diagnosis_views.admin_pengguna, name='admin_pengguna'),
    path('admin-panel/gejala/', diagnosis_views.admin_gejala, name='admin_gejala'),
    path('admin-panel/penyakit/', diagnosis_views.admin_penyakit, name='admin_penyakit'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "diagnosis" / "static")
    # Jika ada media files:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)