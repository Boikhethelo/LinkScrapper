import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    All configuration is loaded from environment variables.
    fill in your values in your .env file.
    """

    # ===============================================
    #           LinkedIn Credentials
    # ===============================================

    LINKEDIN_EMAIL : str = os.getenv("LINKEDIN_EMAIL", "")
    LINKEDIN_PASSWORD : str = os.getenv("LINKEDIN_PASSWORD", "")


    # ===============================================
    #            LinkedIn OAuth2 API
    # ===============================================

    LINKEDIN_CLIENT_ID : str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_REDIRECT_URI: str = os.getenv(
        "LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback"
    )

    # ===============================================
    #            Rate Limiting
    # ===============================================

    MIN_DELAY: float = float(os.getenv("MIN_DELAY", "3.0"))
    MAX_DELAY: float = float(os.getenv("MAX_DELAY" , "8.0"))
    MAX_RETRIES: int = float(os.getenv("MAX_RETRIES" , "3"))


    # ================================================
    #              Browser
    # ================================================

    HEADLESS: bool =os.getenv("HEADLESS" , "true").lower() == "true"


    # ================================================
    #                 Storage
    # ================================================

    DB_PATH : str = os.getenv("DB_PATH" , "data/linkedin.db")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "data/output")

settings = Settings()