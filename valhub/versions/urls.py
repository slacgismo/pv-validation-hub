from django.urls import path
from .views import (
    VersionsListCreateView,
    VersionsDetailView,
    GetPythonVersions,
)

urlpatterns = [
    path("", VersionsListCreateView.as_view(), name="versions-list-create"),
    path("<int:pk>/", VersionsDetailView.as_view(), name="versions-detail"),
    path("python/", GetPythonVersions, name="get-python-versions"),
]
