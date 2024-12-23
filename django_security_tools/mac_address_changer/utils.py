# mac_address_changer/utils.py

import re
import subprocess

def validate_mac(mac_address):
    """
    Validates the MAC address format.
    """
    regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return bool(re.match(regex, mac_address))

def change_mac_command(interface, mac):
    """
    Changes the MAC address for the specified interface.
    """
    try:
        print(f"Changing MAC address for {interface} to {mac}")

        # Bring the interface down
        subprocess.run(["sudo", "ip", "link", "set", interface, "down"], check=True)

        # Change the MAC address
        subprocess.run(["sudo", "ip", "link", "set", interface, "address", mac], check=True)

        # Bring the interface back up
        subprocess.run(["sudo", "ip", "link", "set", interface, "up"], check=True)

        print(f"MAC address for {interface} successfully changed to {mac}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error executing ip command: {e}")

