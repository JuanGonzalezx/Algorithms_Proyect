from decouple import config

class Settings:
    # API Keys
    GEMINI_API_KEY: str = config("GEMINI_API_KEY")
    
    # Server configuration
    HOST: str = config("HOST", default="localhost")
    PORT: int = config("PORT", default=8000, cast=int)
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    
    # Model configuration
    MAX_INPUT_LENGTH: int = config("MAX_INPUT_LENGTH", default=10000, cast=int)
    TIMEOUT_SECONDS: int = config("TIMEOUT_SECONDS", default=30, cast=int)

settings = Settings()