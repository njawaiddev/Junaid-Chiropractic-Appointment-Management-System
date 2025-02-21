# Junaid Chiropractic Management System

Version 2.0.0

A comprehensive management system for chiropractic clinics, featuring appointment scheduling, patient management, and Google Calendar integration.

## Features

- Patient Management
- Appointment Scheduling
- Google Calendar Integration
- Offline Mode Support
- Automatic Backups
- Statistics and Reports

## Installation

### Windows Users

1. Download the latest installer: [ChiropracticManager_Setup_v2.exe](releases/ChiropracticManager_Setup_v2.exe)
2. Run the installer as administrator
3. Follow the installation wizard
4. Launch the application from your Start Menu or Desktop shortcut

Note: This is a standalone installer. You don't need to install Python or any other dependencies - everything is included in the installer.

### For Developers

If you want to modify or build the application from source:

#### Prerequisites
- Python 3.9 or later
- pip package manager

#### Setup
1. Clone the repository:
```bash
git clone https://github.com/njawaiddev/Junaid-Chiropractic-Appointment-Management-System.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/main.py
```

## Google Calendar Integration

To use Google Calendar features:
1. Go to Google Cloud Console
2. Create a new project or select an existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download credentials.json
6. Place credentials.json in the application data directory
7. Authorize the application when prompted

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details.

## Developer

Naveed Jawaid

## Support

For support, please open an issue on GitHub or contact the developer.

## Project Structure

```
src/
├── database/
│   ├── __init__.py
│   ├── db_manager.py
│   └── schema.py
├── ui/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── patient_view.py
│   └── appointment_view.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── main.py
```

## Building Executable

To create a standalone executable:

```bash
pyinstaller --onefile --windowed src/main.py
``` 