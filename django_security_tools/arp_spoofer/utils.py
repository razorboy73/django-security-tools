import subprocess
import re
import ipaddress
from scapy.all import ARP, Ether, srp

def get_gateway_info():
    """
    Detect the gateway IP address and MAC address for the current network using the `arp` command.

    Returns:
        dict: Dictionary with `ip`, `mac`, and `raw_output` keys, or None if it cannot be determined.
    """
    try:
        result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            return {"error": f"Error executing arp command: {result.stderr}"}

        arp_output = result.stdout
        gateway_match = re.search(r'_gateway\s+\(([\d.]+)\)\s+at\s+([\w:]+)', arp_output, re.IGNORECASE)

        if gateway_match:
            return {
                "ip": gateway_match.group(1),
                "mac": gateway_match.group(2),
                "raw_output": arp_output
            }
        else:
            return {"error": "Gateway IP not found in arp output.", "raw_output": arp_output}

    except FileNotFoundError:
        return {"error": "The arp command is not available on this system."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

def scan_network(ip_range):
    """
    Scans the network for active devices in the specified IP range.

    Args:
        ip_range (str): The IP range to scan in CIDR notation (e.g., '192.168.1.0/24').

    Returns:
        list: List of dictionaries with `ip` and `mac` keys for each discovered device.
    """
    try:
        ip_network = ipaddress.ip_network(ip_range, strict=False)
        arp = ARP(pdst=str(ip_network))
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        result = srp(packet, timeout=2, verbose=False)[0]

        devices = []
        for sent, received in result:
            devices.append({'ip': received.psrc, 'mac': received.hwsrc})
        return devices
    except ValueError as e:
        raise ValueError(f"Invalid IP range: {ip_range}") from e
    except Exception as e:
        raise RuntimeError(f"Error scanning network: {e}") from e
