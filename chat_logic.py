import sys
import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import Config
from rag_pipeline import RAGPipeline
from booking_flow import BookingFlow, BookingState
from db.supabase_client import SupabaseManager
from utils.email_sender import send_confirmation_email

class ChatLogic:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
            openai_api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            temperature=Config.TEMPERATURE
        )
        self.rag = RAGPipeline()
        self.booking_flows = {} # Map session_id -> BookingFlow
        self.supabase = SupabaseManager()

    def get_booking_flow(self, session_id):
        if session_id not in self.booking_flows:
            self.booking_flows[session_id] = BookingFlow()
        return self.booking_flows[session_id]

    def detect_intent(self, user_input, history):
        """
        Determine if user is asking a general question or wants to book.
        Simple Keyword / LLM based detection.
        """
        # Simple keyword heuristic for speed/robustness
        booking_keywords = ["book", "reservation", "reserve", "table", "appointment"]
        
        # If in middle of booking, intent is booking
        # But this is stateless, so we rely on session state checks in `process_message`
        
        # Check if LLM thinks it's a booking intent
        prompt = f"""
        Analyze the user input and determine intent.
        Input: "{user_input}"
        
        Return ONLY one word:
        - "BOOKING" if user wants to make a new reservation or is providing reservation details.
        - "QUERY" if user is asking about menu, hours, location, policies, etc.
        - "OTHER" for chit-chat.
        """
        response = self.llm.invoke([SystemMessage(content=prompt)])
        intent = response.content.strip().upper()
        
        if any(w in user_input.lower() for w in booking_keywords):
            return "BOOKING"
            
        return intent

    def process_message(self, session_id, user_input, chat_history):
        flow = self.get_booking_flow(session_id)
        
        # 1. If we are already in a booking flow (not INITIAL), continue it.
        if flow.state != BookingState.INITIAL:
            response, is_complete = flow.process_input(user_input)
            
            if is_complete:
                # Save to DB
                db_result = self.supabase.create_booking(flow.booking_data)
                if db_result["success"]:
                    response += f"\n\n(Booking ID: {db_result['data'][0]['id']})"
                    
                    # Send Confirmation Email 
                    # Assuming email is in booking_data since we collected it
                    if "email" in flow.booking_data:
                        email_res = send_confirmation_email(flow.booking_data["email"], flow.booking_data)
                        if email_res["success"]:
                            response += "\n📧 Confirmation email sent."
                        else:
                            response += f"\n(⚠️ Email failed: {email_res.get('error')})"
                else:
                    response += f"\n\n(Note: Could not save to database: {db_result.get('error')})"
                
                # Reset flow
                self.booking_flows[session_id] = BookingFlow() 
                
            return response

        # 2. Detect Intent
        intent = self.detect_intent(user_input, chat_history)

        if "BOOKING" in intent:
            # Start booking flow
            response, _ = flow.process_input(user_input) # Will trigger INITIAL -> COLLECT_NAME
            return response

        elif "QUERY" in intent:
            # RAG
            context = self.rag.query(user_input)
            
            rag_prompt = f"""
            You are a helpful restaurant assistant. Answer the user question based on the context below.
            If the answer is not in the context, say you don't know but can help with a booking.
            
            Context:
            {context}
            
            User Question: {user_input}
            """
            response = self.llm.invoke([SystemMessage(content=rag_prompt)])
            return response.content
            
        else:
            # General chit chat
            response = self.llm.invoke(chat_history + [HumanMessage(content=user_input)])
            return response.content
