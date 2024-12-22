from django.shortcuts import render

def home_view(request):
    # List of active applications with their display names and URLs
    applications = [
        {'name': 'MAC Address Changer', 'url': 'mac_address_changer:index'},
        {'name': 'Network Scanner', 'url': 'network_scanner:index'},
    ]
    return render(request, 'home.html', {'applications': applications})
