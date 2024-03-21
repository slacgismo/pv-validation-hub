from django.urls import path
from .views import ErrorReportList, ErrorReportDetail

urlpatterns = [
    path("error_report/", ErrorReportList.as_view()),
    path("error_report/<int:pk>/", ErrorReportDetail.as_view()),
]
