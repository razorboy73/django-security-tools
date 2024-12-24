import subprocess
import re
from django.shortcuts import render
from django.http import JsonResponse
from .forms import NetworkScannerForm
from scapy.all import ARP, Ether, srp
import ipaddress
import logging
from django.contrib import messages
from .utils import get_gateway_info, scan_network, spoof_target


def index(request):
    gateway_info = None
    scan_results = None
    error = None

    if request.method == "POST":
        if "detect_gateway" in request.POST:
            gateway_info = get_gateway_info()
            if gateway_info.get("error"):
                messages.error(request, gateway_info["error"])
            else:
                messages.success(request, f"Gateway detected: {gateway_info['ip']} ({gateway_info['mac']})")
        elif "scan_network" in request.POST:
            gateway_info = get_gateway_info()
            if gateway_info and not gateway_info.get("error"):
                ip_range = gateway_info["ip"] + "/24"
                try:
                    scan_results = scan_network(ip_range)
                    messages.success(request, "Network scan completed successfully.")
                except Exception as e:
                    error = f"Error during network scan: {e}"
                    messages.error(request, error)
            else:
                error = gateway_info.get("error", "Error detecting gateway.")
                messages.error(request, error)
        elif "spoof_target" in request.POST:
            target_data = request.POST.get("target")
            gateway_info = get_gateway_info()
            if gateway_info and not gateway_info.get("error") and target_data:
                try:
                    victim_ip, victim_mac = target_data.split("|")
                    spoof_details = spoof_target(victim_ip, victim_mac, gateway_info["ip"])
                    messages.success(
                        request,
                        f"The computer with the MAC address {spoof_details['hwsrc']} started spoofing {spoof_details['pdst']} ({spoof_details['hwdst']}), "
                        f"claiming to be {spoof_details['psrc']}."
                    )
                except Exception as e:
                    error = f"Error during spoofing: {e}"
                    messages.error(request, error)
            else:
                messages.error(request, "Please select a target and ensure the gateway is detected.")


    return render(request, "arp_spoofer/index.html", {
        "gateway_info": gateway_info,
        "scan_results": scan_results,
        "error": error,
    })