from django.urls import path
from . import views

app_name = 'arp_spoofer'

urlpatterns = [
    path('', views.index, name='index'),
    path('get_packet_count/', views.get_packet_count_view, name='get_packet_count'),

]
