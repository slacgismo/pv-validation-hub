from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import django.contrib.auth as auth

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication,
)

from .serializers import AccountSerializer, AccountSerializerClean
from .models import Account
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(["POST"])
def register(request: Request):
    required_fields = [
        "username",
        "email",
        "password",
        "firstName",
        "lastName",
        "acceptTerms",
    ]

    if request.data is None or not isinstance(request.data, dict):
        return HttpResponse("missing request data", status=400)

    if not all(field in request.data for field in required_fields):
        return HttpResponse("missing required fields", status=400)

    _username = request.data["username"]
    _useremail = request.data["email"]
    _password = request.data["password"]
    _firstName = request.data["firstName"]
    _lastName = request.data["lastName"]
    _acceptTerms = request.data["acceptTerms"]

    if _acceptTerms is not True:
        return JsonResponse({"error": "You must accept the terms"}, status=400)

    account = Account(
        username=_username,
        email=_useremail,
        firstName=_firstName,
        lastName=_lastName,
        acceptTerms=_acceptTerms,
    )
    account.set_password(_password)
    account.save()

    # Automatically log the user in after registration
    user = auth.authenticate(request, username=_username, password=_password)

    if user is not None:
        logging.error(f"uuid: {user.uuid}")
    else:
        logging.error("user is None")

    if user is not None:
        auth.login(request, user)

        # get or create login token for the user
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            "token": str(token.key),
            "user": AccountSerializer(account).data,
            "username": _username,
        }

        return JsonResponse(data, status=201)

    return JsonResponse({"error": "Invalid credentials"}, status=400)


@csrf_exempt
@api_view(["POST"])
def login(request: Request):

    if request.data is None or not isinstance(request.data, dict):
        return HttpResponse("missing request data", status=400)

    required_fields = ["username", "password"]

    if not all(field in request.data for field in required_fields):
        return HttpResponse("missing required fields", status=400)

    _username = request.data["username"]
    _password = request.data["password"]

    user = auth.authenticate(request, username=_username, password=_password)

    if user is not None:
        logger.info("User is authenticated")

        auth.login(request._request, user)

        # get or create login token for the user
        token = Token.objects.get_or_create(user=user)
        data = {
            "token": str(token[0].key),
            "username": _username,
        }

        dump = json.dumps(data)
        return HttpResponse(dump, content_type="application/json", status=200)
    else:
        return HttpResponse("Invalid credentials", status=400)


# This class will be deprecated, we should standardize to functions
class AccountDetail(APIView):
    """
    Retrieve, update or delete a user.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def get(self, request: Request):
        logger.info("user", request.user)
        logger.info("auth", request.auth)
        logger.info("req:", request)
        serializer = AccountSerializer(request.user)
        return JsonResponse(serializer.data)

    @csrf_exempt
    def put(self, request: Request):
        account = request.user
        data = request.data

        # update origin account
        serializer = AccountSerializer(account, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    @csrf_exempt
    def delete(self, request: Request):
        account = request.user
        account.delete()
        return HttpResponse(status=204)


# Public Route for public profile lookup
@csrf_exempt
@api_view(["POST"])
def get_account(request):
    username = request.data.get("username")
    if not username:
        return JsonResponse({"error": "Username not provided"}, status=400)
    try:
        account = Account.objects.get(username=username)
        # Exclude sensitive fields
        serializer = AccountSerializerClean(account)
        logger.info(f"account: {serializer.data}")
        return JsonResponse(serializer.data)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Account not found"}, status=404)


@csrf_exempt
@api_view(["PUT"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_account(request):
    account = request.user
    data = request.data
    logger.info(f"update_account: {data}")

    serializer = AccountSerializer(account, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=400)


@csrf_exempt
@api_view(["DELETE"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_account(request):
    account = request.user
    account.delete()
    return HttpResponse(status=204)


# Users on the client use Token Auth w/ a generated session Token, not Django Session Auth
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_id(request: Request):
    user = request.user
    if user is None:
        return JsonResponse({"error": "user not found"}, status=404)

    if not hasattr(user, "uuid"):
        return JsonResponse({"error": "user id not found"}, status=404)

    user_id = user.uuid
    return JsonResponse({"user_id": user_id}, status=200)
