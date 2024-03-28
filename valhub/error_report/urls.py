from django.urls import path
from .views import (
    ErrorReportList,
    ErrorReportDetail,
    ErrorReportLeaderboard,
    ErrorReportPrivateList,
)

urlpatterns = [
    path("error_report/", ErrorReportList.as_view()),
    path("error_report/<int:pk>/", ErrorReportDetail.as_view()),
    path("error_report/private/<int:pk>/", ErrorReportPrivateList.as_view()),
]
