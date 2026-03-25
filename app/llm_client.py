"""LLM client: handles all interactions with Together AI API (Free Tier)."""

import json
import re
import urllib3
import requests
from app.config import TOGETHER_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS

# Suppress SSL warnings for corporate environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"


def _call_together(messages: list, json_mode: bool = False) -> str:
    """Make a REST call to Together AI API."""
    if not TOGETHER_API_KEY:
        raise ValueError(
            "TOGETHER_API_KEY not set. Copy .env.example to .env and add your key.\n"
            "Get a free key at: https://api.together.xyz"
        )

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    response = requests.post(
        TOGETHER_API_URL, headers=headers, json=payload, verify=False, timeout=120
    )
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Send a prompt to the LLM and return the text response."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return _call_together(messages)


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """Send a prompt to the LLM and parse the JSON response."""
    system_with_json = (
        system_prompt + "\n\n"
        "IMPORTANT: Return ONLY valid JSON. No markdown, no code fences, no extra text."
    )
    messages = [
        {"role": "system", "content": system_with_json},
        {"role": "user", "content": user_prompt},
    ]
    text = _call_together(messages, json_mode=True)
    # Strip markdown code fences if present (safety fallback)
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text)
