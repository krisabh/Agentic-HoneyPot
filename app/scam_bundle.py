import json
import re
from textwrap import dedent

from app.agent import AGENT_PERSONA
from app.agent_notes import SUMMARY_PROMPT
from app.gemini_client import generate_content


def _conversation_from_history(history: list) -> str:
    conversation = ""
    for msg in history:
        sender = msg.get("sender", "unknown")
        text = msg.get("text", "")
        conversation += f"{sender}: {text}\n"
    return conversation


def generate_scam_bundle(history: list) -> dict | None:
    """
    Single model call that returns scam detection, agent reply, and agent notes.
    """
    conversation = _conversation_from_history(history)
    prompt = dedent(
        f"""
        You are a scam detection classifier and conversational assistant.
        Be conservative: only mark true when the message has explicit scam indicators.
        Examples include urgency or threats, credential/OTP requests, payment
        instructions (UPI IDs or account details), phishing links/URLs,
        impersonation of banks/government/brands, or fake rewards.
        If the message is normal or you are unsure, return false.

        {AGENT_PERSONA}
        {SUMMARY_PROMPT}

        Conversation:
        {conversation}

        Respond ONLY in JSON:
        {{
          "scamDetected": true or false,
          "confidence": 0.0-1.0,
          "reason": "short explanation"
          
        }}
        """
    ).strip()

    try:
        response = generate_content(prompt)
    except Exception:
        return None

    text_resp = getattr(response, "text", "") or ""
    json_match = re.search(r"\{.*\}", text_resp, re.DOTALL)
    if not json_match:
        return None

    try:
        parsed = json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return None

    scam_detected = bool(parsed.get("scamDetected", False))
    confidence = parsed.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    if scam_detected and confidence < 0.6:
        scam_detected = False

    return {
        "scamDetected": scam_detected,
        "reason": parsed.get("reason", "No reason provided"),
        "agentReply": parsed.get("agentReply", "") or "",
        "agentNotes": parsed.get("agentNotes", "") or "",
    }
