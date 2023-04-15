from django.urls import path
from .views import SystemMetadataList, SystemMetadataDetail

urlpatterns = [
    path('systemmetadata/', SystemMetadataList.as_view()),
    path('systemmetadata/<int:pk>/', SystemMetadataDetail.as_view()),
]
