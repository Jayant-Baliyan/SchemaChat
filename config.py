import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR=Path(__file__).parent

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#LLM_MODEL = "llama-3.3-70b-versatile"
#LLM_MODEL="qwen/qwen3.6-27b"
#LLM_MODEL="openai/gpt-oss-20b"
LLM_MODEL="openai/gpt-oss-120b"
#LLM_MODEL="llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0