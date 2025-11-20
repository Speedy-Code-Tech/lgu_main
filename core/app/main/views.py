from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def dashboard(request):
    user = request.user
    context = {
        "title":"Login",
        "name": user,
        "active":'dashboard'
    }
    return render(request,"dashboard.html",context)