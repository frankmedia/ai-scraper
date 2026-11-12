#!/usr/bin/env python3
"""AI Scraper: batch prompts through Perplexity or ChatGPT in a real browser
and save each answer with the sources it cites.

Usage:
    python scraper.py --site perplexity --prompts-csv prompts.csv
    python scraper.py --site chatgpt --prompts-csv prompts.csv --out-jsonl out.jsonl

The browser is driven with Selenium. Log in manually when the script asks;
no credentials are stored. Keep the pace polite and check the target site's
terms of service before running large batches.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

log = logging.getLogger("ai_scraper")

DEFAULT_PROMPTS = [
    "What is AI consulting?",
    "How to start an AI agency?",
]

URL_RE = re.compile(r"https?://[^\s)\]>\"']+")


# --------------------------------------------------------------------------- #
# Site definitions
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Site:
    name: str
    url: str
    input_selectors: Sequence[str]
    answer_selectors: Sequence[str]
    citation_selectors: Sequence[str]
    internal_domains: Sequence[str]
    warmup_prompts: Sequence[str] = ()
    min_answer_chars: int = 150


SITES = {
    "perplexity": Site(
        name="Perplexity",
        url="https://www.perplexity.ai/",
        input_selectors=(
            "textarea[placeholder*='Ask']",
            "div[contenteditable='true'][role='textbox']",
            "textarea",
        ),
        answer_selectors=(
            "[data-testid='answer']",
            ".prose",
        ),
        citation_selectors=(
            "[data-testid='answer'] a[href]",
            ".prose a[href]",
        ),
        internal_domains=("perplexity.ai",),
    ),
    "chatgpt": Site(
        name="ChatGPT",
        url="https://chatgpt.com/",
        input_selectors=(
            "div#prompt-textarea",
            "textarea[placeholder*='Message']",
            "div[contenteditable='true']",
        ),
        answer_selectors=(
            "div[data-message-author-role='assistant']",
            ".markdown",
        ),
        citation_selectors=(
            "div[data-message-author-role='assistant'] a[href]",
        ),
        internal_domains=("chatgpt.com", "openai.com"),
        warmup_prompts=("Hello",),
    ),
}


@dataclass
class Settings:
    answer_timeout: float = 180.0
    stable_seconds: float = 8.0
    page_load_timeout: float = 30.0
    prompt_delay: tuple[float, float] = (3.0, 6.0)
    typing_delay: tuple[float, float] = (0.03, 0.08)
    headless: bool = False


@dataclass
class Result:
    idx: int
    prompt: str
    answer: str = ""
    citations: List[str] = field(default_factory=list)
    error: str = ""

    def to_row(self) -> dict:
        return {
            "idx": self.idx,
            "prompt": self.prompt,
            "answer": self.answer,
            "citations": "; ".join(self.citations),
            "error": self.error,
        }


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def read_prompts(csv_path: Optional[str]) -> List[str]:
    """Read one prompt per row from the first column of a CSV file."""
    if not csv_path:
        return list(DEFAULT_PROMPTS)
    prompts: List[str] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if row and row[0].strip():
                prompts.append(row[0].strip())
    return prompts


def sleep_between(bounds: tuple[float, float]) -> None:
    time.sleep(random.uniform(*bounds))


def build_driver(settings: Settings) -> WebDriver:
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,1000")
    if settings.headless:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(settings.page_load_timeout)
    return driver


def find_visible(driver: WebDriver, selectors: Iterable[str]) -> Optional[WebElement]:
    """Return the first displayed element matching any selector, in order."""
    for sel in selectors:
        for el in driver.find_elements(By.CSS_SELECTOR, sel):
            try:
                if el.is_displayed():
                    return el
            except WebDriverException:
                continue
    return None


def wait_for_page(driver: WebDriver, timeout: float) -> None:
    """Wait until the tab title no longer looks like an interstitial."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        title = driver.title.lower()
        if "just a moment" not in title and "loading" not in title:
            return
        time.sleep(1)
    log.warning("Page still showed an interstitial after %.0fs", timeout)


def needs_login(driver: WebDriver) -> bool:
    title = driver.title.lower()
    url = driver.current_url.lower()
    return any(k in title for k in ("log in", "login", "sign in")) or "/auth" in url


def wait_for_manual_login() -> None:
    print("\nLogin required. Sign in in the browser window, then press Enter here.")
    input()
    time.sleep(2)


def type_prompt(element: WebElement, text: str, settings: Settings) -> None:
    element.click()
    time.sleep(random.uniform(0.3, 0.8))
    for ch in text:
        element.send_keys(ch)
        sleep_between(settings.typing_delay)
    time.sleep(random.uniform(0.3, 0.6))
    element.send_keys(Keys.RETURN)


def latest_answer_text(driver: WebDriver, site: Site) -> str:
    """Text of the last matching answer container, or empty string."""
    for sel in site.answer_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, sel)
        for el in reversed(elements):
            try:
                text = el.text.strip()
            except WebDriverException:
                continue
            if len(text) >= site.min_answer_chars:
                return text
    return ""


def wait_for_answer(driver: WebDriver, site: Site, settings: Settings) -> str:
    """Poll until the answer text stops growing for `stable_seconds`."""
    deadline = time.time() + settings.answer_timeout
    last_text, last_len, stable_since = "", 0, None
    while time.time() < deadline:
        text = latest_answer_text(driver, site)
        if text:
            if len(text) != last_len:
                last_text, last_len, stable_since = text, len(text), time.time()
                log.debug("Answer at %d chars", last_len)
            elif stable_since and time.time() - stable_since >= settings.stable_seconds:
                return last_text
        time.sleep(1)
    if last_text:
        log.warning("Timed out while answer was still changing; keeping %d chars", last_len)
        return last_text
    raise TimeoutError(f"No answer appeared within {settings.answer_timeout:.0f}s")


def clean_url(url: str) -> str:
    url = url.split("#", 1)[0]
    return url.rstrip(").,;'\"")


def extract_citations(driver: WebDriver, site: Site, answer_text: str) -> List[str]:
    """Collect external links from the answer container and from the text."""
    found: set[str] = set()
    for sel in site.citation_selectors:
        for a in driver.find_elements(By.CSS_SELECTOR, sel):
            try:
                href = a.get_attribute("href") or ""
            except WebDriverException:
                continue
            if href.startswith("http"):
                found.add(clean_url(href))
    for match in URL_RE.findall(answer_text):
        found.add(clean_url(match))
    external = [u for u in found if not any(d in u for d in site.internal_domains)]
    return sorted(external)


# --------------------------------------------------------------------------- #
# Core flow
# --------------------------------------------------------------------------- #
def ask(driver: WebDriver, site: Site, prompt: str, settings: Settings) -> tuple[str, List[str]]:
    driver.get(site.url)
    sleep_between((2.0, 4.0))
    wait_for_page(driver, settings.page_load_timeout)

    if needs_login(driver):
        wait_for_manual_login()
        sleep_between((3.0, 6.0))

    box = find_visible(driver, site.input_selectors)
    if box is None:
        driver.refresh()
        time.sleep(3)
        box = find_visible(driver, site.input_selectors)
    if box is None:
        path = f"debug_no_input_{int(time.time())}.png"
        driver.save_screenshot(path)
        raise RuntimeError(f"Input box not found; screenshot saved to {path}")

    type_prompt(box, prompt, settings)
    answer = wait_for_answer(driver, site, settings)
    citations = extract_citations(driver, site, answer)
    return answer, citations


def run(site_key: str, prompts: List[str], settings: Settings) -> List[Result]:
    site = SITES[site_key]
    driver = build_driver(settings)
    results: List[Result] = []
    try:
        for warm in site.warmup_prompts:
            try:
                log.info("Warm-up prompt: %s", warm)
                ask(driver, site, warm, settings)
            except Exception as exc:  # noqa: BLE001 - warm-up is best effort
                log.info("Warm-up skipped: %s", exc)
            sleep_between(settings.prompt_delay)

        for i, prompt in enumerate(prompts, 1):
            log.info("[%d/%d] %s", i, len(prompts), prompt[:70])
            result = Result(idx=i, prompt=prompt)
            try:
                result.answer, result.citations = ask(driver, site, prompt, settings)
                log.info("Captured %d chars, %d citations", len(result.answer), len(result.citations))
            except KeyboardInterrupt:
                log.warning("Interrupted; saving what we have")
                results.append(result)
                break
            except Exception as exc:  # noqa: BLE001 - record and continue
                result.error = str(exc)
                log.error("Prompt %d failed: %s", i, exc)
            results.append(result)
            if i < len(prompts):
                sleep_between(settings.prompt_delay)
    finally:
        driver.quit()
    return results


def write_outputs(results: List[Result], out_csv: str, out_jsonl: Optional[str]) -> None:
    rows = [r.to_row() for r in results]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["idx", "prompt", "answer", "citations", "error"])
        writer.writeheader()
        writer.writerows(rows)
    log.info("Saved %d rows to %s", len(rows), out_csv)
    if out_jsonl:
        with open(out_jsonl, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        log.info("Saved JSONL to %s", out_jsonl)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Batch prompts through Perplexity or ChatGPT and save answers with citations.")
    parser.add_argument("--site", choices=sorted(SITES), default="perplexity")
    parser.add_argument("--prompts-csv", help="CSV with one prompt per row (first column)")
    parser.add_argument("--limit", type=int, help="Only process the first N prompts")
    parser.add_argument("--out-csv", default="results.csv")
    parser.add_argument("--out-jsonl")
    parser.add_argument("--answer-timeout", type=float, default=180, help="Seconds to wait for each answer")
    parser.add_argument("--stable-seconds", type=float, default=8, help="Seconds of unchanged text before an answer is considered complete")
    parser.add_argument("--headless", action="store_true", help="Run Chrome headless (login prompts will not work)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    prompts = read_prompts(args.prompts_csv)
    if args.limit:
        prompts = prompts[: args.limit]
    if not prompts:
        log.error("No prompts found")
        return 1

    settings = Settings(
        answer_timeout=args.answer_timeout,
        stable_seconds=args.stable_seconds,
        headless=args.headless,
    )
    log.info("Running %d prompts on %s", len(prompts), SITES[args.site].name)
    results = run(args.site, prompts, settings)
    write_outputs(results, args.out_csv, args.out_jsonl)
    failed = sum(1 for r in results if r.error)
    log.info("Done: %d ok, %d failed", len(results) - failed, failed)
    return 0 if failed < len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
