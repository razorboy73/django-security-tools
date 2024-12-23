
from django.urls import path
from . import views

app_name = 'network_scanner'  # This defines the app namespace

urlpatterns = [
    path('', views.index, name='index'),  # Default index view
    path('scan/', views.network_scanner_view, name='scan_network'),  # Use the correct view
    path('history/', views.scan_history_view, name='scan_history'),  # Endpoint for history
]
