from django.shortcuts import render

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