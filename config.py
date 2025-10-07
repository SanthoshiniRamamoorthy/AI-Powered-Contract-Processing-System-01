# contract_ai_agent/app/config.py

import logging

# --- Groq Configuration ---
# WARNING: Replace 'YOUR_GROQ_API_KEY' with your actual key before running.
GROQ_API_KEY = "YOUR_GROQ_API_HERE" 
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"

# --- Ollama Fallback Configuration ---
USE_OLLAMA_FALLBACK = True
# Using the gemma3:4b model you have confirmed is running locally
OLLAMA_MODEL_NAME = "gemma3:4b" 

# --- Application Configuration ---
TEMP_UPLOAD_DIR = "./temp" 
LOG_LEVEL = logging.INFO