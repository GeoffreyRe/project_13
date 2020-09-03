from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def first_view(request):
    text_response = "Ceci est la première vue du projet !"
    return HttpResponse(text_response)
