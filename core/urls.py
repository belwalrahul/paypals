from django.urls import path, include
from core import views

urlpatterns = [
    path('', views.home),
    path('register/', views.callRegisterUserForm),
    path('login/', views.callUserLoginFn),
    path('logout/', views.callUserLogOutFn),
    path('about/', views.about),
    path('add_transaction/', views.add_transaction),
    path('groups/', views.groups),
    path('groups/add', views.add_groups),
    path('add_friend/', views.add_friend),
    path('friends/', views.friends_list),
    path('groups/<int:id>', views.grouppage),
    path('groups/<int:id>/add', views.add_grouptransaction),
    path('account_settings/', views.account_settings),
    path('remove_friend/<int:friend_id>/', views.remove_friend, name='remove_friend'),
    path('delete_transaction/<int:pk>/', views.delete_transaction, name='delete_transaction'),

]