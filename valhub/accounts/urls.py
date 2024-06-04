from django.urls import path
from accounts import views

urlpatterns = [
    # path('', include(router.urls)),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("account", views.AccountDetail.as_view()),
    path("user_id", views.get_user_id, name="get_user_id"),
]
