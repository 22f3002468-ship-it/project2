# app/data_processor.py
from __future__ import annotations

import base64
import csv
import io
import json
import re
from typing import Any, Dict, List, Optional, Union

import httpx
from bs4 import BeautifulSoup

from .config import get_settings
from .utils import logger


class DataProcessor:
    """Process various data formats: CSV, JSON, PDF, text, etc."""

    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.settings = get_settings()

    async def download_file(self, url: str, max_size: int = 10_000_000) -> Dict[str, Any]:
        """
        Download a file and return its processed content.
        Returns: {
            "url": str,
            "content_type": str,
            "size": int,
            "preview": str,  # text preview or summary
            "data": Any,  # parsed data if applicable
        }
        """
        try:
            resp = await self.http_client.get(url, timeout=30.0)
            resp.raise_for_status()
            
            content_type = resp.headers.get("content-type", "").lower()
            content = resp.content
            
            if len(content) > max_size:
                logger.warning("File %s too large (%d bytes), truncating", url, len(content))
                content = content[:max_size]
            
            result = {
                "url": url,
                "content_type": content_type,
                "size": len(content),
                "preview": "",
                "data": None,
            }
            
            # Process based on content type
            if "csv" in content_type or url.endswith(".csv"):
                result.update(self._process_csv(content))
            elif "json" in content_type or url.endswith(".json"):
                result.update(self._process_json(content))
            elif "pdf" in content_type or url.endswith(".pdf"):
                result.update(self._process_pdf(content))
            elif "text" in content_type or url.endswith((".txt", ".md")):
                result.update(self._process_text(content))
            elif "html" in content_type or url.endswith((".html", ".htm")):
                result.update(self._process_html(content))
            elif "excel" in content_type or "spreadsheet" in content_type or url.endswith((".xlsx", ".xls")):
                result.update(self._process_excel(content))
            else:
                # Unknown type, try to decode as text
                result.update(self._process_text(content))
            
            return result
            
        except Exception as e:
            logger.error("Failed to download/process %s: %s", url, e)
            return {
                "url": url,
                "content_type": "unknown",
                "size": 0,
                "preview": f"[Error: {str(e)}]",
                "data": None,
            }

    def _process_csv(self, content: bytes) -> Dict[str, Any]:
        """Process CSV content."""
        try:
            text = content.decode("utf-8", errors="replace")
            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            
            preview_lines = []
            if rows:
                # Header
                preview_lines.append("Headers: " + ", ".join(rows[0].keys()))
                # First few rows
                for i, row in enumerate(rows[:5]):
                    preview_lines.append(f"Row {i+1}: {dict(row)}")
                if len(rows) > 5:
                    preview_lines.append(f"... ({len(rows) - 5} more rows)")
            
            preview = "\n".join(preview_lines)
            return {
                "preview": preview,
                "data": rows,
            }
        except Exception as e:
            return {
                "preview": f"[CSV parse error: {e}]",
                "data": None,
            }

    def _process_json(self, content: bytes) -> Dict[str, Any]:
        """Process JSON content."""
        try:
            text = content.decode("utf-8", errors="replace")
            data = json.loads(text)
            
            # Create preview
            if isinstance(data, dict):
                preview = f"JSON object with keys: {', '.join(list(data.keys())[:10])}"
                if len(data) > 10:
                    preview += f" ... ({len(data) - 10} more keys)"
            elif isinstance(data, list):
                preview = f"JSON array with {len(data)} items"
                if data:
                    preview += f"\nFirst item: {json.dumps(data[0], indent=2)[:500]}"
            else:
                preview = f"JSON value: {str(data)[:500]}"
            
            return {
                "preview": preview,
                "data": data,
            }
        except Exception as e:
            return {
                "preview": f"[JSON parse error: {e}]",
                "data": None,
            }

    def _process_pdf(self, content: bytes) -> Dict[str, Any]:
        """Process PDF content (basic extraction)."""
        try:
            # Try to extract text using basic PDF parsing
            # For production, you might want to use PyPDF2 or pdfplumber
            preview = f"[PDF file, {len(content)} bytes]"
            
            # Try to extract text if possible (basic approach)
            try:
                import PyPDF2
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text_parts = []
                for i, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"Page {i+1}:\n{text[:1000]}")
                if text_parts:
                    preview = "\n\n".join(text_parts)
            except ImportError:
                # PyPDF2 not available, use basic info
                pass
            except Exception as e:
                logger.debug("PDF text extraction failed: %s", e)
            
            return {
                "preview": preview,
                "data": None,  # PDF data not parsed by default
            }
        except Exception as e:
            return {
                "preview": f"[PDF error: {e}]",
                "data": None,
            }

    def _process_text(self, content: bytes) -> Dict[str, Any]:
        """Process plain text content."""
        try:
            text = content.decode("utf-8", errors="replace")
            preview = text[:6000]  # First 6000 chars
            if len(text) > 6000:
                preview += f"\n... ({len(text) - 6000} more characters)"
            return {
                "preview": preview,
                "data": text,
            }
        except Exception as e:
            return {
                "preview": f"[Text decode error: {e}]",
                "data": None,
            }

    def _process_html(self, content: bytes) -> Dict[str, Any]:
        """Process HTML content."""
        try:
            text = content.decode("utf-8", errors="replace")
            soup = BeautifulSoup(text, "lxml")
            
            # Remove scripts and styles
            for tag in soup(["script", "style"]):
                tag.decompose()
            
            # Extract text
            text_content = soup.get_text(separator=" ", strip=True)
            preview = text_content[:6000]
            if len(text_content) > 6000:
                preview += f"\n... ({len(text_content) - 6000} more characters)"
            
            return {
                "preview": preview,
                "data": text_content,
            }
        except Exception as e:
            return {
                "preview": f"[HTML parse error: {e}]",
                "data": None,
            }

    def _process_excel(self, content: bytes) -> Dict[str, Any]:
        """Process Excel content."""
        try:
            # Try to use openpyxl or pandas if available
            try:
                import pandas as pd
                df = pd.read_excel(io.BytesIO(content), nrows=100)  # First 100 rows
                preview = f"Excel file with {len(df)} rows, {len(df.columns)} columns\n"
                preview += f"Columns: {', '.join(df.columns.tolist())}\n"
                preview += f"First few rows:\n{df.head().to_string()}"
                return {
                    "preview": preview,
                    "data": df.to_dict("records"),
                }
            except ImportError:
                return {
                    "preview": f"[Excel file, {len(content)} bytes - pandas not available]",
                    "data": None,
                }
        except Exception as e:
            return {
                "preview": f"[Excel parse error: {e}]",
                "data": None,
            }

    def format_file_info_for_llm(self, file_info: Dict[str, Any]) -> str:
        """Format file information for LLM consumption."""
        lines = [
            f"FILE: {file_info.get('url', 'unknown')}",
            f"Type: {file_info.get('content_type', 'unknown')}",
            f"Size: {file_info.get('size', 0)} bytes",
            "",
            "CONTENT PREVIEW:",
            file_info.get("preview", "[No preview available]"),
        ]
        
        # Add data summary if available
        data = file_info.get("data")
        if data is not None:
            if isinstance(data, list):
                lines.append(f"\nData: List with {len(data)} items")
            elif isinstance(data, dict):
                lines.append(f"\nData: Dict with {len(data)} keys")
            else:
                lines.append(f"\nData: {type(data).__name__}")
        
        return "\n".join(lines)

