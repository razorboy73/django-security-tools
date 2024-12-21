# Django Security Tools

#### Video Demo: <URL HERE>

---

## Description

**Django Security Tools** is a suite of network security and engineering tools designed to provide network engineers with a web-based interface for essential network operations. Built on Django, this project combines high-level web frameworks with low-level system operations for seamless and efficient management.

The first tool in this suite is the **MAC Address Changer**, which allows users to manage and modify MAC addresses of their network interfaces with ease.

---

### Features of **MAC Address Changer**:

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

## Recent Updates

- **Enhanced Revert Functionality**:
  - Automatically reverts the last modified interface without requiring manual input.
- **Improved Error Handling**:
  - Validates MAC address formats, ensures interfaces are up before modifications, and handles command execution errors gracefully.
- **Dynamic Interface Updates**:
  - Fetches and displays active network interfaces dynamically using AJAX, ensuring up-to-date data without refreshing the page.
- **Comprehensive Unit Tests**:
  - Expanded test cases to cover error handling, system command execution, and edge cases.

---

## Distinctiveness and Complexity

### Distinctiveness:

This project uniquely integrates operating system-level network operations with Django, offering a high-level abstraction for low-level commands. Unlike traditional Django applications that focus on database CRUD operations or static content management, this project executes real-time system-level modifications, bridging the gap between web development and network engineering.

---

### Complexity:

1. **System-Level Command Execution**:
   - Executes commands like `ifconfig` and `ip link` securely using Python’s `subprocess` library, handling complex error scenarios.
2. **Database-Driven State Management**:
   - Tracks the state of network interfaces, including fields for `original_mac`, `mac_address`, and `last_changed`.
3. **Dynamic Frontend Interactions**:
   - Utilizes AJAX for fetching network interfaces and JavaScript for dynamic UI updates.
4. **Robust Validation**:
   - Ensures MAC addresses are valid and prevents invalid changes from being applied to network interfaces.
5. **Reversibility**:
   - Tracks and reverts MAC address changes, ensuring no permanent alterations unless explicitly requested.

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
  - Providing real-time feedback and error handling.
- **`urls.py`**: Maps URLs to their corresponding views.
- **`templates/mac_changer/index.html`**: The primary HTML template for the application, including AJAX integration for dynamic updates.
- **`static/css/styles.css`**: Custom CSS for a clean and responsive design.
- **`admin.py`**: Registers the `Interface` model for use in Django’s admin interface.
- **`tests.py`**: Includes comprehensive test cases covering:
  - Validation of MAC addresses.
  - Command execution and error handling.
  - User interactions with the application.

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

Expected Output:
```
Ran 8 tests in 0.345s
OK
```

### Manual Testing:
1. **View Interfaces**:
   - Click the "Find Network Interfaces" button to fetch and display the active interfaces.

2. **Generate a Random MAC**:
   - Click the "Generate MAC" button and verify the generated MAC address is valid.

3. **Change MAC Address**:
   - Select an interface, enter or generate a valid MAC address, and click "Change MAC".
   - Confirm the MAC address is updated on the selected interface.

4. **Revert MAC Address**:
   - Click "Revert to Original MAC" to revert the last modified interface to its original address.

---

## Future Improvements

1. Expand the suite with additional tools, such as:
   - IP address configuration.
   - Port scanning and network monitoring utilities.
   - Firewall management.
2. Implement user authentication for enhanced security.
3. Add support for multiple operating systems (e.g., Windows compatibility).
4. Provide detailed logs and analytics for network operations.

