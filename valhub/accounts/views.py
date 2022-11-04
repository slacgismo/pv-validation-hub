from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
# Create your views here.

def sign_in(request):
    return HttpResponse("go to sign in page")

def register():
    return HttpResponse("register a new user")

def log_in():
    return HttpResponse("user logged in")

def home():
    return HttpResponse("user home page, display user information")