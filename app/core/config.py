import os

class Settings:
    def __init__(self):
        # API Settings
        self.api_prefix: str = "/api"
        self.project_name: str = "EduLLMs"
        self.version: str = "1.0.0"
        
        # Database
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./edullms.db")
        
        # Punjab Text Book API - YOUR SETTINGS
        self.punjab_api_key: str = os.getenv("RENDER_API_KEY", "punjab123")  # Your key
        self.punjab_api_url: str = os.getenv("RENDER_URL", "https://punjab-text-book.onrender.com")
        
        # JWT
        self.secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm: str = "HS256"
        self.access_token_expire_minutes: int = 30
        
        # Print config for debugging
        print(f"\n⚙️  Configuration:")
        print(f"   Punjab API URL: {self.punjab_api_url}")
        print(f"   Punjab API Key: {self.punjab_api_key[:3]}***")
        print(f"   Database: {self.database_url}")

settings = Settings()