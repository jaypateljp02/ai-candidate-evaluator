# Utility Helpers
# Common helper functions used across all phases.

import os
from dotenv import load_dotenv

def load_env():
    """Load environment variables from .env file."""
    load_dotenv()
    return os.getenv("GEMINI_API_KEY")
