import subprocess
import re
from django.shortcuts import render
from django.http import JsonResponse
from .forms import NetworkScannerForm
from scapy.all import ARP, Ether, srp
import ipaddress
import logging
from django.contrib import messages
from .utils import get_gateway_info, scan_network, spoof_both, start_spoofing_continuous, stop_spoofing, enable_port_forwarding



def index(request):
    # Initialize spoofing status in the session if not already set
    if "spoofing_status" not in request.session:
        request.session["spoofing_status"] = False

    gateway_info = None
    scan_results = None
    error = None
    spoofing_status = request.session["spoofing_status"]  # Retrieve spoofing status from session

    if request.method == "POST":
        if "detect_gateway" in request.POST:
            # Detect Gateway Action
            gateway_info = get_gateway_info()
            if gateway_info.get("error"):
                messages.error(request, gateway_info["error"])
            else:
                messages.success(request, f"Gateway detected: {gateway_info['ip']} ({gateway_info['mac']})")

        elif "scan_network" in request.POST:
            # Scan Network Action
            gateway_info = get_gateway_info()
            if gateway_info and not gateway_info.get("error"):
                ip_range = gateway_info["ip"] + "/24"
                try:
                    scan_results = scan_network(ip_range)
                    request.session["scan_results"] = scan_results  # Store scan results in session
                    messages.success(request, f"Network scan completed successfully for {ip_range}.")
                except Exception as e:
                    error = f"Error during network scan: {e}"
                    messages.error(request, error)
            else:
                error = gateway_info.get("error", "Error detecting gateway.")
                messages.error(request, error)

        elif "start_spoofing" in request.POST:
            # Start Spoofing Action
            target_data = request.POST.get("target")
            gateway_info = get_gateway_info()
            if gateway_info and not gateway_info.get("error") and target_data:
                try:
                    victim_ip, victim_mac = target_data.split("|")
                    gateway_ip = gateway_info["ip"]
                    gateway_mac = gateway_info["mac"]

                    start_spoofing_continuous(victim_ip, victim_mac, gateway_ip, gateway_mac)
                    request.session["spoofing_status"] = True  # Set spoofing status to active
                    spoofing_status = True
                    messages.success(
                        request,
                        f"Spoofing started. You are impersonating the gateway ({gateway_ip}) for the victim ({victim_ip})."
                    )
                except Exception as e:
                    error = f"Error during spoofing: {e}"
                    messages.error(request, error)
            else:
                messages.error(request, "Please select a target and ensure the gateway is detected.")

        elif "stop_spoofing" in request.POST:
            # Stop Spoofing Action
            stop_spoofing()
            request.session["spoofing_status"] = False  # Reset spoofing status
            spoofing_status = False
            messages.success(request, "Spoofing stopped.")

    # Clear scan results on a GET request
    elif request.method == "GET":
        request.session.pop("scan_results", None)

    return render(request, "arp_spoofer/index.html", {
        "gateway_info": gateway_info,
        "scan_results": request.session.get("scan_results"),  # Retrieve scan results from session
        "error": error,
        "spoofing_status": spoofing_status,
    })
