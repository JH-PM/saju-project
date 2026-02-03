
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro-latest")
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", 0.7))
    SYSTEM_PROMPT_PATH = os.getenv("SYSTEM_PROMPT_PATH", "system_prompt.md")
    OUTPUT_LANGUAGE = os.getenv("OUTPUT_LANGUAGE", "ko")
    
    _system_prompt_content = None

    @classmethod
    def get_system_prompt(cls):
        """
        Reads and returns the content of the system prompt file.
        Caches the content in memory.
        """
        if cls._system_prompt_content is not None:
            return cls._system_prompt_content
            
        if not os.path.exists(cls.SYSTEM_PROMPT_PATH):
            # Fallback relative to this file if needed, or error
            # Current dir usually root of project
            return "System prompt file not found."
            
        try:
            with open(cls.SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
                cls._system_prompt_content = f.read()
        except Exception as e:
            cls._system_prompt_content = f"Error loading system prompt: {str(e)}"
            
        return cls._system_prompt_content

# Expose a singleton-like access if preferred, or just use Config class
settings = Config
