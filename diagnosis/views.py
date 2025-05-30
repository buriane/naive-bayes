from django.shortcuts import render, redirect
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

                if user.role == 'admin':
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
        messages.warning(request, 'Silakan mulai konsultasi terlebih dahulu.')
        return redirect('konsultasi')

    gejala_ids_str = request.POST.getlist('gejala')
    if not gejala_ids_str:
        messages.warning(request, 'Anda belum memilih gejala apapun.')
        return redirect('konsultasi')

    try:
        gejala_ids = [int(gid) for gid in gejala_ids_str]
    except ValueError:
        messages.error(request, 'Input gejala tidak valid.')
        return redirect('konsultasi')

    all_diagnoses = list(Diagnosis.objects.all())
    all_gejala_objects = list(Gejala.objects.all())

    if not all_diagnoses or not all_gejala_objects:
        messages.error(request, 'Data master penyakit atau gejala tidak ditemukan. Hubungi admin.')
        return redirect('konsultasi')

    diagnosis_counts = {}
    total_records = 0
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_diagnosis_id, COUNT(*) as count FROM laporandiagnosis GROUP BY id_diagnosis_id")
        for row in cursor.fetchall():
            diagnosis_counts[row[0]] = row[1]
            total_records += row[1]
    
    if total_records == 0 or len(all_diagnoses) == 0:
        messages.info(request, "Belum cukup data historis untuk diagnosis akurat. Hasil mungkin kurang presisi.")

    if total_records < len(all_diagnoses) or total_records == 0:
        default_prob = 1 / len(all_diagnoses) if len(all_diagnoses) > 0 else 0.01
        prior_probabilities = {d.id_diagnosis: default_prob for d in all_diagnoses}
    else:
        prior_probabilities = {
            d.id_diagnosis: diagnosis_counts.get(d.id_diagnosis, 0.01) / total_records
            for d in all_diagnoses
        }

    conditional_probs = {}
    epsilon = 1e-9
    for diagnosis_obj in all_diagnoses:
        conditional_probs[diagnosis_obj.id_diagnosis] = {}
        disease_total_reports = diagnosis_counts.get(diagnosis_obj.id_diagnosis, 0)
        for gejala_obj in all_gejala_objects:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM laporangejala lg
                    JOIN laporandiagnosis ld ON lg.id_laporanDiagnosis_id = ld.id_laporandiagnosis
                    WHERE ld.id_diagnosis_id = %s AND lg.id_gejala_id = %s AND lg.value = 1
                """, [diagnosis_obj.id_diagnosis, gejala_obj.id_gejala])
                symptom_count_with_disease = cursor.fetchone()[0]
            conditional_probs[diagnosis_obj.id_diagnosis][gejala_obj.id_gejala] = \
                (symptom_count_with_disease + 1) / (disease_total_reports + 2)

    results = []
    for diagnosis_obj in all_diagnoses:
        log_prior = math.log(prior_probabilities.get(diagnosis_obj.id_diagnosis, epsilon))
        log_likelihood = 0
        for gejala_obj in all_gejala_objects:
            prob_symptom_given_disease = conditional_probs[diagnosis_obj.id_diagnosis].get(gejala_obj.id_gejala, epsilon)
            if gejala_obj.id_gejala in gejala_ids:
                log_likelihood += math.log(max(prob_symptom_given_disease, epsilon))
            else:
                prob_not_symptom = 1.0 - prob_symptom_given_disease
                log_likelihood += math.log(max(prob_not_symptom, epsilon))
        log_posterior = log_prior + log_likelihood
        results.append((diagnosis_obj, log_posterior))

    if not results:
        messages.error(request, "Tidak dapat menghitung hasil diagnosis.")
        return redirect('konsultasi')

    results.sort(key=lambda x: x[1], reverse=True)
    top_diagnosis_obj, top_log_prob = results[0]
    
    max_log_prob = results[0][1] 
    scaled_probs_sum = sum(math.exp(r_log_p - max_log_prob) for _, r_log_p in results)
    
    probability_percentage = 0
    if scaled_probs_sum > 0:
        top_scaled_prob = math.exp(top_log_prob - max_log_prob)
        probability_percentage = (top_scaled_prob / scaled_probs_sum) * 100
    elif len(all_diagnoses) > 0 :
        probability_percentage = 100 / len(all_diagnoses)
    
    user_id_session = request.session.get('user_id', None)
    new_report_id_val = (Laporandiagnosis.objects.order_by('-id_laporandiagnosis').first().id_laporandiagnosis + 1) \
        if Laporandiagnosis.objects.exists() else 1
    
    new_report = Laporandiagnosis(
        id_laporandiagnosis=new_report_id_val,
        id_pengguna_id=user_id_session,
        id_diagnosis_id=top_diagnosis_obj.id_diagnosis,
        tanggal_diagnosis=date.today(), # Ini akan menjadi objek date
        probabilitas=round(probability_percentage, 2)
    )
    new_report.save()

    for gejala_obj_loop in all_gejala_objects:
        new_gejala_report_id_val = (Laporangejala.objects.order_by('-id_laporangejala').first().id_laporangejala + 1) \
            if Laporangejala.objects.exists() else 1
        value_for_report = 1 if gejala_obj_loop.id_gejala in gejala_ids else 0
        Laporangejala.objects.create(
            id_laporangejala=new_gejala_report_id_val,
            id_laporanDiagnosis_id=new_report.id_laporandiagnosis,
            id_gejala_id=gejala_obj_loop.id_gejala,
            value=value_for_report
        )

    selected_gejala_objects = Gejala.objects.filter(id_gejala__in=gejala_ids)
    return render(request, 'diagnosis/hasil.html', {
        'diagnosis': top_diagnosis_obj,
        'probability': round(probability_percentage, 2),
        'selected_gejala': selected_gejala_objects,
        'date': new_report.tanggal_diagnosis,
    })

@login_required_custom
def riwayat(request):
    user_id_session = request.session.get('user_id')
    riwayat_diagnosis_list = Laporandiagnosis.objects.filter(
        id_pengguna_id=user_id_session
    ).select_related('id_diagnosis', 'id_pengguna').order_by('-tanggal_diagnosis')
    
    paginator = Paginator(riwayat_diagnosis_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Riwayat Diagnosismu',
        'page_obj': page_obj,
    }
    return render(request, 'diagnosis/riwayat.html', context)
    
def detail_hasil(request, laporan_id):
    try:
        laporan_obj = Laporandiagnosis.objects.select_related('id_diagnosis', 'id_pengguna').get(id_laporandiagnosis=laporan_id)
        
        user_id_session = request.session.get('user_id')
        user_role_session = request.session.get('user_role')
        
        if laporan_obj.id_pengguna_id != user_id_session and user_role_session != 'admin':
             messages.error(request, 'Anda tidak diizinkan untuk melihat detail laporan ini.')
             return redirect('riwayat' if user_role_session != 'admin' else 'homepage')

        # PERBAIKAN DI SINI:
        # Asumsikan field ForeignKey di model Laporangejala yang menunjuk ke Laporandiagnosis
        # bernama 'id_laporandiagnosis'
        gejala_reports_for_laporan = Laporangejala.objects.filter(
            id_laporandiagnosis=laporan_obj, value=1 
        ).select_related('id_gejala') 
        # Alternatif jika nama fieldnya id_laporandiagnosis_id (kurang umum untuk nama field Django):
        # gejala_reports_for_laporan = Laporangejala.objects.filter(
        #     id_laporandiagnosis_id=laporan_obj.id_laporandiagnosis, value=1 
        # ).select_related('id_gejala')
        
        selected_gejala_from_report_objects = [gr.id_gejala for gr in gejala_reports_for_laporan]
        
        return render(request, 'diagnosis/hasil.html', {
            'diagnosis': laporan_obj.id_diagnosis,
            'probability': laporan_obj.probabilitas,
            'selected_gejala': selected_gejala_from_report_objects,
            'date': laporan_obj.tanggal_diagnosis,
            'laporan_pengguna': laporan_obj.id_pengguna,
            'is_detail_view': True,
            'laporan_id': laporan_id,
            'page_title': f"Detail Laporan #{laporan_id}"
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

# --- Admin Panel Views ---
@login_required_custom
def admin_beranda(request):
    if request.session.get('user_role') != 'admin':
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('homepage')

    total_laporan = Laporandiagnosis.objects.count()
    total_gejala = Gejala.objects.count()
    total_penyakit = Diagnosis.objects.count()
    konsultasi_today = Laporandiagnosis.objects.filter(tanggal_diagnosis=date.today()).count()

    penyakit_data_for_chart = Laporandiagnosis.objects.values(
        'id_diagnosis__nama_diagnosis'
    ).annotate(
        jumlah=Count('id_diagnosis_id')
    ).order_by('-jumlah')
    penyakit_terdiagnosis_top = list(penyakit_data_for_chart[:5])

    riwayat_terbaru_beranda = Laporandiagnosis.objects.select_related('id_diagnosis', 'id_pengguna').order_by('-tanggal_diagnosis')[:5]

    chart_labels = [item['id_diagnosis__nama_diagnosis'] for item in penyakit_terdiagnosis_top]
    chart_data = [item['jumlah'] for item in penyakit_terdiagnosis_top]

    diagnosis_trend_labels = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"] # Data dummy
    diagnosis_trend_data = [12, 19, 3, 5, 2, 3, 7] # Data dummy

    context = {
        'page_title': 'Beranda Admin',
        'active_section': 'beranda',
        'total_laporan': total_laporan,
        'total_gejala': total_gejala,
        'total_penyakit': total_penyakit,
        'konsultasi_today': konsultasi_today,
        'penyakit_terdiagnosis': penyakit_terdiagnosis_top,
        'riwayat_terbaru_beranda': riwayat_terbaru_beranda,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'diagnosis_trend_labels': diagnosis_trend_labels,
        'diagnosis_trend_data': diagnosis_trend_data,
        'user_name': request.session.get('user_name', 'Admin')
    }
    return render(request, 'diagnosis/admin_base.html', context)

@login_required_custom
def admin_riwayat(request):
    if request.session.get('user_role') != 'admin':
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('homepage')

    search_query = request.GET.get('search', '')
    # PERBAIKAN: Urutkan berdasarkan id_laporandiagnosis secara ascending
    laporan_list_all = Laporandiagnosis.objects.select_related('id_diagnosis', 'id_pengguna').order_by('id_laporandiagnosis')

    if search_query:
        filters = Q(id_pengguna__nama_pengguna__icontains=search_query) | \
                  Q(id_diagnosis__nama_diagnosis__icontains=search_query)
        if search_query.isdigit():
            try:
                filters |= Q(id_laporandiagnosis=int(search_query))
            except ValueError:
                pass
        laporan_list_all = laporan_list_all.filter(filters)
    
    paginator = Paginator(laporan_list_all, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Riwayat Konsultasi (Admin)',
        'active_section': 'riwayat',
        'page_obj': page_obj,
        'search_query': search_query,
        'user_name': request.session.get('user_name', 'Admin')
    }
    return render(request, 'diagnosis/admin_base.html', context)

@login_required_custom
def admin_gejala(request):
    if request.session.get('user_role') != 'admin':
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('homepage')
    
    search_query = request.GET.get('search', '')
    # PERBAIKAN: Urutkan berdasarkan id_gejala secara ascending
    gejala_list_all = Gejala.objects.all().order_by('id_gejala')

    if search_query:
        filters = Q(kode_gejala__icontains=search_query) | \
                  Q(nama_gejala__icontains=search_query)
        if search_query.isdigit():
            try:
                filters |= Q(id_gejala=int(search_query))
            except ValueError:
                pass
        gejala_list_all = gejala_list_all.filter(filters)

    paginator = Paginator(gejala_list_all, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Manajemen Gejala (Admin)',
        'active_section': 'gejala',
        'page_obj': page_obj,
        'search_query': search_query,
        'user_name': request.session.get('user_name', 'Admin')
    }
    return render(request, 'diagnosis/admin_base.html', context)

@login_required_custom
def admin_penyakit(request):
    if request.session.get('user_role') != 'admin':
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('homepage')

    search_query = request.GET.get('search', '')
    # Urutkan berdasarkan id_diagnosis secara ascending
    penyakit_list_all = Diagnosis.objects.all().order_by('id_diagnosis')

    if search_query:
        filters = Q(nama_diagnosis__icontains=search_query) | \
                  Q(deskripsi_diagnosis__icontains=search_query)
        if search_query.isdigit():
            try:
                filters |= Q(id_diagnosis=int(search_query))
            except ValueError:
                pass
        penyakit_list_all = penyakit_list_all.filter(filters)

    paginator = Paginator(penyakit_list_all, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Manajemen Penyakit (Admin)',
        'active_section': 'penyakit',
        'page_obj': page_obj,
        'search_query': search_query,
        'user_name': request.session.get('user_name', 'Admin')
    }
    return render(request, 'diagnosis/admin_base.html', context)