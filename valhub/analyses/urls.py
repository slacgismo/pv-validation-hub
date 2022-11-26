from django.urls import path

from . import views

urlpatterns = [
    path(
        "upload",
        views.create_analysis,
        name="create_analysis",
    ),
]
