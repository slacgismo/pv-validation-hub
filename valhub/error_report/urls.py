from django.urls import path

from . import views
from .views import ErrorReportList, ErrorReportDetail

urlpatterns = [
    path("error_report", views.ErrorReport, name="error_report"),
    path(
        "error_report/list",
        ErrorReportList.as_view(),
        name="error_report_list",
    ),
    path("error_report/new", views.ErrorReportNew, name="error_report_new"),
    path(
        "error_report/<int:pk>",
        ErrorReportDetail.as_view(),
        name="error_report_detail",
    ),
    path(
        "error_report/private/<int:pk>",
        views.ErrorReportPrivateList,
        name="error_report_private_list",
    ),
]
