from django.urls import path
from .views import GracefulErrorReportList, GracefulErrorReportDetail

urlpatterns = [
    path("gracefulerrorreport/", GracefulErrorReportList.as_view()),
    path("gracefulerrorreport/<int:pk>/", GracefulErrorReportDetail.as_view()),
]
