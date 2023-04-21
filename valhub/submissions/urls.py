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
    path("analysis/<int:analysis_id>/user_submission/<int:user_id>",
        views.analysis_user_submission,
        name="analysis_user_submission",
    ),
    path("leaderboard", 
         views.leaderboard_update, 
         name="leaderboard_update"),
    path("preload_submissions", 
         views.preload_submissions, 
         name="preload_submissions"),
    path("submission_results/<int:submission_id>",
        views.get_submission_results,
        name="get_submission_results"),
]
