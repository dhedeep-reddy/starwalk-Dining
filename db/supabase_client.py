from supabase import create_client, Client
import os
import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from AI_UseCase.config.config import Config

class SupabaseManager:
    def __init__(self):
        url = Config.SUPABASE_URL
        key = Config.SUPABASE_KEY
        if not url or not key:
            raise ValueError("Supabase credentials not found in config")
        
        self.supabase: Client = create_client(url, key)

    def sign_up(self, email, password, name, is_admin=False):
        """Register a new user in Supabase Auth"""
        try:
            res = self.supabase.auth.sign_up({
                "email": email, 
                "password": password,
                "options": {
                    "data": { 
                        "full_name": name,
                        "is_admin": is_admin
                    } 
                }
            })
            return {"success": True, "data": res}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sign_in(self, email, password):
        """Login existing user"""
        try:
            res = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"success": True, "data": res}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def is_admin(self, user_id):
        """
        Check if user is admin via app_metadata or user_metadata.
        Since we can't easily fetch user by ID without admin key in some setups,
        we rely on the session/user object passed in frontend or fetch my own details.
        
        Alternative: Fetch the user's data from a public 'profiles' table if we had one.
        For now, let's try to get user.
        """
        try:
            user = self.supabase.auth.get_user()
            if user and user.user.user_metadata.get('is_admin'):
                return True
            # Fallback for old hardcoded
            return False
        except:
            return False

    def get_user_bookings(self, user_email):
        """Fetch bookings for a specific user (by email relation)"""
        try:
            # We are joining with customers table on email
            # First find customer_id for this email
            cust_res = self.supabase.table("customers").select("id").eq("email", user_email).execute()
            if not cust_res.data:
                return []
            
            cust_id = cust_res.data[0]['id']
            res = self.supabase.table("reservations").select("*").eq("customer_id", cust_id).order("reservation_date", desc=True).execute()
            return res.data
        except Exception as e:
            return []

    def create_booking(self, booking_data):
        """
        Create a new booking/reservation.
        """
        try:
            customer_data = {
                "name": booking_data.get("name"),
                "email": booking_data.get("email"),
                "phone": booking_data.get("phone")
            }
            
            customer_res = self.supabase.table("customers").upsert(customer_data, on_conflict="email").execute()
            
            if not customer_res.data:
                 customer_res = self.supabase.table("customers").select("*").eq("email", booking_data.get("email")).execute()

            customer_id = customer_res.data[0]['id']

            reservation_data = {
                "customer_id": customer_id,
                "party_size": int(booking_data.get("party_size")),
                "reservation_date": booking_data.get("date"),
                "reservation_time": booking_data.get("time"),
                "special_requests": booking_data.get("special_requests", ""),
                "status": "confirmed"
            }
            
            res = self.supabase.table("reservations").insert(reservation_data).execute()
            return {"success": True, "data": res.data}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_all_bookings(self):
        """Fetch all bookings for admin dashboard"""
        try:
            response = self.supabase.table("reservations").select("*, customers(name, email, phone)").order("reservation_date", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching bookings: {e}")
            return []
