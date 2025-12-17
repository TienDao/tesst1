#!/usr/bin/env python3
"""
Script to crawl businesses from Klaviyo Connect directory
"""

import json
import time
import re
import requests
from bs4 import BeautifulSoup

def crawl_with_playwright(url):
    """Crawl businesses using Playwright"""
    businesses = []

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"Loading page: {url}")
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Wait a bit for dynamic content
        time.sleep(3)

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
                print(f"Found {len(elements)} elements with selector: {selector}")

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
    print("Using requests + BeautifulSoup for crawling...")
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
