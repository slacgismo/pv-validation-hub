from django.urls import path
from accounts import views

urlpatterns = [
    # path('', include(router.urls)),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("account/public/", views.get_account, name="get_account"),
    path("account/update/", views.update_account, name="update_account"),
    path("account/delete/", views.delete_account, name="delete_account"),
    path("user_id", views.get_user_id, name="get_user_id"),
]
