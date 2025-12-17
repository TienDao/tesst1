#!/usr/bin/env python3
"""
Script to crawl businesses from Klaviyo Connect directory
"""

import json
import time
import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def crawl_with_playwright(url, max_clicks=100):
    """Crawl businesses using Playwright with load-more functionality"""
    businesses = []

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"Loading page: {url}")
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Wait a bit for dynamic content
        time.sleep(3)

        # Try to find and click "Load More" button repeatedly
        load_more_selectors = [
            "button:has-text('Load more')",
            "button:has-text('Load More')",
            "button:has-text('Show more')",
            "button:has-text('See more')",
            "button[class*='load']",
            "button[class*='more']",
            "a:has-text('Load more')",
            "a:has-text('Load More')",
        ]

        click_count = 0
        previous_count = 0

        print("\nAttempting to load all results...")
        while click_count < max_clicks:
            # Try to find load more button
            load_more_button = None
            for selector in load_more_selectors:
                try:
                    load_more_button = page.query_selector(selector)
                    if load_more_button and load_more_button.is_visible():
                        break
                except:
                    continue

            if not load_more_button:
                print("No more 'Load More' button found.")
                break

            try:
                # Check if button is enabled
                is_disabled = load_more_button.is_disabled()
                if is_disabled:
                    print("'Load More' button is disabled.")
                    break

                # Click the button
                click_count += 1
                print(f"Click #{click_count}: Loading more results...")
                load_more_button.click()

                # Wait for content to load
                time.sleep(2)
                page.wait_for_load_state("networkidle", timeout=10000)

                # Check if new content was loaded
                current_selectors = [
                    "div.partner-card",
                    "div[class*='PartnerCard']",
                    "div[class*='partner']",
                    "article",
                ]

                current_count = 0
                for selector in current_selectors:
                    elements = page.query_selector_all(selector)
                    if elements and len(elements) > current_count:
                        current_count = len(elements)

                print(f"  Total elements found: {current_count}")

                # If count hasn't increased, we might be done
                if current_count == previous_count:
                    print("No new content loaded. Stopping.")
                    break

                previous_count = current_count

            except Exception as e:
                print(f"Error clicking load more button: {e}")
                break

        print(f"\nFinished loading. Total clicks: {click_count}")

        # Save page content for debugging
        content = page.content()
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Page source saved to page_source.html")

        # Try different selectors to find business cards/listings
        possible_selectors = [
            "div.partner-card",
            "div[class*='PartnerCard']",
            "div[class*='partner']",
            "div[class*='card']",
            "article",
            "div[data-testid*='partner']",
            "a[href*='/partners/']",
        ]

        for selector in possible_selectors:
            elements = page.query_selector_all(selector)
            if elements and len(elements) > 3:
                print(f"\nExtracting businesses from {len(elements)} elements using selector: {selector}")

                for element in elements:
                    try:
                        # Try to get text content
                        text = element.inner_text()

                        # Try to find business name - usually the first line or in a heading
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        if lines:
                            name = lines[0]
                            if name and len(name) > 2 and len(name) < 100 and name not in businesses:
                                businesses.append(name)
                                print(f"Found: {name}")
                    except Exception as e:
                        continue

                if businesses:
                    break

        # Alternative: try to find all h2, h3 tags which often contain business names
        if not businesses:
            print("Trying to find headings...")
            for tag in ['h2', 'h3', 'h4']:
                headings = page.query_selector_all(tag)
                for heading in headings:
                    try:
                        text = heading.inner_text().strip()
                        if text and len(text) > 2 and len(text) < 100 and text not in businesses:
                            # Filter out common non-business text
                            skip_words = ['filter', 'sort', 'search', 'results', 'showing', 'found']
                            if not any(word in text.lower() for word in skip_words):
                                businesses.append(text)
                                print(f"Found: {text}")
                    except:
                        continue

                if businesses and len(businesses) > 5:
                    break

        browser.close()

    return businesses

def crawl_with_requests(url):
    """Crawl businesses using requests and BeautifulSoup"""
    businesses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        print(f"Fetching page: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Save page source
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Page source saved to page_source.html")

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find business cards/listings with various selectors
        possible_selectors = [
            {'class': re.compile(r'partner', re.I)},
            {'class': re.compile(r'card', re.I)},
            {'class': re.compile(r'business', re.I)},
            {'class': re.compile(r'company', re.I)},
        ]

        business_elements = []
        for selector in possible_selectors:
            elements = soup.find_all('div', selector)
            if elements and len(elements) > 3:
                print(f"Found {len(elements)} elements with selector: {selector}")
                business_elements = elements
                break

        # Extract business names
        for element in business_elements:
            # Try to find business name in headings
            name = None
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
                heading = element.find(tag)
                if heading:
                    name = heading.get_text(strip=True)
                    break

            # Try to find in links
            if not name:
                link = element.find('a')
                if link:
                    name = link.get_text(strip=True)

            if name and len(name) > 2 and len(name) < 100 and name not in businesses:
                businesses.append(name)
                print(f"Found: {name}")

        # If still no businesses found, try all headings
        if not businesses:
            print("Trying to find all headings...")
            for tag in ['h2', 'h3', 'h4']:
                headings = soup.find_all(tag)
                for heading in headings:
                    text = heading.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 100:
                        skip_words = ['filter', 'sort', 'search', 'results', 'showing', 'found', 'partner', 'directory']
                        if not any(word in text.lower() for word in skip_words):
                            if text not in businesses:
                                businesses.append(text)
                                print(f"Found: {text}")

                if businesses and len(businesses) > 5:
                    break

    except requests.RequestException as e:
        print(f"Error fetching page: {e}")

    return businesses

def crawl_businesses(url):
    """Crawl businesses from Klaviyo Connect"""
    try:
        print("Using Playwright for crawling with load-more functionality...")
        return crawl_with_playwright(url)
    except Exception as e:
        print(f"\nPlaywright failed: {e}")
        print("\nNote: To use load-more functionality, you need to install Playwright browsers:")
        print("  Run: playwright install")
        print("\nFalling back to requests method (will only get first page)...")
        return crawl_with_requests(url)

def main():
    url = "https://connect.klaviyo.com/?country=US&f_monthly-budget=2500-or-unsure"

    print("Starting Klaviyo business crawl...")
    businesses = crawl_businesses(url)

    print(f"\n{'='*50}")
    print(f"Total businesses found: {len(businesses)}")
    print(f"{'='*50}\n")

    if businesses:
        print("Business List:")
        for i, business in enumerate(businesses, 1):
            print(f"{i}. {business}")

        # Save to JSON file
        output = {
            "total": len(businesses),
            "businesses": businesses,
            "source_url": url
        }

        with open('klaviyo_businesses.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to klaviyo_businesses.json")
    else:
        print("No businesses found. Check page_source.html to debug the page structure.")

if __name__ == "__main__":
    main()
