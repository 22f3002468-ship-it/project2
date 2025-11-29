# app/browser.py
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser

from .config import get_settings
from .utils import logger, log_time


@dataclass
class RenderedPage:
    url: str
    html: str
    text: str
    is_dynamic: bool = False


async def fetch_rendered_page(url: str, force_dynamic: bool = False) -> RenderedPage:
    """
    Fetch and render a page, detecting if it needs JavaScript execution.
    
    Strategy:
    1. Try static fetch first (faster)
    2. If page seems dynamic or force_dynamic=True, use Playwright
    """
    settings = get_settings()
    
    # Try static first (unless forced)
    if not force_dynamic:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers={"User-Agent": settings.user_agent})
                resp.raise_for_status()
                html = resp.text
                
                # Check if page needs JS (has script tags that modify DOM)
                soup = BeautifulSoup(html, "lxml")
                scripts = soup.find_all("script")
                has_dynamic_scripts = any(
                    script.get("src") or ("document" in (script.string or "").lower())
                    for script in scripts
                )
                
                # If no dynamic scripts, return static version
                if not has_dynamic_scripts:
                    text = extract_visible_text(html)
                    return RenderedPage(url=url, html=html, text=text, is_dynamic=False)
        except Exception as e:
            logger.debug("Static fetch failed for %s: %s, trying Playwright", url, e)
    
    # Use Playwright for dynamic content
    async with log_time(f"render_page_dynamic {url}"):
        return await _fetch_with_playwright(url)


async def _fetch_with_playwright(url: str) -> RenderedPage:
    """Use Playwright to render JS-heavy pages."""
    settings = get_settings()
    browser: Optional[Browser] = None
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            context = await browser.new_context(
                user_agent=settings.user_agent,
                viewport={"width": 1920, "height": 1080},
            )
            page: Page = await context.new_page()
            
            # Navigate and wait for content
            await page.goto(url, wait_until="networkidle", timeout=60_000)
            
            # Wait a bit more for any delayed JS execution
            await asyncio.sleep(1)
            
            # Get rendered content
            html = await page.content()
            text = await page.inner_text("body")
            
            # Try to extract text from specific elements if body is empty
            if not text.strip():
                text = await page.evaluate("() => document.body.innerText || ''")
            
            await browser.close()
            browser = None
            
            return RenderedPage(url=url, html=html, text=text, is_dynamic=True)
            
    except Exception as e:
        logger.error("Playwright fetch failed for %s: %s", url, e)
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
        raise


def extract_visible_text(html: str) -> str:
    """
    Extract visible text from HTML using BeautifulSoup.
    Removes scripts, styles, and other non-visible content.
    """
    soup = BeautifulSoup(html, "lxml")
    
    # Remove non-visible elements
    for tag in soup(["script", "style", "noscript", "meta", "link", "head"]):
        tag.decompose()
    
    # Get text with proper spacing
    text = soup.get_text(separator=" ", strip=True)
    
    # Clean up excessive whitespace
    import re
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()
