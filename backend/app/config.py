import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    API_TIMEOUT = 30
    MAX_INPUT_LENGTH = 5000
    
config = Config()