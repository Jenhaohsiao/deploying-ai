import sys
from pathlib import Path

# Add 05_src directory to Python path to allow execution from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))

import gradio as gr
from assignment_chat.main import assignment_chat
from dotenv import load_dotenv
from utils.logger import get_logger
import os

_logs = get_logger(__name__)

# Load environment variables from parent 05_src directory
src_dir = Path(__file__).parent.parent
load_dotenv(src_dir / ".env")
load_dotenv(src_dir / ".secrets")

chat = gr.ChatInterface(
    fn=assignment_chat,
    type="messages",
    title="� Radio DJ - Weather & Music",
    description="Your friendly radio DJ! Ask me about weather forecasts or get music recommendations from Pitchfork reviews. I can even suggest music that matches the weather mood!"
)

if __name__ == "__main__":
    _logs.info('Starting Radio DJ Chat App...')
    chat.launch()
