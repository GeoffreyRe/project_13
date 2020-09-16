from django.shortcuts import render, HttpResponse, redirect
from .forms import UserForm
from users.models import User
from django.db.utils import IntegrityError
from django.contrib import messages
from django.contrib.auth import login as log
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
