# mac_address_changer/utils.py

import re
import subprocess

def validate_mac(mac_address):
    """
    Validates the MAC address format.
    """
    regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return bool(re.match(regex, mac_address))

def change_mac_command(interface_name, new_mac):
    """
    Executes the system command to change the MAC address.
    """
    try:
        subprocess.run(
            ["ifconfig", interface_name, "down"],
            check=True,
        )
        subprocess.run(
            ["ifconfig", interface_name, "hw", "ether", new_mac],
            check=True,
        )
        subprocess.run(
            ["ifconfig", interface_name, "up"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to change MAC address: {e}")
