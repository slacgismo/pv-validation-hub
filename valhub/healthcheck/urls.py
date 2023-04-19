from django.urls import path
from healthcheck.views import healthcheck

urlpatterns = [
    path('', healthcheck),
    # Add other URL patterns here as needed
]
