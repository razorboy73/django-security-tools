Here's the updated **README.md** with the addition of the **Network Scanner** application:

---

# Django Security Tools

#### Video Demo: <URL HERE>

---

## Description

**Django Security Tools** is a suite of network security and engineering tools designed to provide network engineers with a web-based interface for essential network operations. Built on Django, this project combines high-level web frameworks with low-level system operations for seamless and efficient management.

The project currently includes the following tools:
1. **MAC Address Changer**: A utility for managing and modifying MAC addresses of network interfaces.
2. **Network Scanner**: A tool to discover devices on a network, displaying their IP and MAC addresses.

---

## Features of **MAC Address Changer**

1. **View Network Interfaces**:
   - Displays all active network interfaces, their names, and current MAC addresses.
2. **Generate Random MAC Addresses**:
   - Create valid, unique, locally administered MAC addresses with a single click.
3. **Change MAC Addresses**:
   - Modify the MAC address of a selected network interface with input validation.
4. **Revert MAC Addresses**:
   - Automatically identifies the last modified interface and reverts it to its original MAC address.
5. **Track History**:
   - Keeps a history of generated MAC addresses along with timestamps.
6. **User-Friendly Interface**:
   - Includes responsive design, JavaScript interactivity, and real-time alerts for user feedback.

---

## Features of **Network Scanner**

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

## Recent Updates

- **Added Network Scanner Tool**:
  - Integrated ARP-based network scanning with a web interface.
  - Tracks and logs scan results in the database for historical reference.
  - Developed an interactive scan history viewer with collapsible details.
- **Enhanced Revert Functionality in MAC Address Changer**:
  - Automatically reverts the last modified interface without requiring manual input.
- **Improved Error Handling**:
  - Validates MAC address formats, ensures interfaces are up before modifications, and handles command execution errors gracefully.

---

## Distinctiveness and Complexity

### Distinctiveness

This project uniquely integrates operating system-level network operations with Django, offering a high-level abstraction for low-level commands. Unlike traditional Django applications that focus on database CRUD operations or static content management, this project executes real-time system-level modifications and network scans, bridging the gap between web development and network engineering.

---

### Complexity

1. **System-Level Command Execution**:
   - Executes commands like `ifconfig`, `ip link`, and ARP requests securely using Python libraries such as `subprocess` and `scapy`.
2. **Database-Driven State Management**:
   - Tracks network operations and scan history with fields for `original_mac`, `mac_address`, `ip_range`, and `results`.
3. **Dynamic Frontend Interactions**:
   - Utilizes AJAX for real-time data updates and JavaScript for dynamic UI changes.
4. **Robust Validation**:
   - Ensures valid MAC addresses and IP ranges before executing operations.
5. **Reversibility and History Tracking**:
   - Tracks and reverts MAC address changes and logs network scans for future reference.

---

## File Contents

### Project Root

- **`.gitignore`**: Specifies files to be excluded from version control, such as `db.sqlite3` and `__pycache__`.
- **`README.md`**: Comprehensive project documentation.
- **`requirements.txt`**: Lists Python dependencies required for the project.

### `mac_address_changer/`

- **`models.py`**: Defines the `Interface` model for managing network interface details.
- **`views.py`**: Contains logic for:
  - Viewing and managing network interfaces.
  - Changing, reverting, and generating MAC addresses.
- **`urls.py`**: Maps URLs to their corresponding views.
- **`templates/mac_changer/index.html`**: The primary HTML template for the application.
- **`static/css/styles.css`**: Custom CSS for a clean and responsive design.

### `network_scanner/`

- **`models.py`**: Defines the `ScanLog` model for tracking scan history and results.
- **`views.py`**: Contains logic for performing network scans and displaying scan history.
- **`urls.py`**: Maps URLs to their corresponding views.
- **`templates/network_scanner/network_scanner.html`**: HTML template for the scan input form and results.
- **`templates/network_scanner/scan_history.html`**: HTML template for viewing scan history.
- **`scanner.py`**: Implements the ARP-based network scanning logic using `scapy`.

---

## How to Run the Application

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

### Manual Testing:
1. **Scan the Network**:
   - Input an IP range (e.g., `192.168.1.1/24`) in the Network Scanner tool and click "Scan".
   - Verify the displayed IP and MAC addresses.
2. **View Scan History**:
   - Navigate to the Scan History page and verify the logged results.

-