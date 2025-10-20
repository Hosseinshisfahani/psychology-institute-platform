# Appointments App

## Overview
The Appointments app is designed for managing in-person meetings at the psychology institute. It replaces the previous therapy_sessions app and focuses specifically on physical appointments at the institute rather than online sessions.

## Key Features

### For Clients:
- Book in-person appointments with staff members
- View available time slots
- Cancel or reschedule appointments
- Provide feedback after appointments
- View appointment history and statistics

### For Staff:
- Manage their availability schedule
- View their appointments
- Confirm or reject appointment requests
- Mark appointments as completed
- Add internal notes

### For Administrators:
- Manage all appointments
- Create and manage staff profiles
- Configure appointment types
- Manage appointment rooms
- View appointment statistics

## Models

1. **Staff** - Institute staff members who provide appointments
2. **AppointmentType** - Different types of appointments offered
3. **AppointmentRoom** - Physical rooms at the institute
4. **StaffAvailability** - Weekly availability schedule for staff
5. **TimeSlot** - Available time slots for appointments
6. **Appointment** - The actual appointment bookings
7. **AppointmentCancellation** - Tracks cancelled appointments
8. **AppointmentReminder** - Manages appointment reminders
9. **AppointmentFeedback** - Client feedback for completed appointments

## API Endpoints

### Public Endpoints:
- `GET /api/appointments/staff/` - List available staff
- `GET /api/appointments/appointment-types/` - List appointment types
- `GET /api/appointments/available-slots/` - Get available time slots

### Authenticated Endpoints:
- `GET /api/appointments/my-appointments/` - User's appointments
- `POST /api/appointments/appointments/create/` - Book an appointment
- `POST /api/appointments/appointments/{id}/cancel/` - Cancel appointment
- `POST /api/appointments/appointments/{id}/reschedule/` - Reschedule
- `POST /api/appointments/feedback/create/` - Submit feedback

### Admin Endpoints:
- `/api/admin/appointments/` - Manage all appointments
- `/api/admin/staff/` - Manage staff members
- `/api/admin/appointment-types/` - Manage appointment types
- `/api/admin/appointment-rooms/` - Manage rooms

## Key Differences from therapy_sessions:
1. **Focus on in-person meetings** - No online session support
2. **Room management** - Physical room allocation and tracking
3. **Staff roles** - Multiple staff roles beyond therapists
4. **Simplified booking** - Direct appointment booking without complex session management
5. **Institute-specific features** - Floor numbers, room facilities, etc.