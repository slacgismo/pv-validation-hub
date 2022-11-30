from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import (
    api_view,
)

from .serializers import AccountSerializer
from .models import Account
import json


@api_view(["POST"])
@csrf_exempt
def register(request):
    # body = json.loads(request.body.decode('utf-8'))
    # _username = body.get("username")
    # _useremail = body.get("email")
    # _password = body.get("password")
    _username = request.data["username"]
    _useremail = request.data["email"]
    _password = request.data["password"]
    account = Account(username=_username, password=_password, email=_useremail)
    account.save()
    serializer = AccountSerializer(account)
    # user = User.objects.create_user(_username, _useremail, _password)
    # user.save()
    return JsonResponse(serializer.data)


@api_view(["POST"])
@csrf_exempt
def login(request):
    # body = json.loads(request.body.decode('utf-8'))
    # _username = body.get('username')
    # _password = body.get('password')
    _username = request.data["username"]
    _password = request.data["password"]
    account = Account.objects.get(username=_username)

    if account.password == _password:
        return HttpResponse("user logged in", status=200)
        # TODO: redirect to a success page
    else:
        return HttpResponse("wrong password", status=400)
        # TODO: return to an 'invalid login' error message

# def logout_view(request):
#     logout(request)
    # TODO: redirect to a success page

# def profile(request, username):
#     username = request.POST['username']
#     user = User.objects.filter(username=username)
#     if user is not None:
#         return render(request=request, template_name='profile.html', context='')
#     else:
#         return redirect('/')


@method_decorator(csrf_exempt, name='dispatch')
class AccountList(APIView):
    def get(self, request):
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        # data = JSONParser().parse(data=request.data)
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AccountDetail(APIView):
    """
    Retrieve, update or delete a user.
    """

    def get_object(self, pk):
        try:
            return Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return HttpResponse(status=404)

    def get(self, request, pk):
        account = self.get_object(pk)
        serializer = AccountSerializer(account)
        return JsonResponse(serializer.data)

    def put(self, request, pk):
        account = self.get_object(pk)
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    def delete(self, request, pk):
        account = self.get_object(pk)
        account.delete()
        return HttpResponse(status=204)
