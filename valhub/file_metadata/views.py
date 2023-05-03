from rest_framework import generics
from .models import FileMetadata
from .serializers import FileMetadataSerializer

class FileMetadataList(generics.ListCreateAPIView):
    queryset = FileMetadata.objects.all()
    serializer_class = FileMetadataSerializer

class FileMetadataDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = FileMetadata.objects.all()
    serializer_class = FileMetadataSerializer
