from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, logout, login
from electroapp.models import *
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
def dashboard(request):
    
    return render(request, 'dashboard.html')

def dashboard1(request):
    
    return render(request, 'dashboard1.html')

def user_register(request):
    now = datetime.now()
    if request.method == 'POST':
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        password=request.POST['password']
        role='User'
        u = User.objects.create(username=email, email=email, first_name=first_name,last_name=last_name,role=role)
        u.set_password(password)
        u.save()
        
  
        return redirect('/user_login/')
    return render(request, '/user_login')


def user_login(request):
    if request.method == 'POST':
        if User.objects.filter(username = request.POST['username']).exists():
            user = authenticate(request, username = request.POST['username'], password = request.POST['password'])

            if user is None:
                messages.error(request, 'Wrong Password Given')
                return redirect('/user_login')
            else:
                login(request, user)
                return redirect('/dashboard/')
        messages.error(request, 'Wrong Password Given')
        return redirect('/')
    return render(request, 'login/login.html')


@login_required(login_url = "/user_login/")
def user_logout(request):
    logout(request)
    return redirect('/dashboard/')