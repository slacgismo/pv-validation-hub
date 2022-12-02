from django.urls import path, re_path
from rest_framework import routers
from accounts import views

urlpatterns = [
    # path('', include(router.urls)),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('account/', views.AccountList.as_view()),
    # re_path(r'^account\/(?P<pk>.+)$', views.AccountDetail.as_view()),
    path('account/<uuid:pk>/', views.AccountDetail.as_view()),
]