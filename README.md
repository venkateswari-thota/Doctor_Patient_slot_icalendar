# 🩺 Doctor-Patient Appointment System with Advanced iCalendar Sync

A production-grade appointment scheduling system built with FastAPI and MongoDB. This system features a sophisticated **Universal Calendar Sync Engine** that ensures seamless, automatic synchronization across Microsoft Outlook, Google Calendar, and Apple Calendar.

## 🌟 Key Features

- **Smart Multi-Platform Dispatch**: Automatically detects recipient email providers and sends tailored iCalendar signals optimized for each platform.
- **Zero-Click Outlook Integration**: Uses native MIME structures and `Content-Class` headers to auto-add events as "Tentative" without user interaction.
- **Conflict-Free Google Sync**: Implements rigorous `SEQUENCE` tracking and `ATTENDEE` metadata to prevent synchronization errors in Gmail.
- **Apple "Zero-Click" Optimization**: Leverages **Schema.org JSON-LD** and Siri Suggestions to achieve the highest possible automation on iOS and macOS devices.
- **Atomic Booking Logic**: Protects against race conditions and double-bookings using MongoDB atomic operations.
- **Overlap Prevention**: Intelligent slot creation that prevents conflicting appointments for the same doctor.
- **Timezone Aware**: All appointments are localized to **IST (Asia/Kolkata)** for consistent scheduling.

## 🚀 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Motor / PyMongo)
- **iCalendar**: `icalendar` library
- **Email**: `smtplib` (Native MIME construction)
- **Validation**: Pydantic
- **Environment**: Pydantic Settings & Dotenv

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/venkateswari-thota/Doctor_Patient_slot_icalendar.git
cd Doctor_Patient_slot_icalendar
```

### 2. Environment Configuration
Create a `.env` file in the root directory and add your credentials:
```env
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-google-app-password
MAIL_FROM=your-sender-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MONGO_URI=your-mongodb-connection-string
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python -m uvicorn main:app --reload
```
The API documentation will be available at `http://127.0.0.1:8000/docs`.

## 📂 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/slots/create` | Create a new available slot with overlap protection. |
| `GET` | `/slots/free` | List all available slots. |
| `POST` | `/slots/book/{slot_id}` | Book a slot and trigger automatic calendar invites. |
| `DELETE` | `/slots/cancel/{slot_id}` | Cancel a booking with smart platform-specific cleanup. |

## 📅 Platform Synchronization Table

| Platform | Booking (Adding) | Cancellation (Removal) |
| :--- | :--- | :--- |
| **Outlook** | 🔥 **Automatic** | 🔥 **Automatic** |
| **Gmail** | 🔥 **Automatic*** | 🔥 **Automatic** |
| **Apple** | 🚀 **Auto/1-Click** | 🔥 **Automatic** |

*\*First-time senders may require a one-time "Trust" click in Gmail/Apple.*

## 📜 License
This project is for demonstration and production-grade integration purposes.
