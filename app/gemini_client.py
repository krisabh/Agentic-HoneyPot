# app/gemini_client.py

import os

import google.generativeai as genai

_MODEL = None
def get_model():
    """
    Returns a configured Gemini GenerativeModel
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-3-flash-preview")
    
