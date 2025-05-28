from django.contrib import admin
from .models import (
    Diagnosis, Gejala, Pengguna, Laporandiagnosis, 
    Laporangejala, Detailaturan, Aturangejala
)

# Diagnosis Admin
@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('id_diagnosis', 'nama_diagnosis', 'deskripsi_diagnosis')
    list_filter = ('nama_diagnosis',)
    search_fields = ('nama_diagnosis', 'deskripsi_diagnosis')
    list_per_page = 20
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('nama_diagnosis', 'deskripsi_diagnosis')
        }),
        ('Media dan Solusi', {
            'fields': ('gambar_diagnosis', 'solusi_diagnosis'),
            'classes': ('collapse',)
        }),
    )

# Gejala Admin
@admin.register(Gejala)
class GejalaAdmin(admin.ModelAdmin):
    list_display = ('id_gejala', 'kode_gejala', 'nama_gejala', 'pertanyaan_gejala')
    list_filter = ('kode_gejala',)
    search_fields = ('nama_gejala', 'kode_gejala', 'pertanyaan_gejala')
    list_per_page = 20
    ordering = ('kode_gejala',)

# Pengguna Admin
@admin.register(Pengguna)
class PenggunaAdmin(admin.ModelAdmin):
    list_display = ('id_pengguna', 'nama_pengguna', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('nama_pengguna', 'email')
    list_per_page = 20
    readonly_fields = ('password',)  # Make password read-only for security
    
    fieldsets = (
        ('Informasi Pengguna', {
            'fields': ('nama_pengguna', 'email', 'role')
        }),
        ('Security', {
            'fields': ('password',),
            'classes': ('collapse',),
            'description': 'Password is hashed and cannot be edited directly'
        }),
    )

# Laporan Diagnosis Admin
@admin.register(Laporandiagnosis)
class LaporandiagnosisAdmin(admin.ModelAdmin):
    list_display = ('id_laporandiagnosis', 'get_pengguna_nama', 'get_diagnosis_nama', 
                   'tanggal_diagnosis', 'probabilitas')
    list_filter = ('tanggal_diagnosis', 'id_diagnosis')
    search_fields = ('id_pengguna__nama_pengguna', 'id_diagnosis__nama_diagnosis')
    date_hierarchy = 'tanggal_diagnosis'
    list_per_page = 20
    
    def get_pengguna_nama(self, obj):
        return obj.id_pengguna.nama_pengguna if obj.id_pengguna else 'Anonim'
    get_pengguna_nama.short_description = 'Nama Pengguna'
    get_pengguna_nama.admin_order_field = 'id_pengguna__nama_pengguna'
    
    def get_diagnosis_nama(self, obj):
        return obj.id_diagnosis.nama_diagnosis if obj.id_diagnosis else '-'
    get_diagnosis_nama.short_description = 'Diagnosis'
    get_diagnosis_nama.admin_order_field = 'id_diagnosis__nama_diagnosis'

# Laporan Gejala Admin
@admin.register(Laporangejala)
class LaporangjalaAdmin(admin.ModelAdmin):
    list_display = ('id_laporangejala', 'get_laporan_id', 'get_gejala_nama', 'value')
    list_filter = ('value', 'id_gejala')
    search_fields = ('id_laporandiagnosis__id_laporandiagnosis', 'id_gejala__nama_gejala')
    list_per_page = 50
    
    def get_laporan_id(self, obj):
        return f"Laporan #{obj.id_laporandiagnosis.id_laporandiagnosis}"
    get_laporan_id.short_description = 'ID Laporan'
    
    def get_gejala_nama(self, obj):
        return obj.id_gejala.nama_gejala if obj.id_gejala else '-'
    get_gejala_nama.short_description = 'Nama Gejala'
    get_gejala_nama.admin_order_field = 'id_gejala__nama_gejala'

# Detail Aturan Admin
@admin.register(Detailaturan)
class DetailaturanAdmin(admin.ModelAdmin):
    list_display = ('id_detailaturan', 'get_gejala_nama')
    search_fields = ('id_gejala__nama_gejala', 'id_gejala__kode_gejala')
    list_per_page = 20
    
    def get_gejala_nama(self, obj):
        return obj.id_gejala.nama_gejala if obj.id_gejala else '-'
    get_gejala_nama.short_description = 'Nama Gejala'

# Aturan Gejala Admin
@admin.register(Aturangejala)
class AturangjalaAdmin(admin.ModelAdmin):
    list_display = ('id_aturangejala', 'id_detailaturan')
    search_fields = ('id_aturangejala',)
    list_per_page = 20

# Customize Admin Site
admin.site.site_header = "Sistem Diagnosis Admin"
admin.site.site_title = "Diagnosis Admin"
admin.site.index_title = "Panel Administrasi Sistem Diagnosis"