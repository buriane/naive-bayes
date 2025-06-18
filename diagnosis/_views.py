from django.shortcuts import render, redirect
from .models import Diagnosis, Gejala, Laporandiagnosis, Laporangejala, Pengguna
from django.db import connection
import numpy as np
from datetime import date
import math
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
import uuid
from functools import wraps

# Create your views here.


def homepage(request):
    return render(request, 'diagnosis/index.html')


def login(request):
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        # Validation
        if not email or not password:
            messages.error(request, 'Email dan password harus diisi.')
            return render(request, 'diagnosis/login.html')
        
        try:
            # Check if user exists
            user = Pengguna.objects.get(email=email)
            
            # Verify password
            if check_password(password, user.password):
                # Login successful - store user info in session
                request.session['user_id'] = user.id_pengguna
                request.session['user_name'] = user.nama_pengguna
                request.session['user_email'] = user.email
                request.session['user_role'] = user.role
                
                return redirect('homepage')
            else:
                messages.error(request, 'Email atau password tidak valid.')
                return render(request, 'diagnosis/login.html')
                
        except Pengguna.DoesNotExist:
            messages.error(request, 'Email atau password tidak valid.')
            return render(request, 'diagnosis/login.html')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return render(request, 'diagnosis/login.html')
    
    return render(request, 'diagnosis/login.html')

def logout(request):
    request.session.flush()
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('login')

def konsultasi(request):
    gejala_list = Gejala.objects.all()
    return render(request, 'diagnosis/konsultasi.html', {
        'gejala_list': gejala_list,
    })

def register(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        terms = request.POST.get('terms')

        # Validation
        if not all([first_name, last_name, email, password]):
            messages.error(request, 'Semua field harus diisi.')
            return render(request, 'diagnosis/register.html')

        if password != confirm_password:
            messages.error(
                request, 'Password dan konfirmasi password tidak cocok.')
            return render(request, 'diagnosis/register.html')

        if not terms:
            messages.error(
                request, 'Anda harus menyetujui syarat dan ketentuan.')
            return render(request, 'diagnosis/register.html')

        # Check if email already exists
        if Pengguna.objects.filter(email=email).exists():
            messages.error(
                request, 'Email sudah terdaftar. Silakan gunakan email lain.')
            return render(request, 'diagnosis/register.html')

        try:
            last_user = Pengguna.objects.order_by('-id_pengguna').first()
            if last_user:
                user_id = last_user.id_pengguna + 1
            else:
                user_id = 1  # First user

            # Combine first and last name
            full_name = f"{first_name} {last_name}"

            # Hash password
            hashed_password = make_password(password)

            # Create new user
            new_user = Pengguna(
                id_pengguna=user_id,
                nama_pengguna=full_name,
                email=email,
                password=hashed_password,
                role='user'  # Default role for registered users
            )
            new_user.save()

            messages.success(
                request, 'Registrasi berhasil! Silakan login dengan akun Anda.')
            return redirect('register')

        except Exception as e:
            messages.error(
                request, f'Terjadi kesalahan saat registrasi: {str(e)}')
            return render(request, 'diagnosis/register.html')

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

    # Prepare data for Naive Bayes calculation
    # 1. Get prior probabilities (how frequently each diagnosis occurs)
    # We'll use a SQL query to get this information from existing records
    diagnosis_counts = {}
    total_records = 0

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_diagnosis, COUNT(*) as count 
            FROM laporandiagnosis 
            GROUP BY id_diagnosis
        """)
        for row in cursor.fetchall():
            diagnosis_id, count = row
            diagnosis_counts[diagnosis_id] = count
            total_records += count

    # If we don't have enough records, use uniform probability
    if total_records < len(all_diagnoses):
        prior_probabilities = {d.id_diagnosis: 1 /
                               len(all_diagnoses) for d in all_diagnoses}
    else:
        prior_probabilities = {d.id_diagnosis: diagnosis_counts.get(d.id_diagnosis, 0.1)/total_records
                               for d in all_diagnoses}

    # 2. Calculate conditional probabilities P(symptom | disease)
    # We'll use Laplace smoothing to handle unseen data
    conditional_probs = {}

    for diagnosis in all_diagnoses:
        conditional_probs[diagnosis.id_diagnosis] = {}

        # For each symptom, calculate P(symptom | disease)
        for gejala in all_gejala:
            # Count how many times this symptom appears with this disease
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM laporangejala lg
                    JOIN laporandiagnosis ld ON lg.id_laporanDiagnosis = ld.id_laporanDiagnosis
                    WHERE ld.id_diagnosis = %s AND lg.id_gejala = %s AND lg.value = 1
                """, [diagnosis.id_diagnosis, gejala.id_gejala])
                symptom_count = cursor.fetchone()[0]

            # Get total number of records for this disease
            disease_total = diagnosis_counts.get(diagnosis.id_diagnosis, 0)

            # Apply Laplace smoothing (add 1 to numerator, add 2 to denominator)
            conditional_probs[diagnosis.id_diagnosis][gejala.id_gejala] = (
                symptom_count + 1) / (disease_total + 2)

    # 3. Calculate posterior probabilities using Naive Bayes
    results = []
    for diagnosis in all_diagnoses:
        # Start with prior probability (in log space to avoid underflow)
        log_posterior = math.log(prior_probabilities.get(
            diagnosis.id_diagnosis, 1/len(all_diagnoses)))

        # Multiply by conditional probabilities
        for gejala_id in gejala_ids:
            # If we have this symptom, use P(symptom=1|disease)
            log_posterior += math.log(
                conditional_probs[diagnosis.id_diagnosis].get(gejala_id, 0.1))

        # For symptoms we don't have, use P(symptom=0|disease) = 1 - P(symptom=1|disease)
        for gejala in all_gejala:
            if gejala.id_gejala not in gejala_ids:
                log_posterior += math.log(
                    1 - conditional_probs[diagnosis.id_diagnosis].get(gejala.id_gejala, 0.1))

        # Convert back from log space
        posterior = math.exp(log_posterior)
        results.append((diagnosis, posterior))

    # Sort by probability (highest first)
    results.sort(key=lambda x: x[1], reverse=True)

    # Get the top diagnosis
    top_diagnosis, probability = results[0]

    # Normalize the probability to 0-100%
    total_prob = sum(prob for _, prob in results)
    probability_percentage = (probability / total_prob) * \
        100 if total_prob > 0 else 0

    # Store the diagnosis result (for both logged in and not logged in users)
    user_id = request.session.get('user_id', None)
    
    # Generate auto-increment ID for the report
    last_report = Laporandiagnosis.objects.order_by('-id_laporandiagnosis').first()
    if last_report:
        new_report_id = last_report.id_laporandiagnosis + 1
    else:
        new_report_id = 1
    
    # Create a new diagnosis report
    # If user is logged in, use user_id, otherwise set to None
    new_report = Laporandiagnosis(
        id_laporandiagnosis=new_report_id,
        id_pengguna_id=user_id,  # This will be None if user is not logged in
        id_diagnosis=top_diagnosis,
        tanggal_diagnosis=date.today(),
        probabilitas=probability_percentage
    )
    new_report.save()

    # Store all the symptoms
    for gejala in all_gejala:
        # Generate auto-increment ID for each symptom record
        last_gejala_report = Laporangejala.objects.order_by('-id_laporangejala').first()
        if last_gejala_report:
            new_gejala_id = last_gejala_report.id_laporangejala + 1
        else:
            new_gejala_id = 1
        
        value = 1 if gejala.id_gejala in gejala_ids else 0
        laporangejala = Laporangejala(
            id_laporangejala=new_gejala_id,  # Add primary key
            id_laporandiagnosis=new_report,
            id_gejala_id=gejala.id_gejala,
            value=value
        )
        laporangejala.save()

    # Get selected symptoms
    selected_gejala = Gejala.objects.filter(id_gejala__in=gejala_ids)

    return render(request, 'diagnosis/hasil.html', {
        'diagnosis': top_diagnosis,
        'probability': probability_percentage,
        'selected_gejala': selected_gejala,
        'date': date.today(),
    })

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, 'Silakan login terlebih dahulu.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
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
        # Get the specific diagnosis report
        laporan = Laporandiagnosis.objects.get(id_laporandiagnosis=laporan_id)
        
        # Get the symptoms for this diagnosis
        gejala_reports = Laporangejala.objects.filter(
            id_laporandiagnosis=laporan,
            value=1  # Only get symptoms that were present
        )
        
        # Get the actual Gejala objects
        selected_gejala = []
        for gejala_report in gejala_reports:
            gejala = Gejala.objects.get(id_gejala=gejala_report.id_gejala_id)
            selected_gejala.append(gejala)
        
        return render(request, 'diagnosis/hasil.html', {
            'diagnosis': laporan.id_diagnosis,
            'probability': laporan.probabilitas,
            'selected_gejala': selected_gejala,
            'date': laporan.tanggal_diagnosis,
            'is_detail_view': True,  # Flag to indicate this is a detail view
        })
        
    except Laporandiagnosis.DoesNotExist:
        # If diagnosis report doesn't exist, redirect to riwayat
        return redirect('riwayat')
    except Exception as e:
        # Handle any other errors
        return redirect('riwayat')


def testing_view(request):
    diagnosis_list = Diagnosis.objects.all()
    gejala_list = Gejala.objects.all()
    return render(request, 'diagnosis/testing.html', {
        'diagnosis_list': diagnosis_list,
        'gejala_list': gejala_list,
    })

@login_required
def admin_panel(request):
    total_pasien = Laporandiagnosis.objects.count()
    total_gejala = Gejala.objects.count()
    total_penyakit = Diagnosis.objects.count()
    konsultasi_today = Laporandiagnosis.objects.filter(tanggal_diagnosis=date.today()).count()

    penyakit_terdiagnosis = Diagnosis.objects.raw('''
        SELECT d.id_diagnosis, d.nama_diagnosis, COUNT(ld.id_diagnosis) as jumlah
        FROM laporandiagnosis ld
        JOIN diagnosis d ON d.id_diagnosis = ld.id_diagnosis
        GROUP BY d.id_diagnosis
        ORDER BY jumlah DESC
    ''')

    gejala_list = Gejala.objects.all()
    penyakit_list = Diagnosis.objects.all()
    riwayat_list = Laporandiagnosis.objects.select_related('id_diagnosis', 'id_pengguna').order_by('-tanggal_diagnosis')[:10]

    return render(request, 'diagnosis/admin_panel.html', {
        'total_pasien': total_pasien,
        'total_gejala': total_gejala,
        'total_penyakit': total_penyakit,
        'konsultasi_today': konsultasi_today,
        'penyakit_terdiagnosis': penyakit_terdiagnosis,
        'gejala_list': gejala_list,
        'penyakit_list': penyakit_list,
        'riwayat_list': riwayat_list,
    })