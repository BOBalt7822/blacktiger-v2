#!/usr/bin/env python3
import sys
import os
import subprocess
import importlib
import time

def get_platform():
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux"

def install_package(pkg):
    plat = get_platform()
    try:
        importlib.import_module(pkg)
        return True
    except ImportError:
        pass
    
    print(f"[*] Installing {pkg}...")
    
    if plat == "windows":
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"], capture_output=True, check=True)
            try:
                importlib.import_module(pkg)
                return True
            except:
                pass
        except:
            pass
    else:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", pkg, "--quiet"], capture_output=True, check=True)
            try:
                importlib.import_module(pkg)
                return True
            except:
                pass
        except:
            pass
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", pkg, "--quiet"], capture_output=True, check=True)
            try:
                importlib.import_module(pkg)
                return True
            except:
                pass
        except:
            pass
    
    return False

def ensure_dependencies():
    packages = [
        ("aiohttp", "aiohttp"),
        ("bs4", "beautifulsoup4"),
        ("holehe", "holehe")
    ]
    
    missing = []
    for mod_name, pkg_name in packages:
        try:
            importlib.import_module(mod_name)
        except ImportError:
            missing.append(pkg_name)
    
    if missing:
        print("\n[*] Installing required packages...")
        print("[*] This may take a moment...")
        
        for pkg in missing:
            if not install_package(pkg):
                print(f"[!] Failed to install {pkg}")
                print("[*] Trying fallback method...")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
                except:
                    print(f"[!] Please manually install: pip install {pkg}")
                    input("\nPress Enter after installing...")
                    try:
                        importlib.import_module(pkg.replace("-", "_"))
                    except:
                        pass

ensure_dependencies()

import asyncio
import re
import json
import aiohttp
from typing import Dict, List, Tuple, Optional
import holehe
from bs4 import BeautifulSoup

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
        self.total_modules = len(TARGET_MODULES)
        self.checked = 0
        self.found_accounts = []
        self.rate_limited = []
        self.errors = []
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
            'facebook.com': {'country': 'United States', 'code': 'US'},
            'twitter.com': {'country': 'United States', 'code': 'US'},
            'github.com': {'country': 'United States', 'code': 'US'},
        }
        
        if domain in specific:
            return specific[domain]
        
        return {'country': 'Unknown', 'code': 'XX'}
    
    async def check_module(self, module_name: str) -> Tuple[str, bool, Dict]:
        try:
            module = getattr(holehe.modules, module_name)
            result = await module(self.email)
            
            exists = False
            if isinstance(result, dict):
                exists = result.get('rateLimit', False) or result.get('exists', False) or result.get('found', False)
            
            return (module_name, exists, result)
        except Exception as e:
            return (module_name, False, {"error": str(e)})
    
    async def scan_all(self) -> Dict:
        print(f"\n[*] Scanning: {self.email}")
        print(f"[*] Country: {self.country_info['country']}")
        print(f"[*] Checking {self.total_modules} platforms...\n")
        
        tasks = [self.check_module(m) for m in TARGET_MODULES]
        
        for future in asyncio.as_completed(tasks):
            module_name, exists, result = await future
            self.checked += 1
            
            if exists:
                self.found_accounts.append(module_name)
            
            if result.get('rateLimit', False):
                self.rate_limited.append(module_name)
            
            if 'error' in result and result['error']:
                self.errors.append((module_name, result['error']))
            
            self.results[module_name] = {"exists": exists, "data": result}
            
            status = "FOUND" if exists else "NOT FOUND"
            print(f"  [{self.checked:02d}/{self.total_modules}] {module_name:12} {status}")
        
        return self.results
    
    def print_summary(self):
        print("\n" + "="*60)
        print(f"RESULTS FOR: {self.email}")
        print("="*60)
        print(f"Country: {self.country_info['country']}")
        print(f"Accounts found: {len(self.found_accounts)}")
        
        if self.found_accounts:
            print("\nFOUND ACCOUNTS:")
            for module in sorted(self.found_accounts):
                print(f"  - {module}")
        
        if self.rate_limited:
            print(f"\nRate Limited: {', '.join(self.rate_limited)}")
        
        print("="*60 + "\n")

async def main_async():
    print("\n" + "="*60)
    print("EMAIL TRACKER")
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
        
        confirm = input(f"Scan '{email}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.\n")
            continue
        
        start = time.time()
        tracker = EmailTracker(email)
        await tracker.scan_all()
        elapsed = time.time() - start
        
        tracker.print_summary()
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
