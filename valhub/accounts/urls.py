from django.urls import path, re_path
from rest_framework import routers
from accounts import views

urlpatterns = [
    # path('', include(router.urls)),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('account', views.AccountDetail.as_view()),
]
