from django.urls import path

from . import views

urlpatterns = [
    path(
        "analysis/<int:analysis_id>/submission",
        views.analysis_submission,
        name="analysis_submission",
    ),
    path(
        "submission/<int:submission_id>",
        views.submission_detail,
        name="submission_detail",
    ),
    path(
        "change_submission_status/<int:submission_id>",
        views.change_submission_status,
        name="change_submission_status",
    ),
    path(
        "update_submission_result/<int:submission_id>",
        views.update_submission_result,
        name="update_submission_result",
    ),
    path(
        "update_submission_name/<int:user_id>/<int:submission_id>",
        views.update_submission_name,
        name="update_submission_name",
    ),
    path(
        "archive_submission/<int:user_id>/<int:submission_id>",
        views.archive_submission,
        name="archive_submission",
    ),
    path(
        "user_submission/<int:user_id>",
        views.user_submission,
        name="user_submission",
    ),
    path(
        "analysis/<int:analysis_id>/user_submission",
        views.analysis_user_submission,
        name="analysis_user_submission",
    ),
    path("leaderboard", views.leaderboard_update, name="leaderboard_update"),
    path(
        "preload_submissions",
        views.preload_submissions,
        name="preload_submissions",
    ),
    path(
        "submission_results/<int:submission_id>",
        views.get_submission_results,
        name="get_submission_results",
    ),
    path(
        "user/<int:user_id>/submissions/<int:analysis_id>",
        views.get_user_submissions,
        name="get_user_submissions",
    ),
]
