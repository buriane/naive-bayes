from django.shortcuts import render, redirect, get_object_or_404
from .models import Diagnosis, Gejala, Laporandiagnosis, Laporangejala, Pengguna
from django.db import connection
from django.db.models import Q
from django.db.models import Count
from datetime import date
import datetime
import math
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from django.utils import timezone
from django.conf import settings

# Custom decorator untuk login_required
def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, 'Silakan login terlebih dahulu.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# --- Views Pengguna Biasa ---
def homepage(request):
    return render(request, 'diagnosis/index.html')

def login(request):
    # Check if user is already logged in
    if request.session.get('user_id'):
        user_role = request.session.get('user_role')
        if user_role in ['admin', 'pakar']:
            return redirect('admin_beranda')
        else:
            return redirect('homepage')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email dan password harus diisi.')
            return render(request, 'diagnosis/login.html')

        try:
            user = Pengguna.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id_pengguna
                request.session['user_name'] = user.nama_pengguna
                request.session['user_email'] = user.email
                request.session['user_role'] = user.role

                if user.role in ['admin', 'pakar']:
                    return redirect('admin_beranda')
                else:
                    return redirect('homepage')
            else:
                messages.error(request, 'Email atau password tidak valid.')
        except Pengguna.DoesNotExist:
            messages.error(request, 'Email atau password tidak valid.')
        except Exception as e:
            messages.error(request, 'Terjadi kesalahan internal. Silakan coba lagi.')
        return render(request, 'diagnosis/login.html')
    return render(request, 'diagnosis/login.html')

def logout(request):
    request.session.flush()
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('login')

def konsultasi(request):
    gejala_list = Gejala.objects.all().order_by('kode_gejala')
    return render(request, 'diagnosis/konsultasi.html', {
        'gejala_list': gejala_list,
    })

def register(request):
    # Check if user is already logged in
    if request.session.get('user_id'):
        user_role = request.session.get('user_role')
        if user_role in ['admin', 'pakar']:
            return redirect('admin_beranda')
        else:
            return redirect('homepage')
    
    if request.method == 'POST':
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        terms = request.POST.get('terms')
        form_input = request.POST

        if not all([first_name, last_name, email, password, confirm_password]):
            messages.error(request, 'Semua field harus diisi.')
            return render(request, 'diagnosis/register.html', {'input': form_input})

        if password != confirm_password:
            messages.error(request, 'Password dan konfirmasi password tidak cocok.')
            return render(request, 'diagnosis/register.html', {'input': form_input})

        if not terms:
            messages.error(request, 'Anda harus menyetujui syarat dan ketentuan.')
            return render(request, 'diagnosis/register.html', {'input': form_input})

        if Pengguna.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar. Silakan gunakan email lain.')
            return render(request, 'diagnosis/register.html', {'input': form_input})

        try:
            last_user = Pengguna.objects.order_by('-id_pengguna').first()
            user_id = (last_user.id_pengguna + 1) if last_user else 1
            full_name = f"{first_name} {last_name}"
            hashed_password = make_password(password)

            new_user = Pengguna(
                id_pengguna=user_id,
                nama_pengguna=full_name,
                email=email,
                password=hashed_password,
                role='user'
            )
            new_user.save()
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat registrasi: {str(e)}')
            return render(request, 'diagnosis/register.html', {'input': form_input})
    return render(request, 'diagnosis/register.html')

def tentang(request):
    return render(request, 'diagnosis/tentang.html')

def hasil(request):
    if request.method != 'POST':
        return redirect('konsultasi')

    # Get selected symptoms from form
    gejala_ids = request.POST.getlist('gejala')
    if not gejala_ids:
        return redirect('konsultasi')

    # Convert to integers
    gejala_ids = [int(gid) for gid in gejala_ids]

    # Get all diagnoses and gejala
    all_diagnoses = list(Diagnosis.objects.all())
    all_gejala = list(Gejala.objects.all())

    # Define knowledge base rules (sesuai dengan nc values dalam dokumentasi)
    knowledge_base = {
        'Hepatitis A': [1, 3, 4, 5, 7],    # G01, G03, G04, G05, G07
        'Hepatitis B': [3, 6, 7, 8, 9],    # G03, G06, G07, G08, G09
        'Hepatitis C': [1, 2, 3, 10],      # G01, G02, G03, G10
        'Sirosis Hati': [7, 11, 12],       # G07, G11, G12
        'Kolestasis': [8, 9, 13],          # G08, G09, G13
    }

    # Calculate rule-based scores (tetap untuk hybrid approach)
    rule_scores = {}
    for diagnosis in all_diagnoses:
        diagnosis_name = diagnosis.nama_diagnosis
        if diagnosis_name in knowledge_base:
            required_symptoms = knowledge_base[diagnosis_name]
            matched_symptoms = len(set(gejala_ids) & set(required_symptoms))
            total_required = len(required_symptoms)
            
            rule_confidence = (matched_symptoms / total_required) * 100 if total_required > 0 else 0
            rule_scores[diagnosis.id_diagnosis] = rule_confidence
        else:
            rule_scores[diagnosis.id_diagnosis] = 0

    # --- NAIVE BAYES CALCULATION SESUAI DOKUMENTASI ---
    
    # Konstanta sesuai dokumentasi
    N_VALUE_FOR_EACH_CLASS = 1  # n = jumlah record pada data learning untuk setiap kelas
    TOTAL_CLASSES = 5           # banyaknya jenis class penyakit
    P_VALUE = 1 / TOTAL_CLASSES  # p = 1/5 = 0,2 (bukan 0,1667 seperti sebelumnya)
    TOTAL_SYMPTOMS_M = 13       # m = jumlah parameter/gejala (sesuai dokumentasi: 13)

    # 1. Menentukan nilai nc untuk setiap kelas
    # nc sudah ditentukan melalui knowledge_base

    # 2. Melakukan perhitungan nilai P(ai|vj) serta perhitungan nilai P(vj)
    conditional_probs = {}
    
    # Prior Probability P(vj) - uniform untuk semua penyakit
    prior_probability = 1 / TOTAL_CLASSES  # 0,2 untuk setiap penyakit

    for diagnosis in all_diagnoses:
        conditional_probs[diagnosis.id_diagnosis] = {}
        diagnosis_name = diagnosis.nama_diagnosis
        
        for gejala in all_gejala:
            # Menentukan nc: 1 jika gejala ada dalam knowledge_base untuk penyakit ini, 0 jika tidak
            if diagnosis_name in knowledge_base and gejala.id_gejala in knowledge_base[diagnosis_name]:
                nc = 1
            else:
                nc = 0
            
            # Rumus P(ai|vj) = (nc + m * p) / (n + m)
            prob_symptom_given_disease = (nc + (TOTAL_SYMPTOMS_M * P_VALUE)) / \
                                         (N_VALUE_FOR_EACH_CLASS + TOTAL_SYMPTOMS_M)
            
            conditional_probs[diagnosis.id_diagnosis][gejala.id_gejala] = prob_symptom_given_disease

    # 3. Melakukan perhitungan P(ai|vj) x P(vj) untuk tiap kelas v
    nb_results = []
    
    for diagnosis in all_diagnoses:
        # Mulai dengan P(vj) - prior probability
        posterior_probability = prior_probability
        
        # Kalikan dengan P(ai|vj) untuk SEMUA gejala yang dipilih pasien
        # Sesuai contoh dalam dokumentasi yang mengalikan semua gejala yang ada
        for patient_gejala_id in gejala_ids:
            prob = conditional_probs[diagnosis.id_diagnosis].get(patient_gejala_id)
            if prob is not None:
                posterior_probability *= prob
        
        nb_results.append((diagnosis, posterior_probability))

    # 4. Menentukan nilai perkalian terbesar dari klasifikasi v
    # Sort berdasarkan probabilitas tertinggi
    nb_results.sort(key=lambda x: x[1], reverse=True)
    
    # Konversi ke persentase untuk tampilan (sesuai tabel dalam dokumentasi)
    nb_probabilities = {}
    for diagnosis, prob in nb_results:
        # Kalikan dengan 100 untuk mendapatkan persentase kecil seperti dalam dokumentasi
        nb_probabilities[diagnosis.id_diagnosis] = prob * 100

    # PERBAIKAN: Gunakan HANYA Naive Bayes untuk hasil akhir (bukan hybrid)
    # Karena dokumentasi menunjukkan hasil akhir menggunakan pure Naive Bayes
    
    # Sort berdasarkan Naive Bayes probability saja
    final_results = []
    for diagnosis in all_diagnoses:
        nb_score = nb_probabilities.get(diagnosis.id_diagnosis, 0)
        rule_score = rule_scores.get(diagnosis.id_diagnosis, 0)  # Tetap hitung untuk referensi
        
        # Gunakan nb_score sebagai final probability (bukan kombinasi)
        final_results.append((diagnosis, nb_score, rule_score, nb_score))

    # Sort by Naive Bayes score (highest first)
    final_results.sort(key=lambda x: x[1], reverse=True)

    # Get the top diagnosis
    top_diagnosis, final_probability, rule_prob, nb_prob = final_results[0]

    # TAMBAHAN: Siapkan data semua probabilitas untuk ditampilkan
    all_probabilities = []
    for diagnosis, nb_score, rule_score, final_score in final_results:
        all_probabilities.append({
            'diagnosis': diagnosis,
            'probability': nb_score
        })

    # Store the diagnosis result
    user_id = request.session.get('user_id', None)
    
    # Generate auto-increment ID for the report
    last_report = Laporandiagnosis.objects.order_by('-id_laporandiagnosis').first()
    if last_report:
        new_report_id = last_report.id_laporandiagnosis + 1
    else:
        new_report_id = 1
    
    # Create a new diagnosis report
    new_report = Laporandiagnosis(
        id_laporandiagnosis=new_report_id,
        id_pengguna_id=user_id,
        id_diagnosis=top_diagnosis,
        tanggal_diagnosis=date.today(),
        probabilitas=final_probability
    )
    new_report.save()

    # Store all the symptoms
    for gejala in all_gejala:
        last_gejala_report = Laporangejala.objects.order_by('-id_laporangejala').first()
        if last_gejala_report:
            new_gejala_id = last_gejala_report.id_laporangejala + 1
        else:
            new_gejala_id = 1
        
        value = 1 if gejala.id_gejala in gejala_ids else 0
        laporangejala = Laporangejala(
            id_laporangejala=new_gejala_id,
            id_laporandiagnosis=new_report,
            id_gejala_id=gejala.id_gejala,
            value=value
        )
        laporangejala.save()

    # Get selected symptoms
    selected_gejala = Gejala.objects.filter(id_gejala__in=gejala_ids)

    return render(request, 'diagnosis/hasil.html', {
        'diagnosis': top_diagnosis,
        'probability': final_probability,
        'selected_gejala': selected_gejala,
        'date': date.today(),
        'all_probabilities': all_probabilities,
    })

@login_required_custom
def riwayat(request):
    # Get current logged-in user ID from session
    user_id = request.session.get('user_id')
    
    # Retrieve diagnosis history for the current user, ordered by date (newest first)
    riwayat_diagnosis = Laporandiagnosis.objects.filter(
        id_pengguna=user_id
    ).select_related('id_diagnosis').order_by('-tanggal_diagnosis')
    
    # Calculate statistics
    total_count = riwayat_diagnosis.count()
    high_risk = riwayat_diagnosis.filter(probabilitas__gte=70).count()
    medium_risk = riwayat_diagnosis.filter(probabilitas__gte=40, probabilitas__lt=70).count()
    low_risk = riwayat_diagnosis.filter(probabilitas__lt=40).count()
    
    return render(request, 'diagnosis/riwayat.html', {
        'riwayat_diagnosis': riwayat_diagnosis,
        'total_count': total_count,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
    })
    
def detail_hasil(request, laporan_id):
    try:
        laporan_obj = Laporandiagnosis.objects.select_related('id_diagnosis', 'id_pengguna').get(id_laporandiagnosis=laporan_id)
        
        user_id_session = request.session.get('user_id')
        user_role_session = request.session.get('user_role')
        
        if laporan_obj.id_pengguna_id != user_id_session and user_role_session != 'admin':
             messages.error(request, 'Anda tidak diizinkan untuk melihat detail laporan ini.')
             return redirect('riwayat' if user_role_session != 'admin' else 'homepage')

        # Get gejala yang dipilih pada laporan ini
        gejala_reports_for_laporan = Laporangejala.objects.filter(
            id_laporandiagnosis=laporan_obj, value=1 
        ).select_related('id_gejala') 
        
        selected_gejala_from_report_objects = [gr.id_gejala for gr in gejala_reports_for_laporan]
        
        # TAMBAHAN: Hitung ulang probabilitas semua penyakit berdasarkan gejala yang tersimpan
        gejala_ids = [gr.id_gejala.id_gejala for gr in gejala_reports_for_laporan]
        
        if gejala_ids:  # Jika ada gejala yang tersimpan
            # Get all diagnoses and gejala (sama seperti di fungsi hasil)
            all_diagnoses = list(Diagnosis.objects.all())
            all_gejala = list(Gejala.objects.all())

            # Define knowledge base rules (sama seperti di fungsi hasil)
            knowledge_base = {
                'Hepatitis A': [1, 3, 4, 5, 7],    # G01, G03, G04, G05, G07
                'Hepatitis B': [3, 6, 7, 8, 9],    # G03, G06, G07, G08, G09
                'Hepatitis C': [1, 2, 3, 10],      # G01, G02, G03, G10
                'Sirosis Hati': [7, 11, 12],       # G07, G11, G12
                'Kolestasis': [8, 9, 13],          # G08, G09, G13
            }

            # --- NAIVE BAYES CALCULATION (sama seperti di fungsi hasil) ---
            
            # Konstanta sesuai dokumentasi
            N_VALUE_FOR_EACH_CLASS = 1
            TOTAL_CLASSES = 5
            P_VALUE = 1 / TOTAL_CLASSES
            TOTAL_SYMPTOMS_M = 13

            # Perhitungan conditional probabilities
            conditional_probs = {}
            prior_probability = 1 / TOTAL_CLASSES

            for diagnosis in all_diagnoses:
                conditional_probs[diagnosis.id_diagnosis] = {}
                diagnosis_name = diagnosis.nama_diagnosis
                
                for gejala in all_gejala:
                    if diagnosis_name in knowledge_base and gejala.id_gejala in knowledge_base[diagnosis_name]:
                        nc = 1
                    else:
                        nc = 0
                    
                    prob_symptom_given_disease = (nc + (TOTAL_SYMPTOMS_M * P_VALUE)) / \
                                                 (N_VALUE_FOR_EACH_CLASS + TOTAL_SYMPTOMS_M)
                    
                    conditional_probs[diagnosis.id_diagnosis][gejala.id_gejala] = prob_symptom_given_disease

            # Perhitungan probabilitas untuk setiap penyakit
            nb_results = []
            
            for diagnosis in all_diagnoses:
                posterior_probability = prior_probability
                
                for patient_gejala_id in gejala_ids:
                    prob = conditional_probs[diagnosis.id_diagnosis].get(patient_gejala_id)
                    if prob is not None:
                        posterior_probability *= prob
                
                nb_results.append((diagnosis, posterior_probability))

            # Sort berdasarkan probabilitas tertinggi
            nb_results.sort(key=lambda x: x[1], reverse=True)
            
            # Konversi ke persentase
            nb_probabilities = {}
            for diagnosis, prob in nb_results:
                nb_probabilities[diagnosis.id_diagnosis] = prob * 100

            # Siapkan data semua probabilitas untuk ditampilkan
            all_probabilities = []
            for diagnosis, prob in nb_results:
                all_probabilities.append({
                    'diagnosis': diagnosis,
                    'probability': prob * 100
                })
        else:
            # Jika tidak ada gejala, buat list kosong
            all_probabilities = []
        
        return render(request, 'diagnosis/hasil.html', {
            'diagnosis': laporan_obj.id_diagnosis,
            'probability': laporan_obj.probabilitas,
            'selected_gejala': selected_gejala_from_report_objects,
            'date': laporan_obj.tanggal_diagnosis,
            'laporan_pengguna': laporan_obj.id_pengguna,
            'is_detail_view': True,
            'laporan_id': laporan_id,
            'page_title': f"Detail Laporan #{laporan_id}",
            'all_probabilities': all_probabilities,
        })
    except Laporandiagnosis.DoesNotExist:
        messages.error(request, 'Laporan diagnosis tidak ditemukan.')
        return redirect('riwayat' if request.session.get('user_role') != 'admin' else 'admin_riwayat')
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('riwayat' if request.session.get('user_role') != 'admin' else 'admin_riwayat')
    
def testing_view(request):
    if not settings.DEBUG:
        return redirect('homepage')
    diagnosis_list = Diagnosis.objects.all()
    gejala_list = Gejala.objects.all()
    return render(request, 'diagnosis/testing.html', {
        'diagnosis_list': diagnosis_list,
        'gejala_list': gejala_list,
    })

# --- Role-based Access Control Decorators ---
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.session.get('user_id'):
                messages.error(request, 'Silakan login terlebih dahulu.')
                return redirect('login')
            
            user_role = request.session.get('user_role')
            if user_role not in allowed_roles:
                messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
                return redirect('admin_beranda')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# --- Admin Panel Views ---

@login_required_custom
@role_required(['admin', 'pakar'])
def admin_beranda(request):
    # Get diagnosis distribution data
    diagnosis_stats = Laporandiagnosis.objects.values(
        'id_diagnosis__nama_diagnosis'
    ).annotate(
        count=Count('id_diagnosis')
    ).order_by('-count')[:5]  # Top 5 diagnoses

    # Get recent diagnosis trends (last 7 days)
    today = timezone.now().date()
    seven_days_ago = today - timezone.timedelta(days=6)
    
    daily_diagnoses = Laporandiagnosis.objects.filter(
        tanggal_diagnosis__gte=seven_days_ago
    ).values(
        'tanggal_diagnosis'
    ).annotate(
        count=Count('id_laporandiagnosis')
    ).order_by('tanggal_diagnosis')

    # Fill in missing dates with zero counts
    date_counts = {str(date): 0 for date in [seven_days_ago + timezone.timedelta(days=x) for x in range(7)]}
    for item in daily_diagnoses:
        date_counts[str(item['tanggal_diagnosis'])] = item['count']

    # Get user statistics
    total_users = Pengguna.objects.count()
    total_diagnoses = Laporandiagnosis.objects.count()
    total_gejala = Gejala.objects.count()
    total_penyakit = Diagnosis.objects.count()

    # Get recent diagnoses
    recent_diagnoses = Laporandiagnosis.objects.select_related(
        'id_pengguna', 'id_diagnosis'
    ).order_by('-tanggal_diagnosis')[:5]

    context = {
        'page_title': 'Beranda Admin',
        'active_section': 'beranda',
        'diagnosis_stats': list(diagnosis_stats),
        'daily_diagnoses': {
            'dates': list(date_counts.keys()),
            'counts': list(date_counts.values())
        },
        'stats': {
            'total_users': total_users,
            'total_diagnoses': total_diagnoses,
            'total_gejala': total_gejala,
            'total_penyakit': total_penyakit
        },
        'recent_diagnoses': recent_diagnoses
    }
    return render(request, 'diagnosis/admin_base.html', context)

@login_required_custom
@role_required(['admin'])
def admin_riwayat(request):
    if request.method == 'POST' and request.POST.get('action') == 'delete':
        try:
            laporan_id = request.POST.get('laporan_id')
            laporan = Laporandiagnosis.objects.get(id_laporandiagnosis=laporan_id)
            
            # Delete related gejala reports first
            Laporangejala.objects.filter(id_laporandiagnosis=laporan).delete()
            # Then delete the diagnosis report
            laporan.delete()
            
            messages.success(request, 'Riwayat diagnosis berhasil dihapus.')
        except Laporandiagnosis.DoesNotExist:
            messages.error(request, 'Riwayat diagnosis tidak ditemukan.')
        except Exception as e:
            messages.error(request, f'Gagal menghapus riwayat diagnosis: {str(e)}')
        return redirect('admin_riwayat')

    riwayat_list = Laporandiagnosis.objects.all().select_related(
        'id_diagnosis', 'id_pengguna'
    ).order_by('-tanggal_diagnosis')
    
    paginator = Paginator(riwayat_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Riwayat Diagnosis',
        'active_section': 'riwayat',
        'page_obj': page_obj,
    }
    return render(request, 'diagnosis/admin_base.html', context)

@login_required_custom
@role_required(['admin'])
def admin_pengguna(request):
    pengguna_list = Pengguna.objects.all().order_by('-id_pengguna')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                nama = request.POST.get('nama_pengguna')
                email = request.POST.get('email')
                password = request.POST.get('password')
                role = request.POST.get('role')
                
                if Pengguna.objects.filter(email=email).exists():
                    messages.error(request, 'Email sudah terdaftar.')
                else:
                    new_user = Pengguna(
                        nama_pengguna=nama,
                        email=email,
                        password=make_password(password),
                        role=role
                    )
                    new_user.save()
                    messages.success(request, 'Pengguna berhasil ditambahkan.')
            except Exception as e:
                messages.error(request, f'Gagal menambahkan pengguna: {str(e)}')
                
        elif action == 'update':
            try:
                user_id = request.POST.get('id_pengguna')
                user = Pengguna.objects.get(id_pengguna=user_id)
                
                user.nama_pengguna = request.POST.get('nama_pengguna')
                user.email = request.POST.get('email')
                if request.POST.get('password'):
                    user.password = make_password(request.POST.get('password'))
                user.role = request.POST.get('role')
                
                user.save()
                messages.success(request, 'Data pengguna berhasil diperbarui.')
            except Pengguna.DoesNotExist:
                messages.error(request, 'Pengguna tidak ditemukan.')
            except Exception as e:
                messages.error(request, f'Gagal memperbarui pengguna: {str(e)}')
                
        elif action == 'delete':
            try:
                user_id = request.POST.get('id_pengguna')
                user = Pengguna.objects.get(id_pengguna=user_id)
                
                # Prevent self-deletion
                if user.id_pengguna == request.session.get('user_id'):
                    messages.error(request, 'Tidak dapat menghapus akun sendiri.')
                else:
                    user.delete()
                    messages.success(request, 'Pengguna berhasil dihapus.')
            except Pengguna.DoesNotExist:
                messages.error(request, 'Pengguna tidak ditemukan.')
            except Exception as e:
                messages.error(request, f'Gagal menghapus pengguna: {str(e)}')
    
    paginator = Paginator(pengguna_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Manajemen Pengguna',
        'active_section': 'pengguna',
        'page_obj': page_obj,
    }
    return render(request, 'diagnosis/admin_base.html', context)

@login_required_custom
@role_required(['pakar'])
def admin_gejala(request):
    gejala_list = Gejala.objects.all().order_by('kode_gejala')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                kode = request.POST.get('kode_gejala')
                nama = request.POST.get('nama_gejala')
                pertanyaan = request.POST.get('pertanyaan_gejala')
                
                if Gejala.objects.filter(kode_gejala=kode).exists():
                    messages.error(request, 'Kode gejala sudah ada.')
                else:
                    # Get the last ID and increment it
                    last_gejala = Gejala.objects.order_by('-id_gejala').first()
                    new_id = (last_gejala.id_gejala + 1) if last_gejala else 1
                    
                    new_gejala = Gejala(
                        id_gejala=new_id,
                        kode_gejala=kode,
                        nama_gejala=nama,
                        pertanyaan_gejala=pertanyaan
                    )
                    new_gejala.save()
                    messages.success(request, 'Gejala berhasil ditambahkan.')
            except Exception as e:
                messages.error(request, f'Gagal menambahkan gejala: {str(e)}')
                
        elif action == 'update':
            try:
                gejala_id = request.POST.get('id_gejala')
                gejala = Gejala.objects.get(id_gejala=gejala_id)
                
                gejala.kode_gejala = request.POST.get('kode_gejala')
                gejala.nama_gejala = request.POST.get('nama_gejala')
                gejala.pertanyaan_gejala = request.POST.get('pertanyaan_gejala')
                
                gejala.save()
                messages.success(request, 'Data gejala berhasil diperbarui.')
            except Gejala.DoesNotExist:
                messages.error(request, 'Gejala tidak ditemukan.')
            except Exception as e:
                messages.error(request, f'Gagal memperbarui gejala: {str(e)}')
                
        elif action == 'delete':
            try:
                gejala_id = request.POST.get('id_gejala')
                gejala = Gejala.objects.get(id_gejala=gejala_id)
                gejala.delete()
                messages.success(request, 'Gejala berhasil dihapus.')
            except Gejala.DoesNotExist:
                messages.error(request, 'Gejala tidak ditemukan.')
            except Exception as e:
                messages.error(request, f'Gagal menghapus gejala: {str(e)}')
    
    paginator = Paginator(gejala_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Manajemen Gejala',
        'active_section': 'gejala',
        'page_obj': page_obj,
    }
    return render(request, 'diagnosis/admin_base.html', context)

@login_required_custom
@role_required(['pakar'])
def admin_penyakit(request):
    penyakit_list = Diagnosis.objects.all().order_by('id_diagnosis')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                nama = request.POST.get('nama_diagnosis')
                deskripsi = request.POST.get('deskripsi_diagnosis')
                solusi = request.POST.get('solusi_diagnosis')
                gambar = request.POST.get('gambar_diagnosis')
                
                # Get the last ID and increment it
                last_penyakit = Diagnosis.objects.order_by('-id_diagnosis').first()
                new_id = (last_penyakit.id_diagnosis + 1) if last_penyakit else 1
                
                new_penyakit = Diagnosis(
                    id_diagnosis=new_id,
                    nama_diagnosis=nama,
                    deskripsi_diagnosis=deskripsi,
                    solusi_diagnosis=solusi,
                    gambar_diagnosis=gambar
                )
                new_penyakit.save()
                messages.success(request, 'Penyakit berhasil ditambahkan.')
            except Exception as e:
                messages.error(request, f'Gagal menambahkan penyakit: {str(e)}')
                
        elif action == 'update':
            try:
                penyakit_id = request.POST.get('id_diagnosis')
                penyakit = Diagnosis.objects.get(id_diagnosis=penyakit_id)
                
                penyakit.nama_diagnosis = request.POST.get('nama_diagnosis')
                penyakit.deskripsi_diagnosis = request.POST.get('deskripsi_diagnosis')
                penyakit.solusi_diagnosis = request.POST.get('solusi_diagnosis')
                penyakit.gambar_diagnosis = request.POST.get('gambar_diagnosis')
                
                penyakit.save()
                messages.success(request, 'Data penyakit berhasil diperbarui.')
            except Diagnosis.DoesNotExist:
                messages.error(request, 'Penyakit tidak ditemukan.')
            except Exception as e:
                messages.error(request, f'Gagal memperbarui penyakit: {str(e)}')
                
        elif action == 'delete':
            try:
                penyakit_id = request.POST.get('id_diagnosis')
                penyakit = Diagnosis.objects.get(id_diagnosis=penyakit_id)
                penyakit.delete()
                messages.success(request, 'Penyakit berhasil dihapus.')
            except Diagnosis.DoesNotExist:
                messages.error(request, 'Penyakit tidak ditemukan.')
            except Exception as e:
                messages.error(request, f'Gagal menghapus penyakit: {str(e)}')
    
    paginator = Paginator(penyakit_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Manajemen Penyakit',
        'active_section': 'penyakit',
        'page_obj': page_obj,
    }
    return render(request, 'diagnosis/admin_base.html', context)

@login_required_custom
@role_required(['admin'])
def update_diagnosis_images(request):
    # Dictionary mapping diagnosis names to their image files
    diagnosis_images = {
        'Hepatitis A': '/static/diagnosis/hepatitis-a.jpg',
        'Hepatitis B': '/static/diagnosis/hepatitis-b.jpg',
        'Hepatitis C': '/static/diagnosis/hepatitis-c.jpg',
        'Kanker Hati': '/static/diagnosis/kanker-hati.jpg',
        'Perlemakan Hati': '/static/diagnosis/perlemakan-hati.jpg',
        'Sirosis Hati': '/static/diagnosis/sirosis.png'
    }
    
    try:
        for diagnosis_name, image_path in diagnosis_images.items():
            diagnosis = Diagnosis.objects.filter(nama_diagnosis__icontains=diagnosis_name).first()
            if diagnosis:
                diagnosis.gambar_diagnosis = image_path
                diagnosis.save()
                messages.success(request, f'Berhasil memperbarui gambar untuk {diagnosis_name}')
            else:
                messages.warning(request, f'Diagnosis {diagnosis_name} tidak ditemukan')
        
        messages.success(request, 'Semua gambar diagnosis berhasil diperbarui')
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return redirect('admin_penyakit')