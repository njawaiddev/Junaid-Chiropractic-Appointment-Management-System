# Junaid Chiropractic Appointment Management System

A comprehensive desktop application for managing chiropractic appointments, patient records, and session history.

## Features

- Doctor Dashboard with daily, weekly, and monthly appointment views
- Patient Database Management
- Appointment Scheduling and Management
- Patient History Tracking
- Calendar-style UI
- SQLite Database with monthly tables

## Installation

1. Ensure Python 3.8+ is installed on your system
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

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