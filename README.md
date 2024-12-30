# Django Security Tools

#### Video Demo: <URL HERE>


## Description

**Django Security Tools** is a suite of network security and engineering tools designed to provide network engineers and ethical hackers with a web-based interface for essential network operations. Built on Django, this project combines high-level web frameworks with low-level system operations for seamless and efficient management.

The project includes the following tools:
1. **MAC Address Changer**: A utility for managing and modifying MAC addresses of network interfaces.
2. **Network Scanner**: A tool to discover devices on a network, displaying their IP and MAC addresses.
3. **ARP Spoofer**: A tool to perform ARP spoofing for testing and educational purposes.

---

## Features Overview

### 1. **MAC Address Changer**

1. **View Network Interfaces**:
   - Displays all active network interfaces, their names, and current MAC addresses.
2. **Generate Random MAC Addresses**:
   - Create valid, unique, locally administered MAC addresses with a single click.
3. **Change MAC Addresses**:
   - Modify the MAC address of a selected network interface with input validation.
4. **Revert MAC Addresses**:
   - Automatically identifies the last modified interface and reverts it to its original MAC address.
5. **Track History**:
   - Keeps a history of generated and changed MAC addresses along with timestamps.
6. **User-Friendly Interface**:
   - Includes responsive design, JavaScript interactivity, and real-time alerts for user feedback.

---

### 2. **Network Scanner**

1. **Discover Devices on the Network**:
   - Sends ARP requests to a specified IP range and identifies active devices.
2. **Display IP and MAC Addresses**:
   - Lists the IP and MAC addresses of devices discovered during the scan.
3. **Track Scan History**:
   - Logs IP ranges scanned along with results and timestamps for future reference.
4. **Interactive Scan History Viewer**:
   - Provides a detailed view of past scan results with collapsible data for improved readability.
5. **Intuitive User Interface**:
   - Features simple forms for inputting IP ranges and dynamically updates scan results.

---

### 3. **ARP Spoofer**

1. **Gateway Detection**:
   - Automatically detects and displays the IP and MAC address of the network gateway using the `arp -a` command.
   - Displays the results directly in the UI without page reloads.
2. **Network Device Scanning**:
   - Scans the network to discover connected devices and lists their IP and MAC addresses.
   - Dynamically populates a dropdown list of devices for selection as spoofing targets.
3. **ARP Spoofing**:
   - Spoofs the selected target (victim) and router to enable a man-in-the-middle attack.
   - Enables port forwarding automatically during the spoofing process.
4. **Stop Spoofing**:
   - Stops the spoofing process and restores the original ARP mappings of the target and router.
5. **Real-Time Packet Count**:
   - Displays the number of packets being sent in real-time in the terminal.
6. **Dynamic UI Updates**:
   - Enables/Disables appropriate buttons (e.g., Start/Stop Spoofing) based on the current state.
   - Provides user feedback via alert messages directly on the page.

---

## How to Use Each Tool

### **MAC Address Changer**

1. **View Active Interfaces**:
   - Open the MAC Address Changer page to see all active network interfaces and their MAC addresses.
2. **Generate a New MAC Address**:
   - Click the **Generate** button to create a random MAC address.
3. **Change the MAC Address**:
   - Select an interface, input the new MAC address, and click **Change MAC**.
4. **Revert to Original MAC**:
   - Click the **Revert** button to restore the original MAC address.

---

### **Network Scanner**

1. **Input an IP Range**:
   - Enter the desired IP range in CIDR notation (e.g., `192.168.1.0/24`).
2. **Scan the Network**:
   - Click **Scan Network** to discover devices connected to the specified IP range.
3. **View Results**:
   - The discovered devices are displayed with their IP and MAC addresses.
4. **Track History**:
   - View past scan results on the **Scan History** page.

---

### **ARP Spoofer**

1. **Find Gateway**:
   - Click the **Find Gateway** button to detect and display the router’s IP and MAC address.
2. **Scan Network**:
   - Click the **Scan Network** button to discover all devices connected to the network.
   - View the discovered devices in a dynamically populated table.
3. **Start Spoofing**:
   - Select a target device from the dropdown list.
   - Click the **Start Spoofing** button to initiate spoofing between the selected target and the gateway.
   - Port forwarding is enabled automatically during spoofing.
4. **Stop Spoofing**:
   - Click the **Stop Spoofing** button to end the spoofing process and restore ARP tables.

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/razorboy73/django-security-tools
cd django-security-tools
```

### 2. Set Up a Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

---

## Testing the Application

### Run Unit Tests
To ensure the application is functioning correctly, execute:
```bash
python manage.py test
```

### Manual Testing
1. **MAC Address Changer**:
   - View, modify, and revert MAC addresses for active network interfaces.
2. **Network Scanner**:
   - Input an IP range and verify the discovered devices in the results.
3. **ARP Spoofer**:
   - Detect the gateway, scan the network, select a target, and initiate spoofing.
   - Verify the real-time spoofing functionality and stop spoofing to restore ARP tables.

---

## Notes on Security and Ethical Usage

**This tool is intended for educational and testing purposes only. Unauthorized use on networks you do not own or have explicit permission to test is illegal and unethical. Always follow ethical hacking principles and obtain proper authorization before using this tool.**

---

## Recent Updates

- Added dropdown-based target selection for ARP Spoofer.
- Enabled automatic port forwarding during spoofing.
- Enhanced UI feedback and error handling across all tools.
- Improved real-time feedback for ARP Spoofing. 

