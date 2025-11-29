from __future__ import annotations

import json
from typing import Any, Dict

from pydantic import AnyUrl
from openai import OpenAI

from .config import settings
from .models import SolverResult
from .utils import logger


client = OpenAI(api_key=settings.openai_api_key)


SYSTEM_PROMPT = """
You are a senior data engineer helping solve auto-graded quiz tasks.

You are given:
- A quiz HTML page (after JavaScript has executed).
- The URL of that page.
- The student's email and secret (used for POSTing answers).
Your job is to:
1. Understand the question from the HTML.
2. Identify the endpoint/URL where the answer must be submitted.
3. Determine what the JSON payload must look like.
4. Compute the correct answer.
5. Return ONLY a JSON object with this exact schema:

{
  "submit_url": "https://.../submit",
  "answer": <any JSON-serializable value>,
  "extra_payload": { "field1": "value1", ... },
  "done": false
}

Rules:
- Do NOT include comments or backticks.
- "submit_url" MUST be a URL in the page instructions.
- "extra_payload" should be any extra fields required by the spec
  (for example, sometimes they want "answer" inside another object).
- If the quiz chain is finished and no further submissions are required,
  set "done": true (but still return a valid payload for the current quiz).
- Never invent URLs; use only those present in the HTML.
"""


def _build_user_prompt(
    html: str,
    quiz_url: str,
    email: str,
    secret: str,
) -> str:
    return f"""
You must read and interpret this quiz page.

Current quiz URL:
{quiz_url}

Student email: {email}
Student secret: {secret}

FULL HTML (after JS execution):

<<<HTML_START>>>
{html}
<<<HTML_END>>>

From this HTML, determine:
- What the question is asking
- Where to submit the answer
- What the JSON payload must look like

Return ONLY a JSON object with keys:
submit_url, answer, extra_payload, done

Important:
- Include 'email', 'secret', and 'url' in extra_payload if the page requires them.
- If the specification shows an example payload, follow it exactly.
"""


def _parse_llm_json(text: str) -> Dict[str, Any]:
    """
    LLM sometimes wraps JSON with extra text; try to extract the JSON object.
    """
    text = text.strip()
    # Try raw first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to locate the first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        return json.loads(snippet)

    raise ValueError("Could not parse JSON from LLM output")


def solve_quiz_from_html(
    html: str,
    quiz_url: str,
    email: str,
    secret: str,
) -> SolverResult:
    """
    Uses OpenAI to figure out submit_url, answer, and extra_payload.
    """
    logger.info("Calling LLM to interpret quiz page: %s", quiz_url)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(html, quiz_url, email, secret)},
    ]

    resp = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0,
    )

    content = resp.choices[0].message.content
    logger.debug("LLM raw response: %s", content)

    data = _parse_llm_json(content)

    return SolverResult(
        submit_url=AnyUrl(str(data["submit_url"])),
        answer=data["answer"],
        extra_payload=data.get("extra_payload", {}),
        done=bool(data.get("done", False)),
    )
