from django.urls import path

from . import views

urlpatterns = [
    path(
        "upload",
        views.create_analysis,
        name="create_analysis",
    ),
    path(
        "home",
        views.list_analysis,
        name="list_analysis",
    ),
    path(
        "<int:analysis_id>",
        views.analysis_detail,
        name="analysis_detail",
    ),
]
