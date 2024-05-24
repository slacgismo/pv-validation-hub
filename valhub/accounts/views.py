from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import django.contrib.auth as auth

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .serializers import AccountSerializer
from .models import Account
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(["POST"])
def register(request):
    _username = request.data["username"]
    _useremail = request.data["email"]
    _password = request.data["password"]
    _firstName = request.data["firstName"]
    _lastName = request.data["lastName"]

    account = Account.objects.create(
        username=_username,
        email=_useremail,
        password=_password,
        firstName=_firstName,
        lastName=_lastName,
    )

    serializer = AccountSerializer(account)
    return JsonResponse(serializer.data)


@csrf_exempt
@api_view(["POST"])
def login(request):
    _username = request.data["username"]
    _password = request.data["password"]

    user = auth.authenticate(request, username=_username, password=_password)

    if user is not None:
        logger.info("User is authenticated")
        auth.login(request, user)

        # get or create login token for the user
        token = Token.objects.get_or_create(user=user)
        data = {
            "token": str(token[0].key),
        }

        dump = json.dumps(data)
        return HttpResponse(dump, content_type="application/json", status=200)
    else:
        return HttpResponse("wrong password", status=400)


@method_decorator(csrf_exempt, name="dispatch")
class AccountDetail(APIView):
    """
    Retrieve, update or delete a user.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def get(self, request):
        serializer = AccountSerializer(request.user)
        return JsonResponse(serializer.data)

    @csrf_exempt
    def put(self, request):
        account = request.user

        # update origin account
        serializer = AccountSerializer(
            account, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    @csrf_exempt
    def delete(self, request):
        account = request.user
        account.delete()
        return HttpResponse(status=204)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_id(request):
    user = request.user
    return JsonResponse({"user_id": user.uuid})
