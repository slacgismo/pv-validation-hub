from django.urls import path
from healthcheck.views import healthcheck

urlpatterns = [
    path('healthy/', healthcheck),
    # Add other URL patterns here as needed
]
