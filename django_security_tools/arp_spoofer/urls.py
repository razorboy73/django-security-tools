from django.urls import path
from . import views

app_name = 'arp_spoofer'  # Define a namespace for this app

urlpatterns = [
    path('', views.index, name='index'),
    path('start_spoofing/', views.start_spoofing, name='start_spoofing'),
    path('stop_spoofing/', views.stop_spoofing, name='stop_spoofing'),
]