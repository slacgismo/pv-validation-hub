from django.urls import path

from . import views

urlpatterns = [
    path(
        "analysis/<int:analysis_id>/submission",
        views.analysis_submission,
        name="analysis_submission",
    ),
    path("analysis/<int:analysis_id>/submission/<int:submission_id>",
        views.submission_detail,
        name="submission_detail",
    ),
    path("user_submission/<int:user_id>",
        views.user_submission,
        name="user_submission",
    ),
]
