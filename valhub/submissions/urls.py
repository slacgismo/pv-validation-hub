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
    path("analysis/<int:analysis_id>/change_submission_status/<int:submission_id>",
        views.change_submission_status,
        name="change_submission_status",
    ),
    path("analysis/<int:analysis_id>/update_submission_result/<int:submission_id>",
        views.update_submission_result,
        name="update_submission_result",
    ),
    path("user_submission/<int:user_id>",
        views.user_submission,
        name="user_submission",
    ),
    path("analysis/<int:analysis_id>/user_submission",
        views.analysis_user_submission,
        name="analysis_user_submission",
    ),
    path("leaderboard", 
         views.leaderboard_update, 
         name="leaderboard_update"),
]
