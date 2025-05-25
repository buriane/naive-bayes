from django.shortcuts import render, redirect
from .models import Diagnosis, Gejala, Laporandiagnosis, Laporangejala, Pengguna
from django.db import connection
import numpy as np
from datetime import date
import math

# Create your views here.
def homepage(request):
    return render(request, 'diagnosis/index.html')

def login(request):
    return render(request, 'diagnosis/login.html')

def konsultasi(request):
    gejala_list = Gejala.objects.all()
    return render(request, 'diagnosis/konsultasi.html', {
        'gejala_list': gejala_list,
    })

def register(request):
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
        prior_probabilities = {d.id_diagnosis: 1/len(all_diagnoses) for d in all_diagnoses}
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
            conditional_probs[diagnosis.id_diagnosis][gejala.id_gejala] = (symptom_count + 1) / (disease_total + 2)
    
    # 3. Calculate posterior probabilities using Naive Bayes
    results = []
    for diagnosis in all_diagnoses:
        # Start with prior probability (in log space to avoid underflow)
        log_posterior = math.log(prior_probabilities.get(diagnosis.id_diagnosis, 1/len(all_diagnoses)))
        
        # Multiply by conditional probabilities
        for gejala_id in gejala_ids:
            # If we have this symptom, use P(symptom=1|disease)
            log_posterior += math.log(conditional_probs[diagnosis.id_diagnosis].get(gejala_id, 0.1))
        
        # For symptoms we don't have, use P(symptom=0|disease) = 1 - P(symptom=1|disease)
        for gejala in all_gejala:
            if gejala.id_gejala not in gejala_ids:
                log_posterior += math.log(1 - conditional_probs[diagnosis.id_diagnosis].get(gejala.id_gejala, 0.1))
        
        # Convert back from log space
        posterior = math.exp(log_posterior)
        results.append((diagnosis, posterior))
    
    # Sort by probability (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Get the top diagnosis
    top_diagnosis, probability = results[0]
    
    # Normalize the probability to 0-100%
    total_prob = sum(prob for _, prob in results)
    probability_percentage = (probability / total_prob) * 100 if total_prob > 0 else 0
    
    # Store the diagnosis result if user is logged in
    user_id = request.session.get('user_id', None)
    if user_id:
        # Create a new diagnosis report
        new_report = Laporandiagnosis(
            id_pengguna_id=user_id,
            id_diagnosis=top_diagnosis,
            tanggal_diagnosis=date.today(),
            probabilitas=probability_percentage
        )
        new_report.save()
        
        # Get the ID of the new report
        report_id = new_report.id_laporandiagnosis
        
        # Store all the symptoms
        for gejala_id in all_gejala:
            value = 1 if gejala_id.id_gejala in gejala_ids else 0
            laporangejala = Laporangejala(
                id_laporandiagnosis=new_report,
                id_gejala_id=gejala_id.id_gejala,
                value=value
            )
            laporangejala.save()
    
    # Get selected symptoms
    selected_gejala = Gejala.objects.filter(id_gejala__in=gejala_ids)
    
    return render(request, 'diagnosis/hasil.html', {
        'diagnosis': top_diagnosis,
        'probability': probability_percentage,
        'selected_gejala': selected_gejala,
    })

def riwayat(request):
    return render(request, 'diagnosis/riwayat.html')

def testing_view(request):
    diagnosis_list = Diagnosis.objects.all()
    gejala_list = Gejala.objects.all()
    return render(request, 'diagnosis/testing.html', {
        'diagnosis_list': diagnosis_list,
        'gejala_list': gejala_list,
    })
