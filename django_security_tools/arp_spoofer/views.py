import subprocess
import re
from django.shortcuts import render
from django.http import JsonResponse
from .forms import NetworkScannerForm
from scapy.all import ARP, Ether, srp
import ipaddress
import logging
from .utils import get_gateway_info, scan_network
from django.shortcuts import render
from .utils import get_gateway_info, scan_network

def index(request):
    """
    Handles the main index view, including gateway detection and network scanning.
    """
    gateway_info = None
    scan_results = None
    error = None

    if request.method == "POST":
        # Detect Gateway
        if "detect_gateway" in request.POST:
            gateway_info = get_gateway_info()

        # Scan Network
        elif "scan_network" in request.POST:
            # Ensure gateway info is fetched before scanning
            gateway_info = get_gateway_info()
            if gateway_info and not gateway_info.get("error"):
                ip_range = gateway_info["ip"] + "/24"  # Assuming /24 CIDR for the scan
                try:
                    scan_results = scan_network(ip_range)
                except Exception as e:
                    error = f"Error during network scan: {e}"

    return render(request, "arp_spoofer/index.html", {
        "gateway_info": gateway_info,
        "scan_results": scan_results,
        "error": error,
    })
