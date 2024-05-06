from  django.urls import path

from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('toggle_bluetooth', views.toggle_bluetooth, name='toggle_bluetooth'),
    path('toggle_wifi', views.toggle_wifi, name='toggle_wifi'),
]