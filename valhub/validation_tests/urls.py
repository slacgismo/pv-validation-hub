from django.urls import path
from .views import (
    ValidationTestsListAPIView,
    ValidationTestsDetailAPIView,
    ValidationTestsUploadCSV,
)


urlpatterns = [
    path(
        "", ValidationTestsListAPIView.as_view(), name="validation_tests_list"
    ),
    path(
        "<int:pk>/",
        ValidationTestsDetailAPIView.as_view(),
        name="validation_tests_detail",
    ),
    path(
        "upload_csv/",
        ValidationTestsUploadCSV.as_view(),
        name="validation_tests_upload_csv",
    ),
]
