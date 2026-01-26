import os

class Settings:
    def __init__(self):
        self.api_prefix = "/api"
        self.project_name = "EduLLMs"
        self.version = "1.0.0"

        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./edullms.db")

        self.punjab_api_key = os.getenv("RENDER_API_KEY", "")
        self.punjab_api_url = os.getenv(
            "RENDER_URL",
            "https://6399df36b31b.ngrok-free.app"
        )

        self.secret_key = os.getenv("SECRET_KEY", "")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

        print("\n⚙️ Configuration loaded")
        print(f"   Punjab API URL: {self.punjab_api_url}")
        print(f"   Punjab API Key: {self.punjab_api_key[:3]}***")

settings = Settings()
