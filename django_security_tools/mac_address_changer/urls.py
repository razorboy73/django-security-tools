from django.urls import path
from . import views

app_name = 'mac_address_changer'

urlpatterns = [
    path('', views.index, name='index'),
    path('find-interfaces/', views.find_interfaces, name='find_interfaces'),
    path('generate/', views.generate_mac, name='generate_mac'),
    path('change/', views.change_mac, name='change_mac'),
    path('revert/', views.revert_mac, name='revert_mac'),  # Ensure this is present
]