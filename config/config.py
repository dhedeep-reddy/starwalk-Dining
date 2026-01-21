import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Azure OpenAI
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Model Parameters
    TEMPERATURE = 0.7
    MAX_TOKENS = 1000

    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        missing = []
        if not cls.AZURE_OPENAI_API_KEY: missing.append("AZURE_OPENAI_API_KEY")
        if not cls.AZURE_OPENAI_ENDPOINT: missing.append("AZURE_OPENAI_ENDPOINT")
        if not cls.SUPABASE_URL: missing.append("SUPABASE_URL")
        if not cls.SUPABASE_KEY: missing.append("SUPABASE_KEY")
        
        if missing:
            return False, f"Missing environment variables: {', '.join(missing)}"
        return True, "Configuration valid"
