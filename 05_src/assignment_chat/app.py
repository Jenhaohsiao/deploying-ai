import sys
from pathlib import Path

# Add 05_src directory to Python path to allow execution from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))

import gradio as gr
from assignment_chat.main import assignment_chat
from dotenv import load_dotenv
import os

# Load environment variables from parent 05_src directory
src_dir = Path(__file__).parent.parent
load_dotenv(src_dir / ".env")
load_dotenv(src_dir / ".secrets")

chat = gr.ChatInterface(
    fn=assignment_chat,
    type="messages"
)

if __name__ == "__main__":
    chat.launch()
