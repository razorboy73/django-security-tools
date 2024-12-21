from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import MacAddressHistory, Interface
import subprocess
import random

def index(request):
    interfaces = Interface.objects.all()
    return render(request, "mac_address_changer/index.html", {"interfaces": interfaces})

def generate_mac(request):
    new_mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
    MacAddressHistory.objects.create(mac_address=new_mac)
    return JsonResponse({"mac_address": new_mac})

def change_mac(request):
    interface_name = request.POST.get("interface")
    new_mac = request.POST.get("mac")
    interface = Interface.objects.get(name=interface_name)

    if not validate_mac(new_mac):
        messages.error(request, "Invalid MAC address format.")
        return redirect("index")

    try:
        original_mac = check_interface(interface_name)
        if not interface.original_mac:
            interface.original_mac = original_mac
            interface.save()

        change_mac_command(interface_name, new_mac)
        messages.success(request, f"MAC address changed to {new_mac}.")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("index")

def revert_mac(request):
    interface_name = request.POST.get("interface")
    interface = Interface.objects.get(name=interface_name)

    try:
        if not interface.original_mac:
            raise ValueError("Original MAC address not found.")

        change_mac_command(interface_name, interface.original_mac)
        messages.success(request, f"Reverted back to original MAC: {interface.original_mac}.")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("index")

# Utility functions for subprocess handling
def validate_mac(mac):
    pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
    return re.match(pattern, mac) is not None

def check_interface(interface):
    result = subprocess.check_output(["ifconfig", interface]).decode("utf-8")
    return re.search(r"ether ([0-9a-fA-F:]{17})", result).group(1)

def change_mac_command(interface, mac):
    subprocess.run(["ifconfig", interface, "down"], check=True)
    subprocess.run(["ifconfig", interface, "hw", "ether", mac], check=True)
    subprocess.run(["ifconfig", interface, "up"], check=True)
