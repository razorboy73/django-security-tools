from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import MacAddressHistory, Interface
import subprocess
import random
import re

def index(request):
    interfaces = Interface.objects.all()
    return render(request, "mac_address_changer/index.html", {"interfaces": interfaces})


def find_interfaces(request):
    """
    Returns a list of active network interfaces with their current MAC addresses.
    Updates the Interface table in the database.
    """
    try:
        # Get the output of ifconfig
        result = subprocess.check_output(['ifconfig'], stderr=subprocess.STDOUT).decode('utf-8')

        # Log the raw output for debugging
        print("Raw ifconfig output:\n", result)

        # Parse interface names and MAC addresses
        interfaces = []
        # Updated regex: Matches all interfaces and optionally captures MAC addresses
        regex = r'^(\w+): flags=.*?\n(?:.*\n)*?(?:\s+ether\s+([0-9a-fA-F:]{17}))?'

        for match in re.finditer(regex, result, re.MULTILINE):
            interface_name = match.group(1)  # Extract interface name
            mac_address = match.group(2) if match.group(2) else "No MAC Address"  # Extract MAC or set as "No MAC Address"

            # Update or create the Interface in the database
            Interface.objects.update_or_create(
                name=interface_name,
                defaults={'original_mac': mac_address, 'mac_address': mac_address}
            )
            interfaces.append({'name': interface_name, 'mac': mac_address})

        # Log the parsed interfaces for debugging
        print("Parsed interfaces:", interfaces)

        # User instructions
        instructions = "Click on a network interface below to select it for MAC address changes."

        return JsonResponse({'interfaces': interfaces, 'instructions': instructions})

    except subprocess.CalledProcessError as e:
        error_message = f"Error fetching interfaces: {str(e)}"
        print(error_message)  # Log the error
        return JsonResponse({'error': error_message}, status=500)

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)  # Log the error
        return JsonResponse({'error': error_message}, status=500)
    
    
def generate_mac(request):
    new_mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
    MacAddressHistory.objects.create(mac_address=new_mac)
    return JsonResponse({"mac_address": new_mac})

def change_mac(request):
    interface_name = request.POST.get("interface")
    new_mac = request.POST.get("mac")

    print(f"POST data - interface: {interface_name}, mac: {new_mac}")  # Debugging

    if not interface_name:
        messages.error(request, "No interface selected.")
        return redirect("index")

    try:
        interface = Interface.objects.get(name=interface_name)
    except Interface.DoesNotExist:
        messages.error(request, f"Interface '{interface_name}' not found in the database.")
        return redirect("index")

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
