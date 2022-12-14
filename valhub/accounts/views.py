from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view

from .serializers import AccountSerializer
from .models import Account
import json


@csrf_exempt
@api_view(["POST"])
def register(request):
    _username = request.data["username"]
    _useremail = request.data["email"]
    _password = request.data["password"]
    _firstName = request.data["firstName"]
    _lastName = request.data["lastName"]
    account = Account(
        username = _username, 
        password = _password, 
        email = _useremail,
        firstName = _firstName,
        lastName = _lastName,
    )
    account.save()
    serializer = AccountSerializer(account)
    return JsonResponse(serializer.data)


@csrf_exempt
@api_view(["POST"])
def login(request):
    _username = request.data['username']
    _password = request.data['password']
    account = Account.objects.get(username=_username)

    if account.password == _password:
        data = {
            'id': str(account.id),
        }
        dump = json.dumps(data)
        return HttpResponse(dump, content_type='application/json', status=200)
    else:
        return HttpResponse("wrong password", status=400)

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
    @csrf_exempt
    def get_object(self, pk):
        try:
            # _id = request.data["id"]
            # _username = request.data['username']
            return Account.objects.get(pk=pk)
        except Account.DoesNotExist:
            return HttpResponse(status=404)
    @csrf_exempt
    def get(self, request, pk):
        account = self.get_object(pk=pk)
        _account = Account(
            id=account.id,
            username=account.username, 
            email=account.email,
            firstName=account.firstName,
            lastName=account.lastName,
            )
        serializer = AccountSerializer(_account)
        return JsonResponse(serializer.data)
    @csrf_exempt
    def put(self, request, pk):
        account = self.get_object(pk=pk)
        serializer = AccountSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    @csrf_exempt
    def delete(self, request, pk):
        account = self.get_object(pk=pk)
        account.delete()
        return HttpResponse(status=204)
