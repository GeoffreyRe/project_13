from django.shortcuts import render, HttpResponse, redirect
from .forms import UserForm, UserFormLogin
from users.models import User
from django.db.utils import IntegrityError
from django.contrib import messages
from django.contrib.auth import login as log, authenticate, logout 
from django.contrib.auth.decorators import login_required
# Create your views here.

def view_signup(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            # on crée l'utilisateur
            #import pdb; pdb.set_trace()
            try:
                user = User.objects.create_user(
                        user_form.cleaned_data['username'],
                        user_form.cleaned_data['email'],
                        user_form.cleaned_data['password'])
                log(request, user)
                messages.add_message(request, messages.INFO, "Vous êtes maintenant connecté, {}".format(user.username))
                return redirect('view_home')

            except IntegrityError:
                messages.add_message(request, messages.INFO, "Un utilisateur avec cet email existe déjà")
                user_form = UserForm(request.POST)
    else:
        user_form = UserForm()

    context = {'form' : user_form}
    return render(request, 'users/sign_up.html', context)

def view_login(request):
    if request.method == "POST":
        # on tente de loger l'utilisateur avec les données
        user_form_login = UserFormLogin(request.POST)
        
        """
        Je ne pense pas que ce soit la meilleure méthode : Voir avec Thierry
        """
        user = authenticate(
            email=request.POST['email'], password=request.POST['password']
        )
        if user is not None:
            log(request, user)
            messages.add_message(request, messages.ERROR, "Vous êtes maintenant connecté, {}".format(user.username))
            return redirect('view_home')
        else:
            # si l'utilisateur n'existe pas
            # on informe l'utilisateur
            messages.add_message(request, messages.ERROR, "Votre email et/ou mot de passe est incorrect")
    else:
        # si la requête est de type get ou autre
        user_form_login= UserFormLogin()
    
    context = {'form' : user_form_login}
    return render(request, "users/login.html", context)

@login_required
def view_logout(request):
    logout_username = request.user.username
    logout(request)
    messages.add_message(request, messages.INFO, "Vous avez été déconnecté, {}".format(logout_username))
    return redirect("view_home")