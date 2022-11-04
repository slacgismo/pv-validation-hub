from django.urls import path
from . import views

urlpatterns = [
    path('sign_in', views.sign_in, name='sign_in'),
    path('register', views.register, name='register'),
    path('log_in', views.log_in, name='log_in'),
    path('home', views.home, name='home'),
]