from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


@login_required(login_url='/users/login/')
def map(request):
    return render(request, "analytics/monitoring.html")