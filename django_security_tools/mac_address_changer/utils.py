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
    Changes the MAC address of the specified network interface.
    """
    try:
        # Take the interface down
        subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'down'], check=True)

        # Clear IP address (optional, depends on your use case)
        subprocess.run(['sudo', 'ip', 'addr', 'flush', 'dev', interface_name], check=True)

        # Change the MAC address
        subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'address', new_mac], check=True)

        # Bring the interface back up
        subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'up'], check=True)

        print(f"Changing MAC address for {interface_name} to {new_mac}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to change MAC address: {e.stderr or e}")

