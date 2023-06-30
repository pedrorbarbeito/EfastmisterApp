from django.urls import path
from django.contrib.auth import views as auth_views

import UsersApp.views

urlpatterns = [
    path('register/', UsersApp.views.register, name="register"),
    path('registerpage/', UsersApp.views.vistaRegister, name="registerpage"),
    path('login/', UsersApp.views.loginUser, name="login"),
    path('loginpage/', UsersApp.views.vistaLogin, name="loginpage"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('perfil/', UsersApp.views.perfil, name='perfil'),
    path('editar-perfil/', UsersApp.views.editar_perfil, name='editar_perfil'),
    path('eliminar-perfil/', UsersApp.views.eliminar_perfil, name='eliminar_perfil'),
    path('error-perfil/', UsersApp.views.eliminar_perfil, name='error_perfil'),
]
