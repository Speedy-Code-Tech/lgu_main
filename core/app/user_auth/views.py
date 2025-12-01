from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request,user)
                return redirect('dashboard')
            
            else:
                messages.error(request,"Your account has been disabled")
                return render(request,"login.html")
                
        else:
            messages.error(request,"Invalid Username or Password")
            return render(request,"login.html")
                
    else:
        context = {
            "title":"Login"
        }
        return render(request,"login.html",context)
    
def user_logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
