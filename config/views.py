from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import SignUpForm
from insights.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # role = form.cleaned_data['role']

            # First check if the username already exists
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Username already taken.')
                return render(request, 'signup.html', {'form': form})

            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)

            # Only create profile if it doesn't already exist
            # UserProfile.objects.create(user=user, role=role)

            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def home_view(request):
    if request.user.is_authenticated:
        profile = request.user.userprofile

        return render(request, 'home.html', {'user': request.user, 'profile': profile })
    
    # Not logged in
    signup_form = SignUpForm()
    login_form = AuthenticationForm()

    return render(request, 'home.html', {
        'signup_form': signup_form,
        'login_form': login_form
    })
# touched on 2025-05-27T15:28:59.282941Z