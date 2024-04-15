from django.urls import path

from . import views

urlpatterns = [
    path("error_report", views.ErrorReportList, name="error_report_list"),
    path("error_report/new", views.ErrorReportNew, name="error_report_new"),
    path(
        "error_report/<int:pk>",
        views.ErrorReportDetail,
        name="error_report_detail",
    ),
    path(
        "error_report/private/<int:pk>",
        views.ErrorReportPrivateList,
        name="error_report_private_list",
    ),
]
