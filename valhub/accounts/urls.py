from django.urls import path, include
from rest_framework import routers
from accounts import views

urlpatterns = [
    # path('', include(router.urls)),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    # path('logout', views.logout_view, name='logout'),
    # path('profile/<username>', views.profile, name='profile'),
    path('account/', views.AccountList.as_view()),
    path('account/<int:pk>/', views.AccountDetail.as_view()),
]