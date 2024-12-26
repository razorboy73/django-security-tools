from django.urls import path
from . import views

app_name = 'arp_spoofer'  # Define a namespace for this app

urlpatterns = [
    path('', views.index, name='index'),
    path('start_spoofing/', views.start_spoofing, name='start_spoofing'),
    path('stop_spoofing/', views.stop_spoofing, name='stop_spoofing'),
    path('get_packet_count/', views.get_packet_count, name='get_packet_count'),
    path('find_gateway/', views.find_gateway, name='find_gateway'),
    path('scan_network/', views.scan_network, name='scan_network'),

]