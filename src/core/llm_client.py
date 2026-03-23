import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from ollama import Client as OllamaClient

# Load .env
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Read Configuration
PROVIDER = os.getenv("PROVIDER", "openai").lower()
MODEL = os.getenv("MODEL", "gpt-5-nano")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
TIMEOUT = 60

Message = Dict[str, str]

def chat(messages: List[Message]) -> str:
    if not messages:
        raise ValueError("Messages list cannot be empty")
    if PROVIDER=='openai':
        return _call_openai(messages)
    if PROVIDER=='google':
        return _call_gemini(messages)
    if PROVIDER=='ollama':
        return _call_ollama(messages)

def _call_openai(messages: List[Message]) -> str:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in environment variables")
    client = OpenAI(api_key=OPENAI_API_KEY,timeout=TIMEOUT)
    response = client.chat.completions.create(model=MODEL,messages=messages)
    return response.choices[0].message.content

def _call_gemini(messages: List[Message]) -> str:
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set in the .env file")

    client = genai.Client(api_key=GOOGLE_API_KEY)

    system_text = ""
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        elif msg["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

    config = genai.types.GenerateContentConfig(
        temperature=0,
        system_instruction=system_text if system_text else None,
    )
    response = client.models.generate_content(
        model=MODEL, contents=contents, config=config
    )
    return response.candidates[0].content.parts[0].text

def _call_ollama(messages: List[Message]) -> str:
    """Call local Ollama API."""
    client = OllamaClient(host=OLLAMA_HOST)
    response = client.chat(model=MODEL, messages=messages)
    if not response.message or not response.message.content:
        raise RuntimeError("Ollama returned empty response. Is Ollama running?")
    return response.message.content

