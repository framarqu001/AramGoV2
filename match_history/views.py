

from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.

def home(request):
    return render(request, 'match_history/index.html')

def match_history(request):
    pass

def about(request):
    pass

def champions(reques):
    pass
