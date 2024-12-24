from django.urls import path
from . import views

app_name = 'arp_spoofer'

urlpatterns = [
    path('', views.index, name='index'),
]
