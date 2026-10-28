
from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    path("dashboard/", views.dashboard_view, name="dashboard"),

    path("products/", views.product_list_view, name="product_list"),
    path("products/add/", views.product_create_view, name="product_create"),

    path("products/<int:pk>/edit/", views.product_edit_view, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete_view, name="product_delete"),

]
