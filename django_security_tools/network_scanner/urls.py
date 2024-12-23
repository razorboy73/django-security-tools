from django.urls import path
from . import views

app_name = 'network_scanner'

urlpatterns = [
    path('', views.index, name='index'),  # Index view handles both form and results
    path('history/', views.scan_history_view, name='scan_history'),  # Scan history endpoint
]

