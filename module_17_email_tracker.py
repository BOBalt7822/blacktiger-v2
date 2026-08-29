#!/usr/bin/env python3
import sys
import os
import subprocess
import importlib
import time

def install_package(pkg):
    try:
        importlib.import_module(pkg)
        return True
    except ImportError:
        pass
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"], capture_output=True, check=True)
        return True
    except:
        pass
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", pkg, "--quiet"], capture_output=True, check=True)
        return True
    except:
        pass
    
    return False

def ensure_dependencies():
    packages = [
        ("aiohttp", "aiohttp"),
        ("holehe", "holehe")
    ]
    
    for mod_name, pkg_name in packages:
        try:
            importlib.import_module(mod_name)
        except ImportError:
            print(f"[*] Installing {pkg_name}...")
            if not install_package(pkg_name):
                print(f"[!] Failed to install {pkg_name}")
                print(f"[*] Please run: pip install {pkg_name}")
                input("Press Enter after installing...")

ensure_dependencies()

import asyncio
import re
import json
import aiohttp
from typing import Dict, List, Tuple, Optional
import holehe

TARGET_MODULES = [
    'facebook', 'tiktok', 'discord', 'spotify', 'snapchat',
    'github', 'instagram', 'twitter', 'reddit', 'pinterest',
    'tumblr', 'twitch', 'paypal', 'adobe', 'wordpress',
    'protonmail', 'mailru', 'yahoo', 'microsoft', 'linkedin'
]

class EmailTracker:
    def __init__(self, email: str):
        self.email = email
        self.results = {}
        self.found_accounts = []
        self.country_info = self._get_country(email)
    
    def _get_country(self, email: str) -> Dict:
        domain = email.split('@')[-1].lower()
        
        country_map = {
            '.uk': {'country': 'United Kingdom', 'code': 'GB'},
            '.fr': {'country': 'France', 'code': 'FR'},
            '.de': {'country': 'Germany', 'code': 'DE'},
            '.it': {'country': 'Italy', 'code': 'IT'},
            '.es': {'country': 'Spain', 'code': 'ES'},
            '.pt': {'country': 'Portugal', 'code': 'PT'},
            '.nl': {'country': 'Netherlands', 'code': 'NL'},
            '.be': {'country': 'Belgium', 'code': 'BE'},
            '.ch': {'country': 'Switzerland', 'code': 'CH'},
            '.at': {'country': 'Austria', 'code': 'AT'},
            '.se': {'country': 'Sweden', 'code': 'SE'},
            '.no': {'country': 'Norway', 'code': 'NO'},
            '.dk': {'country': 'Denmark', 'code': 'DK'},
            '.fi': {'country': 'Finland', 'code': 'FI'},
            '.pl': {'country': 'Poland', 'code': 'PL'},
            '.cz': {'country': 'Czech Republic', 'code': 'CZ'},
            '.ru': {'country': 'Russia', 'code': 'RU'},
            '.ua': {'country': 'Ukraine', 'code': 'UA'},
            '.ca': {'country': 'Canada', 'code': 'CA'},
            '.mx': {'country': 'Mexico', 'code': 'MX'},
            '.br': {'country': 'Brazil', 'code': 'BR'},
            '.ar': {'country': 'Argentina', 'code': 'AR'},
            '.cl': {'country': 'Chile', 'code': 'CL'},
            '.jp': {'country': 'Japan', 'code': 'JP'},
            '.cn': {'country': 'China', 'code': 'CN'},
            '.in': {'country': 'India', 'code': 'IN'},
            '.kr': {'country': 'South Korea', 'code': 'KR'},
            '.sg': {'country': 'Singapore', 'code': 'SG'},
            '.au': {'country': 'Australia', 'code': 'AU'},
            '.nz': {'country': 'New Zealand', 'code': 'NZ'},
            '.za': {'country': 'South Africa', 'code': 'ZA'}
        }
        
        for tld, info in country_map.items():
            if domain.endswith(tld):
                return info
        
        specific = {
            'gmail.com': {'country': 'United States', 'code': 'US'},
            'yahoo.com': {'country': 'United States', 'code': 'US'},
            'hotmail.com': {'country': 'United States', 'code': 'US'},
            'outlook.com': {'country': 'United States', 'code': 'US'},
            'protonmail.com': {'country': 'Switzerland', 'code': 'CH'},
            'mail.ru': {'country': 'Russia', 'code': 'RU'},
            'yandex.ru': {'country': 'Russia', 'code': 'RU'},
            'icloud.com': {'country': 'United States', 'code': 'US'},
        }
        
        if domain in specific:
            return specific[domain]
        
        return {'country': 'Unknown', 'code': 'XX'}
    
    async def check_module(self, module_name: str) -> Tuple[str, bool]:
        try:
            module = getattr(holehe.modules, module_name)
            result = await module(self.email)
            
            exists = False
            if isinstance(result, dict):
                exists = result.get('rateLimit', False) or result.get('exists', False) or result.get('found', False)
                if result.get('email', '').lower() == self.email.lower():
                    exists = True
            
            return (module_name, exists)
        except:
            return (module_name, False)
    
    async def scan_all(self) -> Dict:
        print(f"\n[*] Scanning: {self.email}")
        print(f"[*] Country: {self.country_info['country']}")
        print(f"[*] Checking {len(TARGET_MODULES)} platforms...\n")
        
        tasks = [self.check_module(m) for m in TARGET_MODULES]
        results = await asyncio.gather(*tasks)
        
        for module_name, exists in results:
            if exists:
                self.found_accounts.append(module_name)
            self.results[module_name] = exists
        
        return self.results
    
    def print_results(self):
        print("\n" + "="*60)
        print(f"EMAIL: {self.email}")
        print("="*60)
        print(f"Country: {self.country_info['country']} ({self.country_info['code']})")
        print(f"Accounts found: {len(self.found_accounts)}")
        
        if self.found_accounts:
            print("\n[+] SOCIAL MEDIA ACCOUNTS:")
            for module in sorted(self.found_accounts):
                print(f"    - {module.capitalize()}")
        else:
            print("\n[-] No accounts found.")
        
        print("="*60 + "\n")

async def main_async():
    print("\n" + "="*60)
    print("EMAIL TRACKER - Social Media Lookup")
    print("="*60)
    print("Checks: Facebook, TikTok, Discord, Spotify, Snapchat,")
    print("GitHub, Instagram, Twitter, Reddit, Pinterest, Tumblr,")
    print("Twitch, PayPal, Adobe, Wordpress, Protonmail, Mailru,")
    print("Yahoo, Microsoft, LinkedIn\n")
    
    while True:
        email = input("Enter email (or 'exit'): ").strip().lower()
        
        if email in ['exit', 'quit', '']:
            print("Exiting...")
            break
        
        if '@' not in email or '.' not in email:
            print("Invalid email.\n")
            continue
        
        start = time.time()
        tracker = EmailTracker(email)
        await tracker.scan_all()
        elapsed = time.time() - start
        
        tracker.print_results()
        print(f"Completed in {elapsed:.2f} seconds.\n")

def run():
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
    except Exception as e:
        print(f"\n[!] Error: {e}")
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    run()
