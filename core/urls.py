from django.urls import path, include
from core import views

urlpatterns = [
    path('', views.home),
    path('register/', views.callRegisterUserForm),
    path('login/', views.callUserLoginFn),
    path('logout/', views.callUserLogOutFn),
    path('about/', views.about),
    path('add_transaction/', views.add_transaction),
    path('groups/', views.groups)
]