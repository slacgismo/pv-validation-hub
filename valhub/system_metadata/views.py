from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .models import SystemMetadata
from .serializers import SystemMetadataSerializer

from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated


@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
class SystemMetadataList(ListCreateAPIView):
    queryset = SystemMetadata.objects.all()
    serializer_class = SystemMetadataSerializer


@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
class SystemMetadataDetail(RetrieveUpdateDestroyAPIView):
    queryset = SystemMetadata.objects.all()
    serializer_class = SystemMetadataSerializer


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def bulk_systemmetadata_create(request: Request):
    serializer = SystemMetadataSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
