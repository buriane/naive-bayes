from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.homepage, name='homepage'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('tentang/', views.tentang, name='tentang'),
    path('konsultasi/', views.konsultasi, name='konsultasi'),
    path('hasil/', views.hasil, name='hasil'),
    path('riwayat/', views.riwayat, name='riwayat'),
    path('detail-hasil/<int:laporan_id>/', views.detail_hasil, name='detail_hasil'),
    
    # Admin Panel URLs
    path('admin/beranda/', views.admin_beranda, name='admin_beranda'),
    path('admin/riwayat/', views.admin_riwayat, name='admin_riwayat'),
    path('admin/pengguna/', views.admin_pengguna, name='admin_pengguna'),
    path('admin/gejala/', views.admin_gejala, name='admin_gejala'),
    path('admin/penyakit/', views.admin_penyakit, name='admin_penyakit'),
    
    # Testing URL (only available in DEBUG mode)
    path('testing/', views.testing_view, name='testing_view'),
] 