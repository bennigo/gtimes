#!/usr/bin/env python3
"""
Documentation link checker for GTimes documentation.

This script validates all links in the generated documentation to ensure
they are accessible and working correctly.
"""

import os
import re
import sys
import time
from pathlib import Path
from typing import List, Set, Tuple
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Missing required packages. Install with: pip install requests beautifulsoup4")
    sys.exit(1)


class DocumentationLinkChecker:
    """Check all links in MkDocs generated documentation."""
    
    def __init__(self, site_dir: str = "site"):
        self.site_dir = Path(site_dir)
        self.base_url = "file://" + str(self.site_dir.absolute())
        self.checked_urls = set()
        self.broken_links = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GTimes-Documentation-Checker/1.0'
        })
    
    def find_html_files(self) -> List[Path]:
        """Find all HTML files in the site directory."""
        html_files = []
        for html_file in self.site_dir.rglob("*.html"):
            html_files.append(html_file)
        return sorted(html_files)
    
    def extract_links_from_file(self, html_file: Path) -> List[Tuple[str, str]]:
        """
        Extract all links from an HTML file.
        
        Returns:
            List of (link_url, link_text) tuples
        """
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            links = []
            
            # Find all anchor tags with href
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                links.append((href, text))
            
            # Find all image sources
            for img in soup.find_all('img', src=True):
                src = img['src']
                alt = img.get('alt', 'Image')
                links.append((src, f"Image: {alt}"))
            
            return links
            
        except Exception as e:
            print(f"    ❌ Error reading {html_file}: {e}")
            return []
    
    def resolve_relative_url(self, url: str, base_file: Path) -> str:
        """Resolve relative URLs to absolute file paths or URLs."""
        if url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
            return url
        
        if url.startswith('#'):
            # Fragment link within same page
            return str(base_file) + url
        
        # Relative URL - resolve relative to base file
        base_dir = base_file.parent
        if url.startswith('/'):
            # Root-relative URL
            resolved_path = self.site_dir / url.lstrip('/')
        else:
            # Relative URL
            resolved_path = (base_dir / url).resolve()
        
        return str(resolved_path)
    
    def check_local_file(self, file_path: str) -> bool:
        """Check if a local file exists."""
        # Remove fragment identifier
        clean_path = file_path.split('#')[0]
        return Path(clean_path).exists()
    
    def check_external_url(self, url: str) -> bool:
        """Check if an external URL is accessible."""
        if url in self.checked_urls:
            return True  # Already checked
        
        try:
            # Add delay to be respectful to external servers
            time.sleep(0.1)
            
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            # Some servers don't support HEAD, try GET
            if response.status_code == 405:
                response = self.session.get(url, timeout=10, allow_redirects=True)
            
            self.checked_urls.add(url)
            return response.status_code < 400
            
        except Exception as e:
            print(f"    ⚠️  Error checking {url}: {e}")
            return False
    
    def check_fragment_link(self, file_path: str, fragment: str) -> bool:
        """Check if a fragment (anchor) exists in an HTML file."""
        if not fragment:
            return True
        
        clean_path = file_path.split('#')[0]
        if not Path(clean_path).exists():
            return False
        
        try:
            with open(clean_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for elements with matching id
            if soup.find(id=fragment):
                return True
            
            # Check for elements with matching name
            if soup.find(attrs={'name': fragment}):
                return True
            
            # Check for heading anchors (common in documentation)
            if soup.find('a', attrs={'class': 'headerlink', 'href': f'#{fragment}'}):
                return True
            
            return False
            
        except Exception as e:
            print(f"    ❌ Error checking fragment in {clean_path}: {e}")
            return False
    
    def check_links_in_file(self, html_file: Path) -> List[dict]:
        """Check all links in a single HTML file."""
        print(f"  📄 Checking {html_file.relative_to(self.site_dir)}")
        
        links = self.extract_links_from_file(html_file)
        broken_links = []
        
        for link_url, link_text in links:
            # Skip empty or placeholder links
            if not link_url or link_url in ['#', 'javascript:void(0)']:
                continue
            
            # Resolve relative URLs
            if not link_url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                resolved_url = self.resolve_relative_url(link_url, html_file)
            else:
                resolved_url = link_url
            
            # Check link
            is_valid = True
            error_msg = ""
            
            if resolved_url.startswith(('http://', 'https://')):
                # External URL
                if not self.check_external_url(resolved_url):
                    is_valid = False
                    error_msg = "External URL not accessible"
            elif resolved_url.startswith('mailto:'):
                # Email link - basic format validation
                email_match = re.match(r'^mailto:([^@]+@[^@]+\.[^@]+)', resolved_url)
                if not email_match:
                    is_valid = False
                    error_msg = "Invalid email format"
            else:
                # Local file
                if '#' in resolved_url:
                    file_path, fragment = resolved_url.split('#', 1)
                    if not self.check_local_file(file_path):
                        is_valid = False
                        error_msg = "Local file not found"
                    elif not self.check_fragment_link(resolved_url, fragment):
                        is_valid = False
                        error_msg = f"Fragment '#{fragment}' not found"
                else:
                    if not self.check_local_file(resolved_url):
                        is_valid = False
                        error_msg = "Local file not found"
            
            if not is_valid:
                broken_link = {
                    'file': str(html_file.relative_to(self.site_dir)),
                    'url': link_url,
                    'resolved_url': resolved_url,
                    'text': link_text,
                    'error': error_msg
                }
                broken_links.append(broken_link)
                print(f"    ❌ {link_url} -> {error_msg}")
        
        return broken_links
    
    def check_all_links(self) -> bool:
        """Check all links in the documentation."""
        print("🔗 Checking documentation links...")
        
        if not self.site_dir.exists():
            print(f"❌ Documentation site directory not found: {self.site_dir}")
            return False
        
        html_files = self.find_html_files()
        if not html_files:
            print(f"❌ No HTML files found in {self.site_dir}")
            return False
        
        print(f"  Found {len(html_files)} HTML files to check")
        
        all_broken_links = []
        for html_file in html_files:
            file_broken_links = self.check_links_in_file(html_file)
            all_broken_links.extend(file_broken_links)
        
        # Summary
        if all_broken_links:
            print(f"\n❌ Found {len(all_broken_links)} broken links:")
            for broken_link in all_broken_links:
                print(f"  📄 {broken_link['file']}")
                print(f"     🔗 {broken_link['url']} -> {broken_link['error']}")
                print(f"     📝 \"{broken_link['text']}\"")
                print()
            return False
        else:
            print(f"\n✅ All links are working! Checked {len(self.checked_urls)} unique URLs.")
            return True
    
    def validate_internal_structure(self) -> bool:
        """Validate internal documentation structure."""
        print("\n📋 Validating documentation structure...")
        
        required_files = [
            "index.html",
            "guides/installation/index.html",
            "guides/quickstart/index.html",
            "api/gpstime/index.html",
            "api/timefunc/index.html",
            "api/timecalc/index.html",
            "api/exceptions/index.html",
            "examples/basic-usage/index.html",
            "development/contributing/index.html",
        ]
        
        missing_files = []
        for required_file in required_files:
            file_path = self.site_dir / required_file
            if not file_path.exists():
                missing_files.append(required_file)
        
        if missing_files:
            print(f"❌ Missing required documentation files:")
            for missing_file in missing_files:
                print(f"  📄 {missing_file}")
            return False
        else:
            print(f"✅ All required documentation files present")
            return True


def main() -> int:
    """Main function."""
    print("🧪 GTimes Documentation Link Checker")
    print("=" * 50)
    
    checker = DocumentationLinkChecker()
    
    # Check documentation structure
    structure_valid = checker.validate_internal_structure()
    
    # Check all links
    links_valid = checker.check_all_links()
    
    print("\n" + "=" * 50)
    if structure_valid and links_valid:
        print("🎉 All documentation checks PASSED!")
        return 0
    else:
        print("💥 Some documentation checks FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())