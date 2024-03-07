from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SystemMetadata
from .serializers import SystemMetadataSerializer


class SystemMetadataList(generics.ListCreateAPIView):
    queryset = SystemMetadata.objects.all()
    serializer_class = SystemMetadataSerializer


class SystemMetadataDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SystemMetadata.objects.all()
    serializer_class = SystemMetadataSerializer


@api_view(["POST"])
def bulk_systemmetadata_create(request):
    serializer = SystemMetadataSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
