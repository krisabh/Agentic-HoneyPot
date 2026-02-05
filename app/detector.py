# # app/detector.py

# from app.gemini_client import get_model


# def detect_scam(text: str):
#     """
#     Detect whether a message is a scam using Gemini
#     """

#     model = get_model()

#     prompt = f"""
# Analyze the message below and determine if it is a scam.

# Message:
# {text}

# Respond ONLY in JSON:
# {{
#   "scamDetected": true or false,
#   "reason": "short explanation"
# }}
# """

#     response = model.generate_content(prompt)

#     try:
#         text_resp = response.text
#         start = text_resp.find("{")
#         end = text_resp.rfind("}") + 1
#         return eval(text_resp[start:end])
#     except Exception:
#         return {
#             "scamDetected": True,
#             "reason": "Fallback due to parsing error"
#         }


# app/detector.py
import json
import re
from textwrap import dedent
#from app.gemini_client import get_model
from app.gemini_client import generate_content
from app.scam_bundle import generate_scam_bundle

def detect_scam(text: str):
    """
    Detect whether a message is a scam using Gemini
    """

    bundled = generate_scam_bundle([{"sender": "scammer", "text": text}])
    if bundled is None:
        return {
            "scamDetected": False,

            "reason": "Model request failed",
        }

    return {
        "scamDetected": bundled["scamDetected"],
        "reason": bundled["reason"],
    }