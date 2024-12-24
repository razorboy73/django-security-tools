from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib import messages
from mac_address_changer.models import Interface
from .utils import change_mac_command, validate_mac
import subprocess
import re
import random
import json


def index(request):
    """
    Renders the main page with a list of available network interfaces.
    """
    interfaces = Interface.objects.all()
    return render(request, "mac_address_changer/index.html", {"interfaces": interfaces})


def check_nic_status(request):
    """
    Checks the status of all network interfaces using 'ip link show'.
    Identifies interfaces that are 'down' or 'dormant' and includes their MAC addresses.
    """
    try:
        # Run the 'ip link show' command to list all network interfaces
        result = subprocess.run(['ip', 'link', 'show'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Debugging: Log the command's raw output
        print("DEBUG: 'ip link show' output:\n", result.stdout)
        print("DEBUG: 'ip link show' errors:\n", result.stderr)

        if result.returncode != 0:
            raise RuntimeError(f"Error executing 'ip link show': {result.stderr}")

        interfaces = []
        lines = result.stdout.splitlines()
        current_interface = {}

        for line in lines:
            # Match the interface name
            name_match = re.match(r'^\d+:\s+([\w\d@]+):', line)
            if name_match:
                if current_interface:
                    interfaces.append(current_interface)
                current_interface = {
                    "name": name_match.group(1),
                    "status": "unknown",
                    "mac": "unknown",
                }
                continue

            # Match the interface status
            if "state" in line and current_interface:
                if "UP" in line:
                    current_interface["status"] = "up"
                elif "DOWN" in line:
                    current_interface["status"] = "down"
                elif "DORMANT" in line:
                    current_interface["status"] = "dormant"

            # Match the MAC address
            mac_match = re.search(r'link/ether\s+([0-9a-fA-F:]{17})', line)
            if mac_match and current_interface:
                current_interface["mac"] = mac_match.group(1)

        # Append the last interface
        if current_interface:
            interfaces.append(current_interface)

        # Debugging: Log parsed interfaces
        print("DEBUG: Parsed NIC statuses with MAC:\n", interfaces)

        return JsonResponse({"interfaces": interfaces})

    except Exception as e:
        print(f"DEBUG: Error in check_nic_status: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def bring_nic_up(request):
    """
    Brings a specific network interface back up using 'sudo ip link set <interface_name> up'.
    """
    print(f"DEBUG: Received request body: {request.body}")

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        interface_name = data.get("interface")

        if not interface_name:
            return JsonResponse({"error": "Interface name is required."}, status=400)

        result = subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'up'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        print("DEBUG: 'ip link set <interface> up' output:\n", result.stdout)
        print("DEBUG: 'ip link set <interface> up' errors:\n", result.stderr)

        if result.returncode != 0:
            raise RuntimeError(f"Error bringing interface {interface_name} up: {result.stderr.strip()}")

        return JsonResponse({"message": f"Interface {interface_name} is now up."})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def find_interfaces(request):
    """
    Returns a list of active network interfaces with their current MAC addresses.
    """
    try:
        result = subprocess.check_output(['ifconfig'], stderr=subprocess.STDOUT).decode('utf-8')
        print("DEBUG: Raw ifconfig output:\n", result)

        interfaces = []
        current_interface = None

        interface_regex = r'^\s*([\w\d]+):'
        mac_regex = r'ether\s+([0-9a-fA-F:]{17})'

        lines = result.split("\n")
        print("DEBUG: Split ifconfig output into lines.")

        for line in lines:
            interface_match = re.match(interface_regex, line)
            if interface_match:
                current_interface = interface_match.group(1).strip()
                print(f"DEBUG: Found interface: {current_interface}")
                continue

            mac_match = re.search(mac_regex, line)
            if mac_match and current_interface:
                mac_address = mac_match.group(1).strip()
                print(f"DEBUG: Found MAC address for {current_interface}: {mac_address}")

                if current_interface.lower() == "lo":
                    print(f"DEBUG: Skipping loopback interface: {current_interface}")
                    current_interface = None
                    continue

                try:
                    interface, created = Interface.objects.get_or_create(name=current_interface)
                    if created or interface.mac_address != mac_address:
                        interface.mac_address = mac_address
                        interface.save()
                except Exception as e:
                    print(f"DEBUG: Error handling interface {current_interface}: {str(e)}")

                interfaces.append({"name": current_interface, "mac": mac_address})
                current_interface = None

        print(f"DEBUG: Final extracted interfaces: {interfaces}")
        return JsonResponse({"interfaces": interfaces, "instructions": "Select an interface to proceed."})

    except Exception as e:
        print(f"DEBUG: Error in find_interfaces: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def change_mac(request):
    """
    Changes the MAC address for the specified interface.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    # Debug: Log the received request body
    print("DEBUG: Received request body:", request.body)

    try:
        # Parse the JSON body
        data = json.loads(request.body)
        interface_name = data.get("interface")
        new_mac = data.get("mac")

        if not interface_name or not new_mac:
            return JsonResponse({"error": "Both interface and MAC address are required."}, status=400)

        if not validate_mac(new_mac):
            return JsonResponse({"error": f"Invalid MAC address format: {new_mac}."}, status=400)

        # Fetch the interface from the database
        interface = Interface.objects.get(name=interface_name)

        # Retrieve the old MAC address
        old_mac = interface.mac_address

        # Save the original MAC if not already saved
        if not interface.original_mac:
            interface.original_mac = old_mac

        # Change the MAC address
        change_mac_command(interface_name, new_mac)

        # Update the database record
        interface.mac_address = new_mac
        interface.last_changed = now()
        interface.save()

        # Reset `last_changed` for all other interfaces
        Interface.objects.exclude(name=interface_name).update(last_changed=None)

        # Return a detailed success message
        return JsonResponse({
            "message": (
                f"MAC address for interface '{interface_name}' successfully changed. "
                f"Old MAC: {old_mac}, New MAC: {new_mac}."
            ),
            "interface": interface_name,
            "old_mac": old_mac,
            "new_mac": new_mac,
        })
    except Interface.DoesNotExist:
        return JsonResponse({"error": f"Interface '{interface_name}' not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def revert_mac(request):
    """
    Reverts the MAC address for the last changed interface to its original value.
    """
    try:
        interface = Interface.objects.filter(last_changed__isnull=False).first()

        if not interface:
            return JsonResponse({"error": "No interface found to revert."}, status=404)

        if not interface.original_mac:
            return JsonResponse({"error": f"Original MAC address not found for interface '{interface.name}'."}, status=404)

        change_mac_command(interface.name, interface.original_mac)

        interface.mac_address = interface.original_mac
        interface.last_changed = None
        interface.save()

        return JsonResponse({
            "message": f"Reverted MAC address for interface '{interface.name}' to original value: {interface.original_mac}."
        })
    except RuntimeError as e:
        return JsonResponse({"error": f"Error: {e}"}, status=500)


def generate_mac(request):
    """
    Generates a random MAC address.
    """
    mac_address = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
    return JsonResponse({'mac_address': mac_address})
