from enum import Enum
import re

class BookingState(Enum):
    INITIAL = "initial"
    COLLECT_NAME = "collect_name"
    COLLECT_EMAIL = "collect_email"
    COLLECT_PHONE = "collect_phone"
    COLLECT_DATE = "collect_date"
    COLLECT_TIME = "collect_time"
    COLLECT_PARTY_SIZE = "collect_party_size"
    COLLECT_REQUESTS = "collect_requests"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"

class BookingFlow:
    def __init__(self):
        self.state = BookingState.INITIAL
        self.booking_data = {}
        self.missing_fields = [
            "name", "email", "phone", "date", "time", "party_size"
        ]

    def process_input(self, user_input, llm_response=None):
        """
        Process user input based on current state.
        Returns: (next_response_to_user, is_booking_complete)
        """
        # Basic state machine
        if self.state == BookingState.INITIAL:
            self.state = BookingState.COLLECT_NAME
            return "Please provide your **Name** for the reservation.", False
        
        elif self.state == BookingState.COLLECT_NAME:
            self.booking_data["name"] = user_input
            self.state = BookingState.COLLECT_EMAIL
            return f"Thanks {user_input}. What is your **Email** address?", False

        elif self.state == BookingState.COLLECT_EMAIL:
            # Simple validation
            if "@" not in user_input:
                return "That doesn't look like a valid email. Please try again.", False
            self.booking_data["email"] = user_input
            self.state = BookingState.COLLECT_PHONE
            return "Got it. What is your **Phone Number**?", False

        elif self.state == BookingState.COLLECT_PHONE:
            self.booking_data["phone"] = user_input
            self.state = BookingState.COLLECT_DATE
            return "Thanks. What **Date** would you like to book for? (e.g., Tomorrow, 2024-05-20)", False

        elif self.state == BookingState.COLLECT_DATE:
            self.booking_data["date"] = user_input
            self.state = BookingState.COLLECT_TIME
            return "What **Time** would you like?", False

        elif self.state == BookingState.COLLECT_TIME:
            # Simple normalization for "12pm" -> "12:00:00"
            raw_time = user_input.lower().strip()
            formatted_time = raw_time
            
            # Very basic heuristic for xpm/xam
            if "pm" in raw_time or "am" in raw_time:
                 try:
                     import datetime
                     # Parse 12pm, 5:30pm etc.
                     # Remove spaces
                     raw_time = raw_time.replace(" ", "")
                     # pad minutes if missing e.g. "5pm" -> "5:00pm"
                     if ":" not in raw_time:
                         raw_time = raw_time.replace("am", ":00am").replace("pm", ":00pm")
                     
                     dt = datetime.datetime.strptime(raw_time, "%I:%M%p")
                     formatted_time = dt.strftime("%H:%M:%S")
                 except:
                     pass # Fallback to raw input if parse fails
            
            self.booking_data["time"] = formatted_time
            self.state = BookingState.COLLECT_PARTY_SIZE
            return f"Got it ({formatted_time}). How many people are in your **Party**?", False

        elif self.state == BookingState.COLLECT_PARTY_SIZE:
            # simple validation
            if not any(char.isdigit() for char in user_input):
                 return "Please enter a number for the party size.", False
            
            self.booking_data["party_size"] = user_input
            self.state = BookingState.COLLECT_REQUESTS
            return "Any **Special Requests** (e.g., dietary restrictions, high chair)? Say 'None' if none.", False

        elif self.state == BookingState.COLLECT_REQUESTS:
            self.booking_data["special_requests"] = user_input
            self.state = BookingState.CONFIRMATION
            
            summary = (
                f"Please confirm your booking details:\n\n"
                f"- **Name**: {self.booking_data['name']}\n"
                f"- **Email**: {self.booking_data['email']}\n"
                f"- **Phone**: {self.booking_data['phone']}\n"
                f"- **Date**: {self.booking_data['date']}\n"
                f"- **Time**: {self.booking_data['time']}\n"
                f"- **Party Size**: {self.booking_data['party_size']}\n"
                f"- **Requests**: {self.booking_data['special_requests']}\n\n"
                f"Type **'Yes'** to confirm or **'No'** to restart."
            )
            return summary, False

        elif self.state == BookingState.CONFIRMATION:
            if "yes" in user_input.lower():
                self.state = BookingState.COMPLETED
                return "Great! Your booking is confirmed. I've sent you a confirmation email.", True
            else:
                self.state = BookingState.INITIAL
                self.booking_data = {}
                return "Booking cancelled. How else can I help you?", False

        return "Error in booking flow.", False
