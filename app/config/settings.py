from decouple import config

class Settings:
    # API Keys - soporta múltiples keys para rotación automática
    GEMINI_API_KEYS: str = config("GEMINI_API_KEYS", default=None)  # Formato: "key1,key2,key3"
    GEMINI_API_KEY: str = config("GEMINI_API_KEY", default=None)   # Formato legacy (single key)
    
    # Server configuration
    HOST: str = config("HOST", default="localhost")
    PORT: int = config("PORT", default=8000, cast=int)
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    
    # Model configuration
    MAX_INPUT_LENGTH: int = config("MAX_INPUT_LENGTH", default=10000, cast=int)
    
    # Gemini timeout and retry configuration
    GEMINI_TIMEOUT: int = config("GEMINI_TIMEOUT", default=60, cast=int)
    GEMINI_MAX_RETRIES: int = config("GEMINI_MAX_RETRIES", default=3, cast=int)
    GEMINI_BASE_DELAY: int = config("GEMINI_BASE_DELAY", default=2, cast=int)

settings = Settings()