from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
# from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt

from .serializers import AccountSerializer
from .models import Account
# Create your views here.

def register(request):
    _username = request.POST['username']
    _useremail = request.POST['email']
    _password = request.POST['pwd']
    # newAccount = Account(username = _username, password = _password, _email = _useremail)
    # newAccount.save()
    user = User.objects.create_user(_username, _useremail, _password)
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

# def profile(request, username):
#     username = request.POST['username']
#     user = User.objects.filter(username=username)
#     if user is not None:
#         return render(request=request, template_name='profile.html', context='')
#     else:
#         return redirect('/')


@csrf_exempt
def account_list(request):
    """
    List all users, or create a user.
    """
    request
    if request.method == 'GET':
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(data=data)
        serializer = AccountSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def account_detail(request, pk):
    """
    Retrieve, update or delete a user.
    """
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = AccountSerializer(account)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = AccountSerializer(account, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        account.delete()
        return HttpResponse(status=204)

