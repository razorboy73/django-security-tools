import subprocess
import re
from django.shortcuts import render
import logging


# Configure logging to write debug information to the console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_gateway_info():
    """
    Detect the gateway IP address and MAC address for the current network using the `arp` command.

    Returns:
        dict: Dictionary with `ip`, `mac`, and `raw_output` keys, or None if it cannot be determined.
    """
    try:
        # Execute the arp command to list network entries
        result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Log the output and errors for debugging
        logging.debug(f"ARP command stdout: {result.stdout}")
        logging.debug(f"ARP command stderr: {result.stderr}")

        # Check if the command was successful
        if result.returncode != 0:
            logging.error(f"ARP command failed with return code {result.returncode}")
            return {"error": f"Error executing arp command: {result.stderr}"}

        # Parse the output to find the gateway IP and MAC address
        arp_output = result.stdout
        gateway_match = re.search(r'_gateway\s+\(([\d.]+)\)\s+at\s+([\w:]+)', arp_output, re.IGNORECASE)

        if gateway_match:
            return {
                "ip": gateway_match.group(1),  # Captures the gateway IP
                "mac": gateway_match.group(2),  # Captures the MAC address
                "raw_output": arp_output       # Includes the raw ARP command output
            }
        else:
            logging.warning("Gateway IP not found in arp output.")
            return {"error": "Gateway IP not found in arp output.", "raw_output": arp_output}

    except FileNotFoundError:
        logging.error("The arp command is not available on this system.")
        return {"error": "The arp command is not available on this system."}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": f"An error occurred: {e}"}


def index(request):
    gateway_info = None

    if request.method == "POST":
        gateway_info = get_gateway_info()

    return render(request, 'arp_spoofer/index.html', {'gateway_info': gateway_info})
