# network_scanner/views.py
from django.shortcuts import render
from .forms import NetworkScannerForm
from .scanner import scan_network
from .models import ScanLog
import json
import ipaddress
from scapy.all import ARP, Ether, srp

def network_scanner_view(request):
    results = None
    error = None
    if request.method == 'POST':
        form = NetworkScannerForm(request.POST)
        if form.is_valid():
            ip_range = form.cleaned_data['ip_range']
            try:
                results = scan_network(ip_range)
            except ValueError as e:
                error = str(e)
        else:
            error = "Invalid form submission"
    else:
        form = NetworkScannerForm()
    return render(request, 'network_scanner/network_scanner.html', {'form': form, 'results': results, 'error': error})



def scan_history_view(request):
    logs = ScanLog.objects.all()
    return render(request, 'network_scanner/scan_history.html', {'logs': logs})




def scan_network(ip_range):
    print("DEBUG: Calling srp 1...")
    try:
        ip_network = ipaddress.ip_network(ip_range, strict=False)
        print(f"DEBUG: ip_network calculated as {ip_network}")
    except ValueError as e:
        print(f"DEBUG: Invalid IP range: {e}")
        raise ValueError(f"Invalid IP range: {ip_range}") from e

    try:
        arp = ARP(pdst=str(ip_network))
        print(f"DEBUG: ARP created with pdst={arp.pdst}")
    except Exception as e:
        print(f"DEBUG: Error creating ARP object: {e}")
        raise

    try:
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        print(f"DEBUG: Ether created with dst={ether.dst}")
    except Exception as e:
        print(f"DEBUG: Error creating Ether object: {e}")
        raise

    try:
        packet = ether / arp
        print(f"DEBUG: Packet created as {packet.summary()}")
    except Exception as e:
        print(f"DEBUG: Error creating packet: {e}")
        raise

    try:
        print("DEBUG: About to call srp...")
        result = srp(packet, timeout=2, verbose=False)[0]
        print("DEBUG: srp call completed")
    except Exception as e:
        print(f"DEBUG: Error calling srp: {e}")
        raise

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    return devices
