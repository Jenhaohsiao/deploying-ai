import sys
from pathlib import Path

# Add 05_src directory to Python path to allow execution from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
from utils.logger import get_logger
import os

_logs = get_logger(__name__)

src_dir = Path(__file__).parent.parent
load_dotenv(src_dir / ".env")
load_dotenv(src_dir / ".secrets")

client = OpenAI()

open_ai_model = os.getenv("OPENAI_MODEL", "gpt-4-mini")

def assignment_chat(message, history):
    return f"WWW You said: {message}"

