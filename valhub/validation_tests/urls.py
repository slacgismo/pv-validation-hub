from django.urls import path
from .views import ValidationTestsListView, ValidationTestsDetailView


urlpatterns = [
    path('', ValidationTestsListView.as_view(), name='validation_tests_list'),
    path('<int:pk>/', ValidationTestsDetailView.as_view(), name='validation_tests_detail'),
]
