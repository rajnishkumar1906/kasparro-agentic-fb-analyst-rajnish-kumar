"""
src/utils/llm_client.py

Enhanced MultiLLM client for Kasparro Agentic FB Analyst:
- Supports Multi-model fallback
- Embedding-based response validation
- Strong JSON extraction logic (regex-based)
- Safe fallbacks when JSON fails
- Uses `.env` automatically with load_dotenv()
"""

from dotenv import load_dotenv
load_dotenv()

import os
import json
import re
import numpy as np
import requests
from sentence_transformers import SentenceTransformer


BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


class MultiLLM:
    """
    LLM Wrapper with:
    - model fallback
    - cleaned responses
    - JSON extraction
    - embedding-based validation
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing OPENROUTER_API_KEY in your environment variables.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Kasparro-Agent"
        }

        # Fallback models (free tier)
        self.models = [
            "alibaba/tongyi-deepresearch-30b-a3b:free",
            "nvidia/nemotron-nano-12b-v2-vl:free",
            "kwaipilot/kat-coder-pro:free",
            "tngtech/deepseek-r1t2-chimera:free",
            "deepseek/deepseek-r1:free"
            "deepseek/deepseek-chat-v3-0324:free",
            "mistralai/mistral-small-3.2-24b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "x-ai/grok-4.1-fast:free",
            "meituan/longcat-flash-chat:free"
        ]

        # Embedding model for validation
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # -------------------------------------------------------------------
    # INTERNAL METHODS
    # -------------------------------------------------------------------

    def _call_model(self, model, messages, max_tokens=2000):
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }

        try:
            res = requests.post(
                BASE_URL,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=40
            )
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print(f"[LLM ERROR] {model} failed: {e}")
            return None

    def _validate_response(self, response, query):
        """Embedding-based quality validation."""

        if not response or len(response) < 10:
            return False

        negative_indicators = [
            "i cannot", "not available", "unable", "sorry",
            "limit exceed", "i don't know", "no information",
            "consult local"
        ]

        if any(x in response.lower() for x in negative_indicators):
            return False

        try:
            q_emb = self.embedder.encode([query])[0]
            r_emb = self.embedder.encode([response])[0]
            sim = np.dot(q_emb, r_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(r_emb))
            return sim > 0.25
        except:
            return len(response) > 30

    def _clean(self, text):
        if not text:
            return ""
        # DO NOT remove curly braces { } because JSON extraction needs them
        text = re.sub(r'[*#_`>-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    # -------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------

    def ask(self, system_prompt, user_prompt):
        """Returns best cleaned text after model fallback."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        for model in self.models:
            print(f"[LLM] Trying model: {model}")
            raw = self._call_model(model, messages)

            if not raw:
                continue

            cleaned = self._clean(raw)

            if self._validate_response(cleaned, user_prompt):
                print(f"[LLM] Good response from {model}")
                return cleaned

            print(f"[LLM] Poor response from {model}, trying next...")

        return "Model failed to produce a valid response."

    # ---------------------------- JSON EXTRACTION ----------------------------

    def ask_json(self, system_prompt, user_prompt):
        """Extract JSON reliably from LLM output."""

        text = self.ask(system_prompt, user_prompt)

        # 1) Try direct JSON load
        try:
            return json.loads(text)
        except:
            pass

        # 2) Try extracting ANY JSON block using regex
        json_matches = re.findall(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', text, re.DOTALL)
        for block in json_matches:
            try:
                return json.loads(block)
            except:
                continue

        # 3) Try cleaning trailing commas/brackets
        try:
            cleaned = text.replace(",}", "}").replace(",]", "]")
            return json.loads(cleaned)
        except:
            pass

        # 4) Last fallback
        return {"__raw_text": text}
