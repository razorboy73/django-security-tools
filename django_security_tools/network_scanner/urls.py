# network_scanner/urls.py
from django.urls import path
from . import views

app_name = 'network_scanner'

urlpatterns = [
    path('', views.network_scanner_view, name='network_scanner'),
    path('history/', views.scan_history_view, name='scan_history'),
]