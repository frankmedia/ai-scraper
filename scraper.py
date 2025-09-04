# scraper.py - Clean Perplexity AI Scraper
import time
import random
import csv
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

DEFAULT_PROMPTS = [
    "What is AI consulting?",
    "How to start an AI agency?",
]

# Optimized timing settings
ANSWER_WAIT_SECONDS = 120  # Much longer wait for ChatGPT
PER_PROMPT_DELAY = (3.0, 6.0)  # Shorter delays

def read_prompts(csv_path: Optional[str]) -> List[str]:
    """Read prompts from CSV file"""
    if not csv_path:
        return DEFAULT_PROMPTS[:]
    
    prompts: List[str] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            p = row[0].strip()
            if p:
                prompts.append(p)
    return prompts

def human_like_typing(driver, element, text):
    """Type text like a human with random delays"""
    try:
        # Try to click the element
        element.click()
    except:
        # If click fails, try to clear and focus
        try:
            element.clear()
            element.send_keys(Keys.CONTROL + "a")  # Select all
            element.send_keys(Keys.DELETE)  # Delete all
        except:
            pass
    
    time.sleep(random.uniform(0.3, 0.8))
    
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.03, 0.08))
    
    time.sleep(random.uniform(0.3, 0.6))

def wait_for_manual_login(driver) -> bool:
    """Wait for user to manually log in"""
    print("\n" + "="*80)
    print("🔐 LOGIN REQUIRED!")
    print("="*80)
    print("📋 Please log in manually in the browser window.")
    print("⏳ The script will wait for you to complete this step.")
    print("✅ When you're logged in and see the chat interface, return here and press Enter.")
    print("="*80)
    
    input("Press Enter when you're logged in and see the chat interface...")
    time.sleep(3)
    print("✅ Login completed! Continuing with scraping...")
    return True

def get_input_element(driver, site_type="perplexity"):
    """Find the input field based on site type"""
    if site_type == "perplexity":
        selectors = [
            "textarea[placeholder*='Ask anything']",
            "textarea[placeholder*='Ask']",
            "textarea[placeholder*='question']",
            "textarea",
            "div[contenteditable='true']",
            "div[role='textbox']",
        ]
    else:  # chatgpt
        selectors = [
            "textarea[placeholder*='Message ChatGPT']",
            "textarea[placeholder*='Send a message']",
            "textarea[placeholder*='Message']",
            "textarea",
            "div[contenteditable='true']",
        ]
    
    print(f"🔍 Looking for input field...")
    
    for i, sel in enumerate(selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, sel)
            print(f"🔍 Selector '{sel}' found {len(elements)} elements")
            
            for j, element in enumerate(elements):
                try:
                    if element.is_displayed():
                        placeholder = element.get_attribute("placeholder") or "no placeholder"
                        print(f"✅ Found input: '{sel}' (placeholder: '{placeholder}') - element {j+1}")
                        return element
                    else:
                        print(f"⚠️  Element '{sel}' {j+1} is not displayed")
                except Exception as e:
                    print(f"⚠️  Error checking element '{sel}' {j+1}: {e}")
                    continue
        except Exception as e:
            print(f"⚠️  Error with selector '{sel}': {e}")
            continue
    
    return None

def wait_for_answer(driver, site_type="perplexity") -> Optional[str]:
    """Wait for answer to appear with optimized detection"""
    if site_type == "perplexity":
        selectors = [
            "[data-testid='answer']",
            "[data-testid='response']",
            ".prose",
            ".markdown",
            ".answer",
            ".response",
            "main",
            "div[role='main']",
        ]
        # Perplexity-specific filters
        navigation_filters = ['Home', 'Discover', 'Spaces']
    else:  # chatgpt
        selectors = [
            "[data-testid='conversation-turn-2']",
            ".markdown",
            "div[data-message-author-role='assistant']",
            "main div:last-child",
            "div[class*='markdown']",
        ]
        # ChatGPT-specific filters
        navigation_filters = ['ChatGPT', 'New chat', 'Clear conversations']
    
    print(f"🔍 Looking for answer...")
    print(f"⏰ Will wait up to {ANSWER_WAIT_SECONDS} seconds...")
    
    start_time = time.time()
    while time.time() - start_time < ANSWER_WAIT_SECONDS:
        for sel in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for elem in elements:
                    try:
                        text = elem.text.strip()
                        # Look for substantial content that's not navigation
                        if (len(text) > 150 and 
                            not any(text.startswith(filter_text) for filter_text in navigation_filters)):
                            print(f"✅ Found answer: {len(text)} chars")
                            
                            # For ChatGPT, try to get the full answer via copy button
                            if site_type == "chatgpt":
                                full_answer = try_get_full_answer_via_copy(driver)
                                if full_answer and len(full_answer) > len(text):
                                    print(f"📋 Got full answer via copy button: {len(full_answer)} chars")
                                    return full_answer
                            
                            return text
                    except:
                        continue
            except:
                continue
        
        # Progress indicator
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0:
            print(f"⏳ Waiting... ({elapsed}s elapsed)")
        
        time.sleep(1)
    
    print("⏰ Timeout waiting for answer")
    return None

def try_get_full_answer_via_copy(driver) -> Optional[str]:
    """Try to get the full answer by clicking the copy button"""
    try:
        # Look for copy button
        copy_selectors = [
            "button[aria-label*='Copy']",
            "button[aria-label*='copy']",
            "button[data-testid*='copy']",
            "button[title*='Copy']",
            "button[title*='copy']",
            "svg[data-icon='copy']",
            "button:has(svg[data-icon='copy'])",
        ]
        
        for sel in copy_selectors:
            try:
                copy_btn = driver.find_element(By.CSS_SELECTOR, sel)
                if copy_btn.is_displayed():
                    print("📋 Found copy button, clicking to get full answer...")
                    copy_btn.click()
                    time.sleep(1)
                    
                    # Try to get text from clipboard (this might not work in headless mode)
                    # For now, just return the current visible text
                    return None
            except:
                continue
        
        return None
    except:
        return None

def extract_citations(driver, site_type="perplexity") -> List[str]:
    """Extract links from the answer"""
    if site_type == "perplexity":
        selectors = [
            "[data-testid='answer'] a[href]",
            ".prose a[href]",
            "main a[href]",
            "div[role='main'] a[href]",
        ]
    else:  # chatgpt
        # ChatGPT rarely has external links, so we'll look for any meaningful links
        selectors = [
            "div[data-message-author-role='assistant'] a[href]",
            ".markdown a[href]",
            "main a[href]",
            "a[href]",
        ]
    
    links = set()
    for sel in selectors:
        try:
            anchors = driver.find_elements(By.CSS_SELECTOR, sel)
            for a in anchors:
                try:
                    href = a.get_attribute("href")
                    if href and href.startswith("http"):
                        # Clean URLs and filter out internal ChatGPT links
                        if "?" in href:
                            href = href.split("?")[0]
                        
                        # Filter out internal ChatGPT URLs
                        if site_type == "chatgpt" and ("chatgpt.com" in href or "openai.com" in href):
                            continue
                        
                        links.add(href)
                except:
                    pass
        except:
            continue
    
    # For ChatGPT, also extract URLs from the answer text itself
    if site_type == "chatgpt":
        print("🔍 Extracting citations from ChatGPT answer text...")
        try:
            # Get the answer text and look for URLs
            answer_text = get_current_answer_text(driver)
            if answer_text:
                import re
                print(f"📝 Processing {len(answer_text)} characters of answer text for citations...")
                
                # Find URLs in text using regex - more comprehensive pattern
                url_pattern = r'https?://[^\s\)]+'
                text_urls = re.findall(url_pattern, answer_text)
                print(f"🔗 Found {len(text_urls)} URLs in text")
                for url in text_urls:
                    # Clean URL
                    if "?" in url:
                        url = url.split("?")[0]
                    if ")" in url:
                        url = url.rstrip(")")
                    if url not in links and not ("chatgpt.com" in url or "openai.com" in url):
                        links.add(url)
                        print(f"✅ Added URL citation: {url}")
                
                # Also look for domain-like patterns that might be citations
                # This captures things like "Business Chief", "AI Magazine", "FNLondon", "goml.io"
                domain_pattern = r'\b[A-Z][a-zA-Z\s&]+(?:\.com|\.io|\.org|\.net|\.co\.uk|\.ai|\.tech)\b'
                domain_matches = re.findall(domain_pattern, answer_text)
                print(f"🌐 Found {len(domain_matches)} domain-like patterns")
                for domain in domain_matches:
                    # Clean up the domain match
                    clean_domain = domain.strip()
                    if clean_domain and len(clean_domain) > 3:
                        # Add as a potential citation source
                        if clean_domain not in links:
                            links.add(f"Potential source: {clean_domain}")
                            print(f"✅ Added domain citation: {clean_domain}")
                
                # Look for company names that might be sources
                company_pattern = r'\b(?:Business Chief|AI Magazine|FNLondon|Business Insider|The Wall Street Journal|Wikipedia|McKinsey|BCG|Deloitte|EY|PwC|Accenture|IBM|Infosys|Capgemini|Cognizant|Financial Times|The Times of India|The Australian|LinkedIn|Superside|Bitcot|Goml|Ailoitte|Xonique|Faculty|Fractal|Algoscale|Quantiphi|Tredence|ZS Associates|Slalom|Booz Allen Hamilton|Unity Advisory|Keystone|Fusion Collective|Slideworks|Monevate|SIB|Perceptis|Xavier AI)\b'
                company_matches = re.findall(company_pattern, answer_text)
                print(f"🏢 Found {len(company_matches)} company name matches")
                for company in company_matches:
                    if company not in links:
                        links.add(f"Source: {company}")
                        print(f"✅ Added company citation: {company}")
                
                # Also look for any capitalized phrases that might be sources (like "Business Chief", "AI Magazine")
                source_pattern = r'\b[A-Z][a-zA-Z\s&]+(?:Magazine|Journal|Times|Insider|Chief|London|Financial|Wall Street|Business|AI|Tech|Consulting|Analytics|Platform|Company|Firm|Group|Advisory|Collective|Works|Advisory)\b'
                source_matches = re.findall(source_pattern, answer_text)
                print(f"📰 Found {len(source_matches)} source pattern matches")
                for source in source_matches:
                    clean_source = source.strip()
                    if clean_source and len(clean_source) > 3 and clean_source not in links:
                        # Check if it's not already captured by company pattern
                        if not any(clean_source in link for link in links):
                            links.add(f"Potential source: {clean_source}")
                            print(f"✅ Added source citation: {clean_source}")
            else:
                print("⚠️  No answer text found for citation extraction")
        except Exception as e:
            print(f"⚠️  Error extracting text citations: {e}")
            pass
    
    result = sorted(set(links))
    if site_type == "chatgpt" and not result:
        result = ["No external citations found (ChatGPT typically doesn't provide external links)"]
    
    print(f"📚 Extracted {len(result)} citations")
    return result

def get_current_answer_text(driver) -> Optional[str]:
    """Get the current answer text from ChatGPT"""
    try:
        # Try multiple strategies to get the answer text
        selectors = [
            "div[data-message-author-role='assistant']",
            ".markdown",
            "main div:last-child",
            "div[class*='markdown']",
            "div[class*='prose']",
            "div[class*='text']",
            "div[class*='content']",
        ]
        
        print("🔍 Searching for answer text using multiple selectors...")
        for i, sel in enumerate(selectors):
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                print(f"🔍 Selector '{sel}' found {len(elements)} elements")
                
                for j, elem in enumerate(elements):
                    try:
                        text = elem.text.strip()
                        if text and len(text) > 100:
                            print(f"📝 Found answer text: {len(text)} chars for citation extraction using '{sel}' element {j+1}")
                            return text
                        elif text:
                            print(f"⚠️  Element '{sel}' {j+1} has text but too short: {len(text)} chars")
                    except Exception as e:
                        print(f"⚠️  Error processing element '{sel}' {j+1}: {e}")
                        continue
            except Exception as e:
                print(f"⚠️  Error with selector '{sel}': {e}")
                continue
        
        # Fallback: try to get text from the main content area
        print("🔄 Trying fallback: main content area...")
        try:
            main_content = driver.find_element(By.CSS_SELECTOR, "main")
            if main_content:
                text = main_content.text.strip()
                if text and len(text) > 100:
                    print(f"📝 Found fallback text: {len(text)} chars for citation extraction")
                    return text
                else:
                    print(f"⚠️  Main content too short: {len(text) if text else 0} chars")
        except Exception as e:
            print(f"⚠️  Error with main content fallback: {e}")
        
        # Last resort: try to get any visible text from the page
        print("🔄 Trying last resort: any visible text...")
        try:
            body_text = driver.find_element(By.CSS_SELECTOR, "body").text.strip()
            if body_text and len(body_text) > 100:
                print(f"📝 Found body text: {len(body_text)} chars for citation extraction")
                return body_text
        except Exception as e:
            print(f"⚠️  Error with body text: {e}")
        
        print("❌ Could not find suitable answer text for citation extraction")
        return None
    except Exception as e:
        print(f"⚠️  Error getting answer text: {e}")
        return None

def handle_blocking_elements(driver):
    """Handle any blocking elements like buttons or overlays"""
    try:
        # Look for common blocking elements
        blocking_selectors = [
            "button.btn-primary",
            "button[class*='btn']",
            "div[class*='overlay']",
            "div[class*='modal']",
            "button[aria-label*='Close']",
            "button[aria-label*='close']",
        ]
        
        for sel in blocking_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for elem in elements:
                    if elem.is_displayed():
                        try:
                            # Try to click to dismiss
                            elem.click()
                            print(f"🔄 Clicked blocking element: {sel}")
                            time.sleep(1)
                        except:
                            pass
            except:
                continue
                
    except Exception as e:
        print(f"⚠️  Could not handle blocking elements: {e}")
        pass

def ask_one(driver, prompt: str, site_type="perplexity") -> Tuple[str, List[str]]:
    """Ask one question and get the answer"""
    print(f"\n🤖 Processing: {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
    
    # Navigate to the selected site
    if site_type == "perplexity":
        url = "https://www.perplexity.ai/"
        print("🌐 Navigating to Perplexity...")
    else:  # chatgpt
        url = "https://chat.openai.com/"
        print("🌐 Navigating to ChatGPT...")
    
    driver.get(url)
    time.sleep(random.uniform(2, 4))
    
    # Wait for page to be ready (not showing "Just a moment..." or similar)
    print("⏳ Waiting for page to fully load...")
    max_wait = 30  # Wait up to 30 seconds for page to load
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if "just a moment" not in driver.title.lower() and "loading" not in driver.title.lower():
            print("✅ Page appears to be loaded")
            break
        time.sleep(1)
        print(f"⏳ Still waiting for page to load... ({int(time.time() - start_time)}s)")
    
    # Check if login needed
    if "login" in driver.title.lower() or "sign in" in driver.title.lower():
        if not wait_for_manual_login(driver):
            raise Exception("Login not completed")
        
        # Add delay after login to appear more human-like
        delay = random.uniform(3.0, 8.0)
        print(f"⏸️  Waiting {delay:.1f}s after login...")
        time.sleep(delay)
    
    # Find input field
    print(f"🔍 Current page: {driver.title} at {driver.current_url}")
    input_el = get_input_element(driver, site_type)
    if not input_el:
        print("🔄 Input not found, refreshing...")
        driver.refresh()
        time.sleep(3)
        print(f"🔍 After refresh - page: {driver.title} at {driver.current_url}")
        input_el = get_input_element(driver, site_type)
        if not input_el:
            print("❌ Input still not found after refresh, trying one more time...")
            time.sleep(5)  # Wait a bit longer
            input_el = get_input_element(driver, site_type)
            if not input_el:
                # Take a screenshot for debugging
                try:
                    screenshot_path = f"debug_input_not_found_{int(time.time())}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"📸 Screenshot saved to {screenshot_path} for debugging")
                except:
                    pass
                raise Exception("Could not find input field even after refresh and retry")
    
    # Skip blocking element handling for now - it was causing input field issues
    # The fake prompts work fine without it
    
    # Type and submit
    print("⌨️  Typing prompt...")
    human_like_typing(driver, input_el, prompt)
    
    # Submit with Enter
    time.sleep(random.uniform(0.3, 0.8))
    input_el.send_keys(Keys.RETURN)
    print("📤 Submitted prompt, waiting for answer...")
    
    # Wait for answer
    answer = wait_for_answer(driver, site_type)
    if not answer:
        print("⏳ Answer not found, trying extra wait...")
        time.sleep(8)
        answer = wait_for_answer(driver, site_type)
    
    if not answer:
        raise Exception("Could not capture answer")
    
    # For ChatGPT, wait for answer to stop growing (indicating completion)
    if site_type == "chatgpt":
        print("⏳ Waiting for ChatGPT to finish typing...")
        answer = wait_for_answer_completion(driver, answer)
    
    # Extract citations
    print("🔍 Extracting citations...")
    citations = extract_citations(driver, site_type)
    
    print(f"✅ Success! Answer: {len(answer)} chars, Citations: {len(citations)}")
    
    # Add delay after getting answer to appear more human-like
    delay = random.uniform(2.0, 5.0)
    print(f"⏸️  Waiting {delay:.1f}s after getting answer...")
    time.sleep(delay)
    
    return answer.strip(), citations

def ask_one_fast(driver, prompt: str, site_type="perplexity") -> Tuple[str, List[str]]:
    """Fast version for first prompt - quick fail to avoid bot detection"""
    print(f"\n🤖 Fast processing: {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
    
    # Navigate to the selected site
    if site_type == "perplexity":
        url = "https://www.perplexity.ai/"
        print("🌐 Navigating to Perplexity...")
    else:  # chatgpt
        url = "https://chat.openai.com/"
        print("🌐 Navigating to ChatGPT...")
    
    driver.get(url)
    time.sleep(2)  # Shorter wait
    
    # Wait for page to be ready (not showing "Just a moment..." or similar)
    print("⏳ Waiting for page to fully load (fast mode)...")
    max_wait = 15  # Wait up to 15 seconds for page to load in fast mode
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if "just a moment" not in driver.title.lower() and "loading" not in driver.title.lower():
            print("✅ Page appears to be loaded")
            break
        time.sleep(1)
        print(f"⏳ Still waiting for page to load... ({int(time.time() - start_time)}s)")
    
    # Check if login needed
    if "login" in driver.title.lower() or "sign in" in driver.title.lower():
        if not wait_for_manual_login(driver):
            raise Exception("Login not completed")
        
        # Add delay after login to appear more human-like
        delay = random.uniform(2.0, 5.0)
        print(f"⏸️  Waiting {delay:.1f}s after login (fast mode)...")
        time.sleep(delay)
    
    # Find input field
    input_el = get_input_element(driver, site_type)
    if not input_el:
        raise Exception("Input field not found")
    
    # Type and submit quickly
    print("⌨️  Typing prompt quickly...")
    human_like_typing(driver, input_el, prompt)
    
    # Submit with Enter
    time.sleep(0.5)
    input_el.send_keys(Keys.RETURN)
    print("📤 Submitted prompt, waiting briefly...")
    
    # Wait for answer with very short timeout
    answer = wait_for_answer_fast(driver, site_type)
    if not answer:
        raise Exception("Answer not found quickly - skipping to avoid bot detection")
    
    # For ChatGPT, wait for answer to stop growing even in fast mode
    if site_type == "chatgpt":
        print("⏳ Waiting for ChatGPT to finish typing (fast mode)...")
        answer = wait_for_answer_completion(driver, answer)
    
    # Extract citations quickly
    print("🔍 Extracting citations...")
    citations = extract_citations(driver, site_type)
    
    print(f"✅ Fast success! Answer: {len(answer)} chars, Citations: {len(citations)}")
    
    # Add delay after getting answer to appear more human-like
    delay = random.uniform(1.0, 3.0)
    print(f"⏸️  Waiting {delay:.1f}s after getting answer (fast mode)...")
    time.sleep(delay)
    
    return answer.strip(), citations

def wait_for_answer_fast(driver, site_type="perplexity") -> Optional[str]:
    """Fast answer detection with short timeout"""
    selectors = [
        "[data-testid='answer']",
        "[data-testid='response']",
        ".prose",
        ".markdown",
        ".answer",
        ".response",
        "main",
        "div[role='main']",
    ]
    
    print(f"🔍 Looking for answer quickly...")
    print(f"⏰ Will wait up to 30 seconds (fast mode)...")
    
    start_time = time.time()
    while time.time() - start_time < 30:  # Increased from 15 to 30 seconds
        for sel in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for elem in elements:
                    try:
                        text = elem.text.strip()
                        # Look for substantial content that's not navigation
                        if (len(text) > 150 and 
                            not text.startswith('Home') and 
                            not text.startswith('Discover') and
                            not text.startswith('Spaces')):
                            print(f"✅ Found answer quickly: {len(text)} chars")
                            return text
                    except:
                        continue
            except:
                continue
        
        time.sleep(1)
    
    print("⏰ Fast timeout - answer not found quickly")
    return None

def ask_one_super_fast(driver, prompt: str, site_type="perplexity") -> Tuple[str, List[str]]:
    """Super fast version for fake prompts - only 10 seconds max"""
    print(f"\n🤖 Super fast processing: {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
    
    # Navigate to the selected site
    if site_type == "perplexity":
        url = "https://www.perplexity.ai/"
        print("🌐 Navigating to Perplexity...")
    else:  # chatgpt
        url = "https://chat.openai.com/"
        print("🌐 Navigating to ChatGPT...")
    
    driver.get(url)
    time.sleep(1)  # Very short wait
    
    # Wait for page to be ready (not showing "Just a moment..." or similar)
    print("⏳ Waiting for page to fully load (super fast mode)...")
    max_wait = 10  # Wait up to 10 seconds for page to load in super fast mode
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if "just a moment" not in driver.title.lower() and "loading" not in driver.title.lower():
            print("✅ Page appears to be loaded")
            break
        time.sleep(1)
        print(f"⏳ Still waiting for page to load... ({int(time.time() - start_time)}s)")
    
    # Check if login needed
    if "login" in driver.title.lower() or "sign in" in driver.title.lower():
        if not wait_for_manual_login(driver):
            raise Exception("Login not completed")
        
        # Add short delay after login to appear more human-like
        delay = random.uniform(1.0, 2.0)
        print(f"⏸️  Waiting {delay:.1f}s after login (super fast mode)...")
        time.sleep(delay)
    
    # Find input field
    input_el = get_input_element(driver, site_type)
    if not input_el:
        raise Exception("Input field not found")
    
    # Type and submit quickly
    print("⌨️  Typing prompt super quickly...")
    human_like_typing(driver, input_el, prompt)
    
    # Submit with Enter
    time.sleep(0.3)
    input_el.send_keys(Keys.RETURN)
    print("📤 Submitted prompt, waiting super briefly...")
    
    # Wait for answer with very short timeout - only 10 seconds
    answer = wait_for_answer_super_fast(driver, site_type)
    if not answer:
        raise Exception("Answer not found in 10 seconds - skipping fake prompt")
    
    # Extract citations quickly
    print("🔍 Extracting citations...")
    citations = extract_citations(driver, site_type)
    
    print(f"✅ Super fast success! Answer: {len(answer)} chars, Citations: {len(citations)}")
    
    # Add short delay after getting answer to appear more human-like
    delay = random.uniform(0.5, 1.5)
    print(f"⏸️  Waiting {delay:.1f}s after getting answer (super fast mode)...")
    time.sleep(delay)
    
    return answer.strip(), citations

def wait_for_answer_super_fast(driver, site_type="perplexity") -> Optional[str]:
    """Super fast answer detection with only 10 second timeout"""
    selectors = [
        "[data-testid='answer']",
        "[data-testid='response']",
        ".prose",
        ".markdown",
        ".answer",
        ".response",
        "main",
        "div[role='main']",
    ]
    
    print(f"🔍 Looking for answer super quickly...")
    print(f"⏰ Will wait up to 10 seconds (super fast mode)...")
    
    start_time = time.time()
    while time.time() - start_time < 10:  # Only 10 seconds max
        for sel in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, sel)
                for elem in elements:
                    try:
                        text = elem.text.strip()
                        # Look for any content, even short
                        if (len(text) > 50 and 
                            not text.startswith('Home') and 
                            not text.startswith('Discover') and
                            not text.startswith('Spaces')):
                            print(f"✅ Found answer super quickly: {len(text)} chars")
                            return text
                    except:
                        continue
            except:
                continue
        
        time.sleep(0.5)  # Check more frequently
    
    print("⏰ Super fast timeout - answer not found in 10 seconds")
    return None

def wait_for_answer_completion(driver, current_answer: str) -> str:
    """Wait for ChatGPT answer to stop growing (indicating completion)"""
    print("🔄 Monitoring answer length for completion...")
    
    last_length = len(current_answer)
    stable_count = 0
    max_stable_time = 10  # Wait 10 seconds of stable length
    
    start_time = time.time()
    while time.time() - start_time < 60:  # Max 60 seconds waiting for completion
        time.sleep(2)
        
        try:
            new_answer = get_current_answer_text(driver)
            if new_answer:
                new_length = len(new_answer)
                print(f"📏 Answer length: {new_length} chars")
                
                if new_length == last_length:
                    stable_count += 2
                    if stable_count >= max_stable_time:
                        print(f"✅ Answer appears complete (stable for {max_stable_time}s)")
                        return new_answer
                else:
                    stable_count = 0
                    last_length = new_length
                    print(f"📈 Answer still growing...")
        except:
            pass
    
    print("⏰ Timeout waiting for completion, using current answer")
    return current_answer

def main():
    parser = argparse.ArgumentParser(description="AI Site Scraper (Perplexity & ChatGPT)")
    parser.add_argument("--site", choices=["perplexity", "chatgpt"], default="perplexity", 
                       help="Which site to scrape (default: perplexity)")
    parser.add_argument("--prompts-csv", help="CSV with one prompt per row")
    parser.add_argument("--limit", type=int, help="Limit number of prompts to process (for testing)")
    parser.add_argument("--out-csv", default="results.csv", help="Output CSV path")
    parser.add_argument("--out-jsonl", help="Optional JSONL output path")
    args = parser.parse_args()
    
    prompts = read_prompts(args.prompts_csv)
    if not prompts:
        print("No prompts found!")
        return
    
    # Apply limit if specified
    if args.limit and args.limit > 0:
        prompts = prompts[:args.limit]
        print(f"📊 Limited to first {len(prompts)} prompts for testing")
    
    print(f"🚀 Starting {args.site.title()} scraper with {len(prompts)} prompts")
    print(f"📁 Output: {args.out_csv}")
    print(f"⚡ Using optimized timing ({ANSWER_WAIT_SECONDS}s max wait per answer)")
    
    # Setup Chrome
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        rows = []
        for i, prompt in enumerate(prompts, 1):
            print(f"\n{'='*60}")
            print(f"📝 Processing prompt {i}/{len(prompts)}")
            print(f"{'='*60}")
            
            # Add fake first prompt for ChatGPT to warm up
            if i == 1 and args.site == "chatgpt":
                print("🚀 First prompt - sending fake 'Hello' to warm up ChatGPT (10s max)")
                try:
                    # Send a simple "Hello" first - super fast
                    fake_answer, fake_citations = ask_one_super_fast(driver, "Hello", args.site)
                    print("✅ Fake prompt sent successfully, now processing real prompt...")
                    
                    # Add delay between fake and real prompt
                    delay = random.uniform(3.0, 8.0)
                    print(f"⏸️  Waiting {delay:.1f}s between fake and real prompt...")
                    time.sleep(delay)
                    
                    # Now process the real first prompt
                    answer, citations = ask_one(driver, prompt, args.site)
                    rows.append({
                        "idx": i,
                        "prompt": prompt,
                        "answer": answer,
                        "citations": "; ".join(citations),
                    })
                    print("✅ First real prompt succeeded!")
                except Exception as e:
                    print(f"❌ Error processing first prompt: {e}")
                    rows.append({
                        "idx": i,
                        "prompt": prompt,
                        "answer": f"Error: {e}",
                        "citations": "",
                    })
            elif i == 2 and args.site == "chatgpt":
                print("🚀 Second prompt - sending fake 'Are you there?' to continue warming up (10s max)")
                try:
                    # Send "Are you there?" second - super fast
                    fake_answer, fake_citations = ask_one_super_fast(driver, "Are you there?", args.site)
                    print("✅ Second fake prompt sent successfully, now processing real prompt...")
                    
                    # Add delay between fake and real prompt
                    delay = random.uniform(3.0, 8.0)
                    print(f"⏸️  Waiting {delay:.1f}s between fake and real prompt...")
                    time.sleep(delay)
                    
                    # Now process the real second prompt
                    answer, citations = ask_one(driver, prompt, args.site)
                    rows.append({
                        "idx": i,
                        "prompt": prompt,
                        "answer": answer,
                        "citations": "; ".join(citations),
                    })
                    print("✅ Second real prompt succeeded!")
                except Exception as e:
                    print(f"❌ Error processing second prompt: {e}")
                    rows.append({
                        "idx": i,
                        "prompt": prompt,
                        "answer": f"Error: {e}",
                        "citations": "",
                    })
            elif i == 1 and args.site == "perplexity":
                print("🚀 First prompt - using fast-fail mode to avoid bot detection (Perplexity)")
                try:
                    # Quick attempt for first prompt
                    answer, citations = ask_one_fast(driver, prompt, args.site)
                    rows.append({
                        "idx": i,
                        "prompt": prompt,
                        "answer": answer,
                        "citations": "; ".join(citations),
                    })
                    print("✅ First prompt succeeded!")
                except Exception as e:
                    print(f"❌ First prompt failed (expected): {e}")
                    print("⏭️  Skipping to next prompt...")
                    rows.append({
                        "idx": i,
                        "prompt": prompt,
                        "answer": f"Skipped (bot detection): {e}",
                        "citations": "",
                    })
                    continue
            else:
                # Normal processing for subsequent prompts
                try:
                    answer, citations = ask_one(driver, prompt, args.site)
                    rows.append({
                        "idx": i,
                        "prompt": prompt,
                        "answer": answer,
                        "citations": "; ".join(citations),
                    })
                except Exception as e:
                    print(f"❌ Error processing prompt {i}: {e}")
                    rows.append({
                        "idx": i,
                        "prompt": prompt,
                        "answer": f"Error: {e}",
                        "citations": "",
                    })
            
            # Wait between prompts
            if i < len(prompts):
                delay = random.uniform(*PER_PROMPT_DELAY)
                print(f"⏸️  Waiting {delay:.1f}s before next prompt...")
                time.sleep(delay)
        
        # Save results
        df = pd.DataFrame(rows)
        df.to_csv(args.out_csv, index=False, encoding="utf-8")
        print(f"\n💾 Saved {len(rows)} rows to {args.out_csv}")
        
        if args.out_jsonl:
            with open(args.out_jsonl, "w", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"💾 Also wrote JSONL to {args.out_jsonl}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
