from rest_framework import generics
from .models import SystemMetadata
from .serializers import SystemMetadataSerializer

class SystemMetadataList(generics.ListCreateAPIView):
    queryset = SystemMetadata.objects.all()
    serializer_class = SystemMetadataSerializer

class SystemMetadataDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SystemMetadata.objects.all()
    serializer_class = SystemMetadataSerializer
