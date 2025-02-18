from datetime import datetime, timedelta
import calendar
import re

def validate_phone_number(phone):
    """Validate phone number format"""
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Check if the number has a valid length (10-15 digits)
    return 10 <= len(phone) <= 15

def validate_name(name):
    """Validate name format"""
    # Name should be at least 2 characters long and contain only letters, spaces, and hyphens
    return bool(re.match(r'^[A-Za-z\s-]{2,}$', name))

def format_time(time_str):
    """Format time string to HH:MM format"""
    try:
        # Check if time is in 12-hour format
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            # Parse 12-hour format
            time_obj = datetime.strptime(time_str, "%I:%M %p")
            # Return in 24-hour format for database
            return time_obj.strftime("%H:%M")
        else:
            # Parse 24-hour format
            return datetime.strptime(time_str, "%H:%M").strftime("%H:%M")
    except ValueError:
        return None

def get_week_dates(date=None):
    """Get list of dates for the current week"""
    if date is None:
        date = datetime.now()
    
    # Get the start of the week (Monday)
    start = date - timedelta(days=date.weekday())
    
    # Generate list of dates for the week
    return [start + timedelta(days=i) for i in range(7)]

def get_month_calendar(year, month):
    """Get calendar matrix for specified month"""
    return calendar.monthcalendar(year, month)

def format_date(date_obj):
    """Format date object to YYYY-MM-DD string"""
    return date_obj.strftime("%Y-%m-%d")

def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def time_slots(start_hour=9, end_hour=17, interval=30):
    """Generate time slots for appointments in 12-hour format"""
    slots = []
    current = datetime.strptime(f"{start_hour}:00", "%H:%M")
    end = datetime.strptime(f"{end_hour}:00", "%H:%M")
    
    while current <= end:
        # Convert to 12-hour format with AM/PM
        time_12hr = current.strftime("%I:%M %p").lstrip("0")
        slots.append(time_12hr)
        current += timedelta(minutes=interval)
    
    return slots

def validate_age(age):
    """Validate age input"""
    try:
        age = int(age)
        return 0 <= age <= 150
    except ValueError:
        return False

def format_phone_number(phone):
    """Format phone number for display"""
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Format as XXX-XXX-XXXX if 10 digits
    if len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    
    return phone 