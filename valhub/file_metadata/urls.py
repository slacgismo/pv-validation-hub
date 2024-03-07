from django.urls import path
from .views import FileMetadataList, FileMetadataDetail

urlpatterns = [
    path("filemetadata/", FileMetadataList.as_view()),
    path("filemetadata/<int:pk>/", FileMetadataDetail.as_view()),
]
