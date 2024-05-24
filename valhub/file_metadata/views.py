from rest_framework import generics
from .models import FileMetadata
from .serializers import FileMetadataSerializer
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class FileMetadataList(generics.ListCreateAPIView):
    queryset = FileMetadata.objects.all()
    serializer_class = FileMetadataSerializer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class FileMetadataDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FileMetadata.objects.all()
    serializer_class = FileMetadataSerializer
