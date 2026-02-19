import os
from icalendar import Calendar, Event, Alarm, vCalAddress, vText
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

def generate_appointment_ics(
    uid: str,
    summary: str,
    description: str,
    start_time: str,  # "HH:MM:SS"
    end_time: str,    # "HH:MM:SS"
    date_str: str,     # "YYYY-MM-DD"
    method: str = "REQUEST",
    sequence: int = 0,
    status: str = None
):
    cal = Calendar()
    cal.add('prodid', '-//Hospital//Appointment System//EN')
    cal.add('version', '2.0')
    cal.add('method', method)

    event = Event()
    event.add('uid', uid)
    event.add('summary', summary)
    event.add('description', description)

    # Add Organizer (Required for Outlook to process cancellations correctly)
    organizer_email = os.getenv("MAIL_FROM", "noreply@hospital.com")
    organizer = vCalAddress(f'MAILTO:{organizer_email}')
    organizer.params['cn'] = vText('Doctor Appointment System')
    event.add('organizer', organizer)
    
    # Parse date and time with IST (Asia/Kolkata) localization
    def parse_dt(d_str, t_str):
        formats = [
            ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"),
            ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S"),
            ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M"),
            ("%d-%m-%Y %H:%M", "%d-%m-%Y %H:%M"),
        ]
        full_str = f"{d_str} {t_str}"
        ist = pytz.timezone("Asia/Kolkata")
        
        for d_fmt, f_fmt in formats:
            try:
                dt = datetime.strptime(full_str, d_fmt)
                return ist.localize(dt)
            except ValueError:
                continue
        try:
            dt = datetime.strptime(f"{d_str} {t_str}", "%d-%m-%Y %H:%M")
            return ist.localize(dt)
        except:
            raise ValueError(f"Could not parse date/time: {full_str}")

    dt_start = parse_dt(date_str, start_time)
    dt_end = parse_dt(date_str, end_time)
    
    # Assume UTC for simplicity, or localized if needed
    event.add('dtstart', dt_start)
    event.add('dtend', dt_end)
    event.add('dtstamp', datetime.now(pytz.utc))
    event.add('sequence', sequence)
    
    if status:
        event.add('status', status)

    if method == "CANCEL" or status == "CANCELLED":
        # No alarms for cancellation
        pass
    else:
        # Add 30-minute reminder
        alarm30 = Alarm()
        alarm30.add('action', 'DISPLAY')
        alarm30.add('description', f'REMINDER: {summary} in 30 minutes')
        alarm30.add('trigger', timedelta(minutes=-30))
        event.add_component(alarm30)

        # Add 10-minute reminder
        alarm10 = Alarm()
        alarm10.add('action', 'DISPLAY')
        alarm10.add('description', f'REMINDER: {summary} in 10 minutes')
        alarm10.add('trigger', timedelta(minutes=-10))
        event.add_component(alarm10)

    cal.add_component(event)
    return cal.to_ical()
