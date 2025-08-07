#!/usr/bin/env python3
"""
Validate that a URL is accessible and returns a valid response.
"""

import sys
import requests
from urllib.parse import urlparse

def validate_url(url):
    """
    Validate that a URL is accessible and valid.

    Returns:
        True if valid, False otherwise
    """
    # Check URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            print(f"❌ Invalid URL format: {url}")
            return False
    except Exception as e:
        print(f"❌ Error parsing URL: {e}")
        return False

    # Check if URL is accessible
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; AwesomeFordTransit/1.0; +https://github.com/askpatrickw/awesome-fordtransit)'
        }
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

        if response.status_code == 200:
            print(f"✅ URL is valid and accessible: {url}")

            # Check if it appears to be Transit-related
            content_lower = response.text.lower()[:10000]  # Check first 10KB
            transit_keywords = ['transit', 'ford', 'van', 'sprinter', 'camper', 'rv']

            if any(keyword in content_lower for keyword in transit_keywords):
                print("✅ Content appears to be Transit/Van related")
            else:
                print("⚠️ Warning: Content may not be Transit-specific")

            return True
        else:
            print(f"❌ URL returned status code {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ URL request timed out after 10 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to URL")
        return False
    except Exception as e:
        print(f"❌ Error accessing URL: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_url.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    if not url:
        print("❌ No URL provided")
        sys.exit(1)

    if validate_url(url):
        sys.exit(0)
    else:
        sys.exit(1)