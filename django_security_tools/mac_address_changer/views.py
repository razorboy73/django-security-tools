from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib import messages
from mac_address_changer.models import Interface
from .utils import change_mac_command, validate_mac
import subprocess
import re
import random


def index(request):
    """
    Renders the main page with a list of available network interfaces.
    """
    interfaces = Interface.objects.all()
    return render(request, "mac_address_changer/index.html", {"interfaces": interfaces})


def find_interfaces(request):
    """
    Returns a list of active network interfaces with their current MAC addresses.
    This function skips the loopback interface (lo).
    """
    try:
        # Execute the ifconfig command and decode the output
        result = subprocess.check_output(['ifconfig'], stderr=subprocess.STDOUT).decode('utf-8')
        print("DEBUG: Raw ifconfig output:\n", result)

        interfaces = []
        current_interface = None

        # Regular expressions for interface name and MAC address
        interface_regex = r'^\s*([\w\d]+):'  # Matches lines starting with the interface name
        mac_regex = r'ether\s+([0-9a-fA-F:]{17})'  # Matches MAC addresses

        # Split the output into lines for processing
        lines = result.split("\n")
        print("DEBUG: Split ifconfig output into lines.")

        for line in lines:
            # Check if the line contains an interface name
            interface_match = re.match(interface_regex, line)
            if interface_match:
                current_interface = interface_match.group(1).strip()
                print(f"DEBUG: Found interface: {current_interface}")
                continue

            # Check if the line contains a MAC address
            mac_match = re.search(mac_regex, line)
            if mac_match and current_interface:
                mac_address = mac_match.group(1).strip()
                print(f"DEBUG: Found MAC address for {current_interface}: {mac_address}")

                # Skip the loopback interface
                if current_interface.lower() == "lo":
                    print(f"DEBUG: Skipping loopback interface: {current_interface}")
                    current_interface = None
                    continue

                # Save the interface and MAC to the database
                try:
                    interface, created = Interface.objects.get_or_create(name=current_interface)
                    print(f"DEBUG: Interface retrieved or created: {interface.name}, created: {created}")

                    # Update the MAC address if newly created or it has changed
                    if created or interface.mac_address != mac_address:
                        print(f"DEBUG: Updating MAC address for {current_interface}: {interface.mac_address} -> {mac_address}")
                        interface.mac_address = mac_address
                        interface.save()
                    else:
                        print(f"DEBUG: No changes needed for interface: {current_interface}")
                except Exception as e:
                    print(f"DEBUG: Error handling interface {current_interface}: {str(e)}")

                # Append the interface to the response list
                interfaces.append({"name": current_interface, "mac": mac_address})
                current_interface = None  # Reset for the next interface

        # Debugging final extracted interfaces
        print(f"DEBUG: Final extracted interfaces: {interfaces}")

        # Debugging database state after update
        print("DEBUG: Database state after update:")
        for interface in Interface.objects.all():
            print(f"Name: {interface.name}, MAC: {interface.mac_address}")

        # Return the extracted interfaces as JSON response
        return JsonResponse({"interfaces": interfaces, "instructions": "Select an interface to proceed."})

    except Exception as e:
        # Log and return any errors encountered during the process
        print(f"DEBUG: Error in find_interfaces: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def change_mac(request):
    """
    Changes the MAC address for the specified interface.
    """
    interface_name = request.POST.get("interface")
    new_mac = request.POST.get("mac")

    # Debugging: Log received values
    print("DEBUG: interface_name received:", interface_name)
    print("DEBUG: All interfaces in DB:", [i.name for i in Interface.objects.all()])

    if not validate_mac(new_mac):
        messages.error(request, f"Invalid MAC address format: {new_mac}. Please try again.")
        return redirect("mac_address_changer:index")

    try:
        # Fetch the interface from the database
        interface = Interface.objects.get(name=interface_name)

        # Save the original MAC if not already saved
        if not interface.original_mac:
            interface.original_mac = interface.mac_address

        # Change the MAC address
        change_mac_command(interface_name, new_mac)

        # Update the database record
        interface.mac_address = new_mac
        interface.last_changed = now()
        interface.save()

        # Reset `last_changed` for all other interfaces
        Interface.objects.exclude(name=interface_name).update(last_changed=None)

        # Success message
        messages.success(
            request,
            f"MAC address for interface '{interface_name}' successfully changed. "
            f"Original MAC: {interface.original_mac}, New MAC: {new_mac}."
        )
    except Interface.DoesNotExist:
        # Interface not found in the database
        messages.error(request, f"Interface '{interface_name}' not found.")
    except RuntimeError as e:
        # Error occurred during the MAC address change
        messages.error(request, f"Error: {e}")

    # Redirect to the index page
    return redirect("mac_address_changer:index")


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

    return redirect('mac_address_changer:index')


def generate_mac(request):
    """
    Generates a random MAC address.
    """
    mac_address = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
    return JsonResponse({'mac_address': mac_address})
