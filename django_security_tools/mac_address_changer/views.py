from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib import messages
from .models import Interface
import subprocess
import random
import re


def index(request):
    """
    Renders the main page with a list of available network interfaces.
    """
    interfaces = Interface.objects.all()
    return render(request, "mac_address_changer/index.html", {"interfaces": interfaces})

def find_interfaces(request):
    """
    Returns a list of active network interfaces with their current MAC addresses.
    """
    try:
        result = subprocess.check_output(['ifconfig'], stderr=subprocess.STDOUT).decode('utf-8')
        interfaces = []
        regex = r'^(\w+): flags=.*?\n(?:.*\n)*?\s+ether\s+([0-9a-fA-F:]{17})'
        for match in re.finditer(regex, result, re.MULTILINE):
            interfaces.append({'name': match.group(1), 'mac': match.group(2)})

        return JsonResponse({'interfaces': interfaces, 'instructions': "Select an interface to proceed."})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




def validate_mac(mac):
    """
    Validates the MAC address format.
    """
    pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
    return re.match(pattern, mac) is not None


def ensure_interface_up(interface):
    """
    Ensures the specified interface is up.
    """
    try:
        subprocess.run(["ip", "link", "set", interface, "up"], check=True)
        print(f"Interface {interface} is now up.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error bringing up interface {interface}: {e}")


def change_mac_command(interface, mac):
    """
    Changes the MAC address for the specified interface.
    """
    try:
        print(f"Changing MAC address for {interface} to {mac}")

        # Ensure the interface is up
        ensure_interface_up(interface)

        # Bring the interface down
        subprocess.run(["ip", "link", "set", interface, "down"], check=True)

        # Change the MAC address
        subprocess.run(["ip", "link", "set", interface, "address", mac], check=True)

        # Bring the interface back up
        subprocess.run(["ip", "link", "set", interface, "up"], check=True)

        print(f"MAC address for {interface} successfully changed to {mac}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error executing ip command: {e}")



def change_mac(request):
    """
    Changes the MAC address for the specified interface.
    """
    interface_name = request.POST.get("interface")
    new_mac = request.POST.get("mac")

    if not validate_mac(new_mac):
        messages.error(request, f"Invalid MAC address format: {new_mac}. Please try again.")
        return redirect("index")

    try:
        # Get the interface to change
        interface = Interface.objects.get(name=interface_name)

        # Save the original MAC if it's not already saved
        if not interface.original_mac:
            interface.original_mac = interface.mac_address

        # Change the MAC address
        change_mac_command(interface_name, new_mac)

        # Update the MAC address and set last_changed
        interface.mac_address = new_mac
        interface.last_changed = now()
        interface.save()

        # Reset last_changed for all other interfaces
        Interface.objects.exclude(name=interface_name).update(last_changed=None)

        messages.success(
            request,
            f"MAC address for interface '{interface_name}' successfully changed. "
            f"Original MAC: {interface.original_mac}, New MAC: {new_mac}."
        )
    except Interface.DoesNotExist:
        messages.error(request, f"Interface '{interface_name}' not found.")
    except RuntimeError as e:
        messages.error(request, f"Error: {e}")

    return redirect("index")
    """
    Changes the MAC address for the specified interface.
    """
    interface_name = request.POST.get("interface")
    new_mac = request.POST.get("mac")

    if not validate_mac(new_mac):
        messages.error(request, f"Invalid MAC address format: {new_mac}. Please try again.")
        return redirect("index")

    try:
        interface = Interface.objects.get(name=interface_name)
        original_mac = interface.mac_address
        change_mac_command(interface_name, new_mac)
        interface.mac_address = new_mac
        interface.save()

        messages.success(
            request,
            f"MAC address for interface '{interface_name}' successfully changed. "
            f"Original MAC: {original_mac}, New MAC: {new_mac}."
        )
    except Interface.DoesNotExist:
        messages.error(request, f"Interface '{interface_name}' not found.")
    except RuntimeError as e:
        messages.error(request, f"Error: {e}")

    return redirect("index")

def revert_mac(request):
    """
    Reverts the MAC address for the last changed interface to its original value.
    """
    try:
        # Find the last changed interface
        interface = Interface.objects.filter(last_changed__isnull=False).first()

        if not interface:
            raise ValueError("No interface found to revert.")

        if not interface.original_mac:
            raise ValueError(f"Original MAC address not found for interface '{interface.name}'.")

        # Revert the MAC address
        change_mac_command(interface.name, interface.original_mac)

        # Update the database
        interface.mac_address = interface.original_mac
        interface.last_changed = None
        interface.save()

        messages.success(
            request,
            f"Reverted MAC address for interface '{interface.name}' to original value: {interface.original_mac}."
        )
    except ValueError as e:
        messages.error(request, f"Error: {e}")
    except RuntimeError as e:
        messages.error(request, f"Error: {e}")

    return redirect("index")




def generate_mac(request):
    """
    Generates a valid, locally administered MAC address and returns it as a JSON response.
    """
    new_mac = "02:" + ":".join(f"{random.randint(0, 255):02x}" for _ in range(5))
    print(f"Generated MAC address: {new_mac}")
    return JsonResponse({"mac_address": new_mac})
