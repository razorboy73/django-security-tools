from django.shortcuts import render

def home_view(request):
    applications = [
        {"name": "MAC Address Changer", "url": "mac_address_changer:index"},
        {"name": "Network Scanner", "url": "network_scanner:index"},
        {"name": "ARP Spoofer", "url": "arp_spoofer:index"},
       
    ]
    return render(request, 'home.html', {"applications": applications})
