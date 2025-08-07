#!/usr/bin/env python3
"""
Check if a URL already exists in the README.md file.
"""

import sys
import re
from urllib.parse import urlparse, urlunparse

def normalize_url(url):
    """
    Normalize a URL for comparison.
    - Remove trailing slashes
    - Remove www. prefix
    - Convert to lowercase
    - Remove query parameters and fragments for base comparison
    """
    parsed = urlparse(url.lower())

    # Remove www. from netloc
    netloc = parsed.netloc
    if netloc.startswith('www.'):
        netloc = netloc[4:]

    # Remove trailing slash from path
    path = parsed.path.rstrip('/')

    # Reconstruct URL without query and fragment for base comparison
    normalized = urlunparse((
        parsed.scheme,
        netloc,
        path,
        '',  # params
        '',  # query
        ''   # fragment
    ))

    return normalized

def extract_urls_from_markdown(content):
    """
    Extract all URLs from markdown content.
    Handles both [text](url) and plain URL formats.
    """
    urls = []

    # Match markdown links [text](url)
    markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(markdown_pattern, content):
        urls.append(match.group(2))

    # Match plain URLs
    url_pattern = r'https?://[^\s\)>\]]+(?:[^\s\)>\].,;!?]|[.,;!?](?=\s|$))'
    for match in re.finditer(url_pattern, content):
        url = match.group(0)
        # Clean up common trailing punctuation that might be caught
        url = re.sub(r'[.,;!?]+$', '', url)
        urls.append(url)

    return urls

def check_duplicate(url, readme_path='README.md'):
    """
    Check if a URL already exists in the README.

    Returns:
        tuple: (is_duplicate, similar_urls)
    """
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ README.md not found at {readme_path}")
        sys.exit(1)

    # Normalize the input URL
    normalized_input = normalize_url(url)
    input_domain = urlparse(url.lower()).netloc.replace('www.', '')

    # Extract all URLs from README
    existing_urls = extract_urls_from_markdown(content)

    exact_matches = []
    domain_matches = []

    for existing_url in existing_urls:
        normalized_existing = normalize_url(existing_url)
        existing_domain = urlparse(existing_url.lower()).netloc.replace('www.', '')

        # Check for exact match (normalized)
        if normalized_input == normalized_existing:
            exact_matches.append(existing_url)
        # Check for same domain
        elif input_domain == existing_domain:
            domain_matches.append(existing_url)

    # Report findings
    if exact_matches:
        print(f"❌ Duplicate found! This URL already exists in the README:")
        for match in exact_matches:
            print(f"   - {match}")
        return True, exact_matches

    if domain_matches:
        print(f"⚠️ Similar URLs from the same domain found:")
        for match in domain_matches:
            print(f"   - {match}")
        print("✅ Not an exact duplicate, but please verify this is a different resource")
        return False, domain_matches

    print(f"✅ No duplicates found for {url}")
    return False, []

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_duplicates.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    if not url:
        print("❌ No URL provided")
        sys.exit(1)

    is_duplicate, similar = check_duplicate(url)

    if is_duplicate:
        sys.exit(1)  # Exit with error if duplicate
    else:
        sys.exit(0)  # Exit successfully if not duplicate