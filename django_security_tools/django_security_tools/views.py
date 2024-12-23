# django_security_tools/views.py
from django.shortcuts import render

def home_view(request):
    # Define the applications dynamically for scalability
    applications = [
        {"name": "MAC Address Changer", "url": "mac_address_changer:index"},
        {"name": "Network Scanner", "url": "network_scanner:index"},
    ]
    return render(request, 'home.html', {"applications": applications})