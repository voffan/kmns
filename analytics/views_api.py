from collections import defaultdict

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import OuterRef, Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.http import Http404
from django.shortcuts import redirect, render, reverse, get_object_or_404

from main.models import *
from reports.models import *


@login_required(login_url='/users/login/')
def get_data(request):
    return JsonResponse({'result': True})