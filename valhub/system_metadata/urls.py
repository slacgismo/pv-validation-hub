from django.urls import path
from .views import SystemMetadataList, SystemMetadataDetail, bulk_systemmetadata_create

urlpatterns = [
    path("systemmetadata/", SystemMetadataList.as_view()),
    path("systemmetadata/<int:pk>/", SystemMetadataDetail.as_view()),
    path("systemmetadata/bulk_create/", bulk_systemmetadata_create),
]
