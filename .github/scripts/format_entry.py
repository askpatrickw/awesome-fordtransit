#!/usr/bin/env python3
"""
Format a resource entry for the Awesome Ford Transit list.
"""

import sys
import argparse
import re
from urllib.parse import urlparse

def extract_site_name(url):
    """
    Extract a clean site name from a URL.
    """
    parsed = urlparse(url)
    domain = parsed.netloc

    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]

    # Remove common TLDs to get site name
    site_name = domain.split('.')[0]

    # Capitalize words and handle special cases
    site_name = site_name.replace('-', ' ').replace('_', ' ')
    site_name = ' '.join(word.capitalize() for word in site_name.split())

    return site_name

def format_entry(url, description, category=None):
    """
    Format an entry for the README.

    Returns:
        str: Formatted markdown entry
    """
    # Extract site name if not in description
    site_name = extract_site_name(url)

    # Clean up description
    description = description.strip()
    if not description:
        description = f"{site_name} products and services"

    # Remove trailing period if present (we'll add it)
    description = description.rstrip('.')

    # Format the entry
    # Check if the description already contains the site name
    if site_name.lower() not in description.lower():
        # Standard format: [Site Name](url) Description
        entry = f"- [{site_name}]({url}) {description}"
    else:
        # If site name is in description, try to extract it
        # Look for patterns like "Site Name offers..." or "Site Name -..."
        if description.lower().startswith(site_name.lower()):
            # Remove site name from beginning
            desc_without_name = description[len(site_name):].strip()
            if desc_without_name.startswith('-') or desc_without_name.startswith(':'):
                desc_without_name = desc_without_name[1:].strip()
            entry = f"- [{site_name}]({url}) {desc_without_name}"
        else:
            # Site name is somewhere in the description, use as-is
            entry = f"- [{site_name}]({url}) {description}"

    return entry

def get_category_section(category):
    """
    Map category names to their section headers in the README.
    """
    category_map = {
        'Community': '## Community',
        'Dealers': '## Dealers',
        'Engine Mods': '## Engine Mods',
        'Exterior': '## Exterior Components',
        'Exterior - Bumpers': '### Bumpers',
        'Exterior - Front Hooks': '### Front Hooks',
        'Exterior - Rear Shock Relocation': '### Rear Shock Relocation',
        'Exterior - Skid Plates': '### Skid Plates',
        'Exterior - Ski Boxes': '### Ski Boxes',
        'Heating and AC': '## Heating and Air Conditioning',
        'Interior': '## Interior Components',
        'Maintenance': '## Maintenance',
        'Plumbing': '## Plumbing',
        'Suppliers': '## Suppliers to DIY Builders',
        'Suspension and Lifts': '## Suspension and Lifts',
        'Seat Swivels': '## Seat Swivels',
        'Van Automation': '## Van Automation',
        'Van Builds': '## Van Builds',
        'Van Builders': '## Van Builders',
        'Wheels and Tires': '## Wheels and Tires'
    }

    return category_map.get(category, '## ' + category)

def main():
    parser = argparse.ArgumentParser(description='Format a resource entry')
    parser.add_argument('--url', required=True, help='Resource URL')
    parser.add_argument('--description', required=True, help='Resource description')
    parser.add_argument('--category', help='Resource category')
    parser.add_argument('--output', help='Output file (default: stdout)')

    args = parser.parse_args()

    # Format the entry
    entry = format_entry(args.url, args.description, args.category)

    # Add category information if provided
    if args.category:
        section = get_category_section(args.category)
        full_output = f"Category: {args.category}\nSection: {section}\n\nFormatted entry:\n{entry}"
    else:
        full_output = entry

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(full_output)
        print(f"✅ Formatted entry written to {args.output}")
    else:
        print(full_output)

if __name__ == "__main__":
    main()