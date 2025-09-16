# enhancements/llm_client.py
import os
import re
import time
try:
    import openai
except Exception:
    openai = None

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

def is_llm_enabled():
    return OPENAI_KEY is not None and openai is not None

# simple PII redaction for emails and phone numbers
_email_re = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')
_phone_re = re.compile(r'(\+?\d[\d\-\s]{6,}\d)')

def redact_pii(text: str) -> str:
    if not text:
        return text
    text = _email_re.sub("[REDACTED_EMAIL]", text)
    text = _phone_re.sub("[REDACTED_PHONE]", text)
    return text

def query_openai(prompt, model="gpt-3.5-turbo", max_tokens=300, retries=2, timeout=10):
    """
    Query OpenAI ChatCompletion with basic PII redaction and retries.
    Returns dict: {'answer': str} on success or {'error': str} on failure.
    """
    if not is_llm_enabled():
        return {"error": "LLM not configured"}

    openai.api_key = OPENAI_KEY
    safe_prompt = redact_pii(prompt)

    for attempt in range(retries + 1):
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[{"role":"system","content":"You are an assistant specialized in job placements, interview tips and aptitude practice. Be concise and factual."},
                          {"role":"user","content": safe_prompt}],
                max_tokens=max_tokens,
                temperature=0.25,
                timeout=timeout
            )
            text = resp.choices[0].message.content.strip()
            return {"answer": text, "raw": resp}
        except Exception as e:
            last_err = str(e)
            time.sleep(2 ** attempt)
    return {"error": f"LLM request failed after retries: {last_err}"}
