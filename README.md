# Django Security Tools

#### Video Demo: <URL HERE>

---

## Description

A collection of network security and hacking tools written in Python and running as apps within a Django framework

### Project Root

- **`.gitignore`**: Specifies files and directories to be excluded from version control, such as `db.sqlite3` and `__pycache__`.
- **`README.md`**: Provides comprehensive documentation of the project.
- **`requirements.txt`**: Lists all Python dependencies required to run the project.

These tools include the following applications:
**MAC Address Changer**

**MAC Address Changer**

The **MAC Address Changer** is a sophisticated, Django-based web application designed for network engineers to manage and modify the Media Access Control (MAC) addresses of their devices seamlessly. This tool is part of a broader suite of network security and engineering tools, developed to run locally and assist in everyday network management tasks.

The application enables users to:

1. View a list of available network interfaces.
2. Generate random, unique MAC addresses on demand.
3. Change the MAC address of a selected interface.
4. Revert back to the original MAC address when required.
5. Maintain a history of all generated MAC addresses, including timestamps for tracking purposes.

The application provides an intuitive front-end interface with CSS styling and JavaScript alerts to notify users of changes and errors. By integrating Django's robust backend capabilities with Python's subprocess library, this tool ensures secure and efficient handling of system commands.

---

## Distinctiveness and Complexity

### Distinctiveness:

This project is unique as it integrates low-level network manipulation with a high-level web framework like Django. Unlike typical Django applications focused solely on database CRUD operations or general-purpose web interfaces, this application interacts with the operating system to perform real-time network interface modifications. The integration of system-level command execution into a user-friendly web application sets this project apart from traditional Django projects.

### Complexity:

1. **System Interaction**: The project uses Python’s `subprocess` library to execute network commands like `ifconfig`, making it interact directly with the operating system. This introduces complexities such as error handling, command validation, and ensuring system security.
2. **Random MAC Address Generation**: Implementing a utility to generate unique, valid MAC addresses while ensuring that duplicates are never reused requires attention to randomness and database integrity.
3. **Data Persistence**: The application stores the history of generated MAC addresses and the original MAC address for reversion, adding a layer of database interaction that ties into the app’s core functionality.
4. **Error Handling and Alerts**: Real-time feedback to users via JavaScript alerts, coupled with Django’s messaging framework, enhances the user experience while adding complexity to the system.
5. **Integration of Frontend and Backend**: The application incorporates custom CSS for styling and JavaScript for interactivity, ensuring a seamless user experience alongside robust backend logic.
6. **Reversibility**: The ability to revert to the original MAC address adds an additional layer of functionality that ensures reliability and usability for network engineers.

These factors together demonstrate the distinctiveness and complexity of the project, showcasing its uniqueness in the realm of Django applications.

---

## File Contents

### `network_tools/`

- **`manage.py`**: The command-line utility for managing this Django project.

### `mac_changer/`

- **`models.py`**: Contains the `MacAddressHistory` and `Interface` models for tracking MAC addresses and interfaces.
- **`views.py`**: Implements the core logic for generating, changing, reverting MAC addresses, and rendering the interface list.
- **`urls.py`**: Maps URLs to their corresponding views.
- **`forms.py`**: Defines forms for user input (e.g., MAC address and interface selection).
- **`admin.py`**: Registers models with the Django admin interface for easy management.
- **`tests.py`**: Includes unit tests to ensure functionality such as MAC validation and random MAC generation.
- **`templates/mac_changer/index.html`**: The main HTML template for the application.
- **`static/css/styles.css`**: Custom CSS for styling the web interface.

---

## How to Run the Application

1. Clone the repository:

   git clone https://github.com/razorboy73/django-security-tools
   cd django-security-tools
   Set up a Python virtual environment:
   python3 -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate

2. Install dependencies:
   pip install -r requirements.txt
3. Apply database migrations
   python manage.py makemigrations
   python manage.py migrate
4. Run the development server:
   python manage.py runserver
   Open your browser and navigate to http://127.0.0.1:8000/ to access the application.
