from django.urls import path, include
from rest_framework import routers
from . import views

urlpatterns = [
    # path('', include(router.urls)),
    # path('register', views.register, name='register'),
    # path('login', views.login_view, name='login'),
    # path('logout', views.logout_view, name='logout'),
    # path('profile/<username>', views.profile, name='profile'),
    path('account/', views.account_list),
    path('account/<int:pk>/', views.account_detail),
]