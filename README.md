# Django Security Tools

#### Video Demo: <URL HERE>

---

## Description

**Django Security Tools** is a suite of network security and engineering tools built as Django applications. This project aims to provide network engineers with a user-friendly interface to perform essential network operations directly from their browser, running locally on their systems.

The first application in this suite is the **MAC Address Changer**, designed for seamless MAC address management.

### Features of **MAC Address Changer**:

1. **View Network Interfaces**: 
   - Displays all active network interfaces, including their names and current MAC addresses.
2. **Generate Random MAC Addresses**: 
   - Create valid, unique, locally administered MAC addresses with a single click.
3. **Change MAC Addresses**: 
   - Modify the MAC address of a selected network interface.
4. **Revert MAC Addresses**: 
   - Revert any changed MAC address to its original value, ensuring no permanent changes.
5. **Track History**: 
   - Stores a history of generated MAC addresses with timestamps.
6. **User-Friendly Interface**: 
   - Built with a responsive design using Django templates, custom CSS, and JavaScript for real-time alerts and feedback.

### Recent Updates:
- Added functionality to track which network interface was last modified.
- Simplified the process of reverting to the original MAC address by automatically identifying the last changed interface.
- Improved error handling for edge cases such as invalid MAC addresses or unavailable network interfaces.

---

## Distinctiveness and Complexity

### Distinctiveness:

This project stands out because it integrates system-level operations (e.g., MAC address changes via `ifconfig` or `ip`) with a high-level web framework like Django. It bridges the gap between operating system utilities and web-based network management.

Key distinguishing factors include:
- **System-Level Integration**: Uses Python's `subprocess` library to directly interact with the OS, making real-time changes to network configurations.
- **Interactive Web UI**: Combines Django templates, CSS, and JavaScript for a dynamic and user-friendly experience.
- **Reversible Operations**: Tracks and reverts MAC changes, ensuring reliability.

### Complexity:

1. **OS-Level Command Execution**: Handles complex system commands securely and ensures error-free execution by validating inputs and outputs.
2. **Database-Driven Logic**: Uses the Django ORM to manage interfaces and maintain history, including fields for original and last-changed MAC addresses.
3. **Real-Time Updates**: Displays network interfaces and their states dynamically, with AJAX calls for fetching interface data and generating MAC addresses.
4. **Error Handling**: Provides real-time feedback for errors such as invalid MAC addresses or command execution issues, enhancing user reliability.
5. **Scalability**: Lays the groundwork for adding more security tools as Django apps, making it a modular and extensible framework.

---

## File Contents

### Project Root

- **`.gitignore`**: Excludes unnecessary files from version control, such as `db.sqlite3` and `__pycache__`.
- **`README.md`**: Comprehensive project documentation.
- **`requirements.txt`**: Lists Python dependencies required for the project.

### `mac_address_changer/`

- **`models.py`**: Defines models to store interface details, including fields for `original_mac`, `mac_address`, and `last_changed`.
- **`views.py`**: Implements functionality for:
  - Viewing network interfaces.
  - Changing and reverting MAC addresses.
  - Generating random MAC addresses.
  - Handling error cases and user feedback.
- **`urls.py`**: Maps URLs to the appropriate views.
- **`tests.py`**: Unit tests covering:
  - MAC address validation.
  - Generating unique MAC addresses.
  - Changing and reverting MAC addresses.
  - Handling edge cases (e.g., missing original MAC).
- **`templates/mac_changer/index.html`**: The main HTML template for the application, providing a responsive and intuitive user interface.
- **`static/css/styles.css`**: Custom CSS for styling the application.
- **`admin.py`**: Registers models for use in the Django admin interface.

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
To ensure the application is functioning correctly, run:
```bash
python manage.py test
```

Expected Output:
```
Ran 7 tests in 0.123s
OK
```

### Manual Testing:
1. **View Interfaces**:
   - Click the "Find Network Interfaces" button.
   - Verify the list of interfaces and their MAC addresses.

2. **Generate a Random MAC**:
   - Click the "Generate MAC" button and confirm the generated address is valid.

3. **Change MAC Address**:
   - Select an interface, enter a valid MAC address, and click "Change MAC".
   - Confirm the MAC address is updated in the database and on the interface.

4. **Revert MAC Address**:
   - Click "Revert to Original MAC".
   - Verify the MAC address reverts to the original value.

---

## Future Improvements

1. Add support for additional network tools (e.g., IP address configuration, firewall settings).
2. Enhance error handling for specific system environments (e.g., Windows vs. Linux).
3. Implement user authentication for secure access to the tools.

