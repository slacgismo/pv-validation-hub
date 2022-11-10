from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
# Create your views here.

def register(request):
    username = request.POST['username']
    useremail = request.POST['email']
    password = request.POST['pwd']
    user = User.objects.create_user('username', 'useremail', 'userPassword')
    user.save()
    return HttpResponse("register a new user")

def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # TODO: redirect to a success page
    else:
        return -1
        # TODO: return to an 'invalid login' error message

def logout_view(request):
    logout(request)
    # TODO: redirect to a success page

def profile(request, username):
    username = request.POST['username']
    user = User.objects.filter(username=username)
    if user is not None:
        return render(request=request, template_name='profile.html', context='')
    else:
        return redirect('/')