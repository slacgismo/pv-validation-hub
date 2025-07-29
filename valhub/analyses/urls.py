from django.urls import path

from . import views

urlpatterns = [
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
    path(
        "<int:analysis_id>/update",
        views.update_analysis,
        name="update analysis",
    ),
    path(
        "<int:analysis_id>/leaderboard", views.leaderboard, name="leaderboard"
    ),
    path("create/", views.create_new_analysis, name="create_new_analysis"),
]
