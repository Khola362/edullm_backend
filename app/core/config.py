import os
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE any other imports
load_dotenv()

class Settings:
    def __init__(self):
        self.api_prefix = "/api"
        self.project_name = "EduLLMs"
        self.version = "1.0.0"

        # Now these will read from .env file
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./edullms.db")
        self.punjab_api_key = os.getenv("RENDER_API_KEY", "")
        self.punjab_api_url = os.getenv("RENDER_URL", "")
        self.secret_key = os.getenv("SECRET_KEY", "")

        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

        print("\n⚙️ Configuration loaded")
        print(f"   Database URL: {self.database_url}")
        print(f"   Punjab API URL: {self.punjab_api_url}")
        print(f"   Punjab API Key: {self.punjab_api_key}")
        print(f"   Secret Key: {self.secret_key[:8]}***")

# Create global instance
settings = Settings()
