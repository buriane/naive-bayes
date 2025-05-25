from django.shortcuts import render
from .models import Diagnosis, Gejala

# Create your views here.
def homepage(request):
    return render(request, 'diagnosis/index.html')

def login(request):
    return render(request, 'diagnosis/login.html')

def konsultasi(request):
    return render(request, 'diagnosis/konsultasi.html')

def register(request):
    return render(request, 'diagnosis/register.html')

def tentang(request):
    return render(request, 'diagnosis/tentang.html')

def hasil(request):
    return render(request, 'diagnosis/hasil.html')

def riwayat(request):
    return render(request, 'diagnosis/riwayat.html')

def testing_view(request):
    diagnosis_list = Diagnosis.objects.all()
    gejala_list = Gejala.objects.all()
    return render(request, 'diagnosis/testing.html', {
        'diagnosis_list': diagnosis_list,
        'gejala_list': gejala_list,
    })
