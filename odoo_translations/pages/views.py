from django.shortcuts import render

# Create your views here.


def view_home(request):
    return render(request, "pages/home.html")

def view_legal_notice(request):
    return render(request, "pages/legal_notice.html")