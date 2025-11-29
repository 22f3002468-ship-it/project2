# app/solver.py
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
from pydantic import ValidationError

from .browser import RenderedPage, fetch_rendered_page, extract_visible_text
from .config import Settings, get_settings
from .data_processor import DataProcessor
from .models import SolverAnswer, SubmitResult
from .utils import logger, within_deadline


SUBMIT_URL_RE = re.compile(
    r"Post your answer to\s+(https?://[^\s\"']+)", re.IGNORECASE
)
API_URL_RE = re.compile(
    r"(?:API|api|endpoint|url)[:\s]+(https?://[^\s\"'<>]+)", re.IGNORECASE
)


@dataclass
class QuizSolver:
    settings: Settings

    def __post_init__(self):
        # LLM client (works with official OpenAI or custom base URL)
        self.llm_client = AsyncOpenAI(
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url or None,
        )
        self.http_client = httpx.AsyncClient(
            timeout=self.settings.http_timeout,
            headers={"User-Agent": self.settings.user_agent},
        )
        self.data_processor = DataProcessor(self.http_client)

    async def aclose(self):
        await self.http_client.aclose()

    # ---------- Top-level loop ----------

    async def run_quiz_loop(
        self,
        initial_url: str,
        email: str,
        secret: str,
        deadline,
    ) -> None:
        """
        Repeatedly:
          - visit quiz URL
          - solve it
          - POST answer to submit URL
          - follow next URL (if any)
          - stop when no URL or deadline exceeded
        """
        url: Optional[str] = initial_url

        try:
            while url and within_deadline(deadline):
                logger.info("Solving quiz URL: %s", url)

                page = await fetch_rendered_page(url)
                submit_url = self._extract_submit_url(page)

                answer = await self.solve_single_quiz(page)
                if answer is None:
                    logger.error("Solver returned no answer for %s", url)
                    break

                payload = {
                    "email": email,
                    "secret": secret,
                    "url": url,
                    "answer": answer.answer,
                }
                payload_bytes = json.dumps(payload).encode("utf-8")
                if len(payload_bytes) > self.settings.max_payload_bytes:
                    logger.error(
                        "Payload too large (%d bytes) for %s", len(payload_bytes), url
                    )
                    break

                # Submit answer
                result = await self._submit_answer(submit_url, payload)
                logger.info(
                    "Submit result for %s: correct=%s next_url=%s reason=%s",
                    url,
                    result.correct,
                    result.url,
                    result.reason,
                )

                # Handle wrong answers with retry logic
                # Spec: "you are allowed to re-submit, as long as it is still within 3 minutes"
                # Spec: "you may receive the next url to proceed to. If so, you can choose to skip to that URL instead"
                max_retries = 2  # Allow 1 retry (2 total attempts)
                retry_count = 0
                
                while not result.correct and retry_count < max_retries and within_deadline(deadline):
                    # If we have a next URL, we can skip or retry
                    # Strategy: retry once if no next URL, or if we have time
                    if result.url:
                        # We have a next URL - decide: retry or skip?
                        # Retry if we have time and it's the first attempt
                        if retry_count == 0:
                            logger.info("Answer incorrect but next URL available. Retrying once...")
                            # Re-solve the quiz
                            page = await fetch_rendered_page(url)
                            submit_url = self._extract_submit_url(page)
                            answer = await self.solve_single_quiz(page)
                            if answer:
                                payload = {
                                    "email": email,
                                    "secret": secret,
                                    "url": url,
                                    "answer": answer.answer,
                                }
                                result = await self._submit_answer(submit_url, payload)
                                logger.info(
                                    "Retry result for %s: correct=%s next_url=%s",
                                    url,
                                    result.correct,
                                    result.url,
                                )
                                retry_count += 1
                                # If still wrong, proceed to next URL
                                if not result.correct and result.url:
                                    url = str(result.url)
                                    break
                        else:
                            # Already retried, proceed to next URL
                            url = str(result.url)
                            break
                    else:
                        # No next URL, must retry
                        logger.info("Answer incorrect, retrying...")
                        page = await fetch_rendered_page(url)
                        submit_url = self._extract_submit_url(page)
                        answer = await self.solve_single_quiz(page)
                        if answer:
                            payload = {
                                "email": email,
                                "secret": secret,
                                "url": url,
                                "answer": answer.answer,
                            }
                            result = await self._submit_answer(submit_url, payload)
                            logger.info(
                                "Retry result for %s: correct=%s",
                                url,
                                result.correct,
                            )
                            retry_count += 1
                        else:
                            break  # Can't solve, give up

                # Handle correct answer or final state
                if result.correct:
                    if result.url:
                        url = str(result.url)
                    else:
                        # Quiz complete, no more URLs
                        url = None
                        break
                elif result.url:
                    # Wrong but have next URL - proceed
                    url = str(result.url)
                else:
                    # Wrong, no next URL, max retries reached
                    logger.warning("Cannot proceed from %s", url)
                    break

        finally:
            await self.aclose()

    # ---------- Single quiz ----------

    async def solve_single_quiz(self, page: RenderedPage) -> Optional[SolverAnswer]:
        """
        Generic LLM-based solver:
        - Extract question text from page
        - Detect and download relevant data files
        - Detect API endpoints if mentioned
        - Ask LLM to return JSON with {answer, answer_type}
        """
        soup = BeautifulSoup(page.html, "lxml")
        visible_text = extract_visible_text(page.html)
        
        # Get full question text (but limit for LLM context)
        question_text = visible_text[:8000]  # Increased context window
        
        # Collect potential data file links (CSV, JSON, PDF, etc.)
        file_urls: List[str] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(page.url, href)
            text = a.get_text(strip=True) or ""
            # Check for file extensions or download keywords
            if any(
                k in href.lower() or k in text.lower()
                for k in (".csv", ".json", ".txt", ".pdf", ".xlsx", ".xls", "download", "file", "data")
            ):
                file_urls.append(full_url)
        
        # Also check for embedded data URLs in text
        data_url_pattern = re.compile(r"(https?://[^\s\"'<>]+\.(csv|json|txt|pdf|xlsx|xls))", re.IGNORECASE)
        for match in data_url_pattern.finditer(visible_text):
            file_urls.append(match.group(1))
        
        # Remove duplicates while preserving order
        file_urls = list(dict.fromkeys(file_urls))
        
        # Download and process files
        processed_files: List[Dict[str, Any]] = []
        for url in file_urls[:10]:  # Limit to 10 files to avoid timeout
            try:
                file_info = await self.data_processor.download_file(url)
                processed_files.append(file_info)
            except Exception as e:
                logger.warning("Failed to process file %s: %s", url, e)
        
        # Check for API endpoints mentioned in the question
        api_data: Optional[Dict[str, Any]] = None
        api_matches = API_URL_RE.findall(visible_text)
        if api_matches:
            api_url = api_matches[0]
            try:
                logger.info("Found API endpoint: %s", api_url)
                resp = await self.http_client.get(api_url, timeout=30.0)
                resp.raise_for_status()
                try:
                    api_data = resp.json()
                except Exception:
                    api_data = {"text": resp.text[:5000]}
                logger.info("Fetched API data from %s", api_url)
            except Exception as e:
                logger.warning("Failed to fetch API data from %s: %s", api_url, e)
        
        # Call LLM with all collected information
        llm_answer = await self._call_llm_for_answer(
            question_text=question_text,
            processed_files=processed_files,
            api_data=api_data,
        )
        return llm_answer

    # ---------- Helper: submit ----------

    async def _submit_answer(self, submit_url: str, payload: Dict[str, Any]) -> SubmitResult:
        try:
            resp = await self.http_client.post(submit_url, json=payload)
        except Exception as e:
            logger.error("Error submitting to %s: %s", submit_url, e)
            return SubmitResult(correct=False, url=None, reason=str(e), raw_response=None)

        try:
            data = resp.json()
        except Exception:
            data = {"raw_text": resp.text}

        return SubmitResult(
            correct=bool(data.get("correct", False)),
            url=data.get("url"),
            reason=data.get("reason"),
            raw_response=data,
        )

    # ---------- Helper: parse submit URL ----------

    def _extract_submit_url(self, page: RenderedPage) -> str:
        """
        Parse 'Post your answer to https://.../submit' from page text.
        Fallback: /submit on same origin.
        """
        match = SUBMIT_URL_RE.search(page.text) or SUBMIT_URL_RE.search(
            extract_visible_text(page.html)
        )
        if match:
            submit_url = match.group(1).strip().rstrip(".")
            logger.info("Found submit URL: %s", submit_url)
            return submit_url

        # Fallback: heuristic
        logger.warning("Submit URL not found in page text; guessing /submit")
        base = re.match(r"^(https?://[^/]+)", page.url)
        if not base:
            raise RuntimeError(f"Cannot infer submit URL for {page.url}")
        return base.group(1) + "/submit"

    # ---------- Helper: LLM call ----------

    async def _call_llm_for_answer(
        self,
        question_text: str,
        processed_files: List[Dict[str, Any]],
        api_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[SolverAnswer]:
        """
        Ask LLM to produce a JSON answer object.
        LLM MUST respond with: {"answer": ..., "answer_type": "..."}.
        """
        # Format files section
        files_section = []
        for f in processed_files:
            files_section.append(self.data_processor.format_file_info_for_llm(f))
        files_text = "\n\n".join(files_section) if files_section else "No data files found."

        # Format API data section
        api_text = ""
        if api_data:
            if isinstance(api_data, dict):
                api_text = f"API Response Data:\n{json.dumps(api_data, indent=2)[:5000]}\n"
            else:
                api_text = f"API Response:\n{str(api_data)[:5000]}\n"

        system_prompt = (
            "You are an expert data analyst and problem solver. Your task is to solve quiz questions "
            "that involve data sourcing, preparation, analysis, and visualization.\n\n"
            "You will receive:\n"
            "1. The quiz question text from the webpage\n"
            "2. Processed data from downloaded files (CSV, JSON, PDF, Excel, etc.)\n"
            "3. API response data (if applicable)\n\n"
            "Your approach:\n"
            "1. Carefully read and understand the question\n"
            "2. Identify what data is needed to answer it\n"
            "3. Process and analyze the provided data files\n"
            "4. Perform any required calculations, filtering, aggregation, or transformations\n"
            "5. If visualization is needed, describe what should be visualized\n"
            "6. Determine the correct answer based on your analysis\n\n"
            "IMPORTANT OUTPUT FORMAT:\n"
            "You MUST return ONLY a valid JSON object with exactly these keys:\n"
            '  - "answer": the final answer value. Can be:\n'
            "    * A number (int or float) for numerical answers\n"
            "    * A string for text answers\n"
            "    * A boolean (true/false) for yes/no questions\n"
            "    * An object/dict for complex structured answers\n"
            "    * A base64-encoded string (with data URI prefix) for file attachments\n"
            '  - "answer_type": one of "number", "string", "bool", "object", or "file_base64"\n\n'
            "Do NOT include explanations, reasoning, or any text outside the JSON object.\n"
            "The response must be valid JSON only."
        )

        user_prompt_parts = [
            "QUIZ QUESTION:\n",
            question_text,
            "\n\n" + "="*50 + "\n\n",
        ]
        
        if files_text != "No data files found.":
            user_prompt_parts.extend([
                "DATA FILES:\n",
                files_text,
                "\n\n" + "="*50 + "\n\n",
            ])
        
        if api_text:
            user_prompt_parts.extend([
                "API DATA:\n",
                api_text,
                "\n\n" + "="*50 + "\n\n",
            ])
        
        user_prompt_parts.append(
            "Return ONLY a JSON object with 'answer' and 'answer_type' keys. No other text."
        )
        
        user_prompt = "".join(user_prompt_parts)

        try:
            resp = await self.llm_client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for deterministic answers
                max_tokens=2048,  # Increased for complex answers
            )
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            return None

        try:
            content = resp.choices[0].message.content or "{}"
            logger.debug("LLM response: %s", content[:500])
        except (IndexError, AttributeError) as e:
            logger.error("Unexpected LLM response structure: %s", e)
            return None

        try:
            parsed = json.loads(content)
            answer = parsed.get("answer")
            answer_type = parsed.get("answer_type", "string")
            
            # Validate answer_type
            valid_types = {"number", "string", "bool", "object", "file_base64"}
            if answer_type not in valid_types:
                logger.warning("Invalid answer_type '%s', defaulting to 'string'", answer_type)
                answer_type = "string"
            
            return SolverAnswer(answer=answer, answer_type=answer_type)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error("Failed to parse LLM JSON answer: %s content=%s", e, content)
            # Try to extract JSON from response if it's wrapped in text
            json_match = re.search(r'\{[^{}]*"answer"[^{}]*\}', content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    return SolverAnswer(
                        answer=parsed.get("answer"),
                        answer_type=parsed.get("answer_type", "string")
                    )
                except Exception:
                    pass
            return None
