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
        # Handle empty or None input
        if not time_str:
            return None
            
        # Remove any leading/trailing whitespace
        time_str = time_str.strip()
        
        # Check if time is in 12-hour format
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            # Parse 12-hour format
            time_obj = datetime.strptime(time_str.upper(), "%I:%M %p")
        else:
            # Parse 24-hour format
            time_obj = datetime.strptime(time_str, "%H:%M")
            
        # Return in 24-hour format for database
        return time_obj.strftime("%H:%M")
    except ValueError:
        return None

def format_time_12hr(time_str):
    """Convert time string to 12-hour format"""
    try:
        # Handle empty or None input
        if not time_str:
            return None
            
        # Remove any leading/trailing whitespace
        time_str = time_str.strip()
        
        # Parse time string (handles both 12h and 24h formats)
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            time_obj = datetime.strptime(time_str.upper(), "%I:%M %p")
        else:
            time_obj = datetime.strptime(time_str, "%H:%M")
            
        # Convert to 12-hour format
        return time_obj.strftime("%I:%M %p").lstrip("0")
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

def time_slots(start_hour=9, end_hour=17, interval=15):
    """Generate time slots for appointments in 12-hour format"""
    slots = []
    try:
        current = datetime.strptime(f"{start_hour:02d}:00", "%H:%M")
        end = datetime.strptime(f"{end_hour:02d}:00", "%H:%M")
        
        while current <= end:
            # Convert to 12-hour format with AM/PM
            time_12hr = current.strftime("%I:%M %p").lstrip("0")
            slots.append(time_12hr)
            current += timedelta(minutes=interval)
    except ValueError:
        # Return default business hours if there's an error
        slots = ["9:00 AM", "9:15 AM", "9:30 AM", "9:45 AM",
                "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM",
                "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM",
                "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM",
                "1:00 PM", "1:15 PM", "1:30 PM", "1:45 PM",
                "2:00 PM", "2:15 PM", "2:30 PM", "2:45 PM",
                "3:00 PM", "3:15 PM", "3:30 PM", "3:45 PM",
                "4:00 PM", "4:15 PM", "4:30 PM", "4:45 PM",
                "5:00 PM"]
    
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