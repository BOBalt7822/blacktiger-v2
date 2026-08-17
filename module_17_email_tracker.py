#!/usr/bin/env python3
# email_tracker.py

import asyncio
import sys
import time
import re
import aiohttp
from typing import Dict, List, Tuple, Optional

try:
    import holehe
except ImportError:
    print("\n[!] Install: pip install holehe aiohttp beautifulsoup4")
    sys.exit(1)

TARGET_MODULES = [
    'facebook',
    'tiktok',
    'discord',
    'spotify',
    'snapchat',
    'github',
    'instagram'
]

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
]

class ProxyScraper:
    def __init__(self):
        self.proxies = []
        self.valid_proxies = []
    
    @staticmethod
    def extract_proxies(text: str) -> List[str]:
        pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b'
        matches = re.findall(pattern, text)
        valid = []
        for m in matches:
            parts = m.split(':')
            if len(parts) == 2:
                ip_parts = parts[0].split('.')
                try:
                    if all(0 <= int(p) <= 255 for p in ip_parts):
                        port = int(parts[1])
                        if 1 <= port <= 65535:
                            valid.append(m)
                except:
                    pass
        return list(set(valid))
    
    async def scrape_url(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return self.extract_proxies(text)
        except:
            pass
        return []
    
    async def scrape_all(self) -> List[str]:
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
            tasks = [self.scrape_url(session, url) for url in PROXY_SOURCES]
            results = await asyncio.gather(*tasks)
        all_proxies = []
        for res in results:
            all_proxies.extend(res)
        self.proxies = list(set(all_proxies))
        return self.proxies
    
    async def validate_proxy(self, session: aiohttp.ClientSession, proxy: str) -> bool:
        try:
            proxy_url = f"http://{proxy}"
            async with session.get("http://httpbin.org/ip", proxy=proxy_url, timeout=5) as resp:
                return resp.status == 200
        except:
            return False
    
    async def validate_all(self, max_check: int = 200) -> List[str]:
        if not self.proxies:
            return []
        to_check = self.proxies[:max_check]
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(connector=connector, headers={"User-Agent": "Mozilla/5.0"}) as session:
            tasks = [self.validate_proxy(session, p) for p in to_check]
            results = await asyncio.gather(*tasks)
        self.valid_proxies = [p for p, ok in zip(to_check, results) if ok]
        return self.valid_proxies
    
    async def get_working(self) -> List[str]:
        print("[*] Scraping proxies...")
        await self.scrape_all()
        print(f"[*] Found {len(self.proxies)} raw proxies. Validating...")
        await self.validate_all()
        print(f"[*] {len(self.valid_proxies)} working proxies found.")
        return self.valid_proxies
    
    def save(self, filename: str = "proxies.txt"):
        with open(filename, 'w') as f:
            f.write("\n".join(self.valid_proxies))
    
    def load(self, filename: str = "proxies.txt") -> List[str]:
        try:
            with open(filename, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
            self.valid_proxies = proxies
            self.proxies = proxies
            return proxies
        except:
            return []

class EmailTracker:
    def __init__(self, email: str, proxy_list: List[str] = None):
        self.email = email
        self.proxy_list = proxy_list or []
        self.proxy_index = 0
        self.results = {}
        self.total_modules = len(TARGET_MODULES)
        self.checked = 0
        self.found_accounts = []
    
    def get_proxy(self) -> Optional[str]:
        if not self.proxy_list:
            return None
        proxy = self.proxy_list[self.proxy_index % len(self.proxy_list)]
        self.proxy_index += 1
        return f"http://{proxy}"
    
    async def check_module(self, module_name: str) -> Tuple[str, bool, Dict]:
        try:
            module = getattr(holehe.modules, module_name)
            proxy = self.get_proxy()
            result = await module(self.email, proxy=proxy)
            exists = result.get('rateLimit', False) or result.get('exists', False)
            return (module_name, exists, result)
        except Exception as e:
            return (module_name, False, {"error": str(e)})
    
    async def scan_all(self) -> Dict:
        print(f"\n[*] Scanning for accounts using: {self.email}")
        print(f"[*] Checking {self.total_modules} platforms...")
        print(f"[*] Using {len(self.proxy_list)} proxies\n")
        
        tasks = [self.check_module(m) for m in TARGET_MODULES]
        
        for future in asyncio.as_completed(tasks):
            module_name, exists, result = await future
            self.checked += 1
            self.results[module_name] = {
                "exists": exists,
                "data": result
            }
            
            if exists:
                self.found_accounts.append((module_name, result))
            
            status = "FOUND" if exists else "NOT FOUND"
            print(f"  [{self.checked:02d}/{self.total_modules}] {module_name:10} {status}")
        
        return self.results
    
    def get_profile_links(self) -> List[Dict]:
        links = []
        platform_urls = {
            'facebook': 'https://facebook.com/',
            'tiktok': 'https://tiktok.com/@',
            'discord': 'https://discord.com/users/',
            'spotify': 'https://open.spotify.com/user/',
            'snapchat': 'https://snapchat.com/add/',
            'github': 'https://github.com/',
            'instagram': 'https://instagram.com/'
        }
        
        for module_name, data in self.results.items():
            if data["exists"]:
                result = data["data"]
                profile_url = result.get('profile', '')
                if not profile_url:
                    base = platform_urls.get(module_name, '')
                    if base:
                        username = result.get('username', '')
                        if not username:
                            username = self.email.split('@')[0]
                        profile_url = base + username
                    else:
                        profile_url = f"https://{module_name}.com/"
                
                links.append({
                    "platform": module_name.capitalize(),
                    "url": profile_url,
                    "email": result.get('email', self.email),
                    "rate_limit": result.get('rateLimit', False)
                })
        return links
    
    def print_summary(self):
        links = self.get_profile_links()
        
        print("\n" + "="*60)
        print(f"ACCOUNTS FOUND FOR: {self.email}")
        print("="*60)
        print(f"Platforms checked: {self.total_modules}")
        print(f"Accounts found: {len(links)}")
        
        if links:
            print("\nFOUND:")
            print("-"*50)
            for link in sorted(links, key=lambda x: x['platform']):
                rate_limit = " RATE LIMITED" if link['rate_limit'] else ""
                print(f"  {link['platform']:10} -> {link['url']}{rate_limit}")
        else:
            print("\nNo accounts found.")
        
        print("="*60 + "\n")

async def main_async():
    print("\n" + "="*60)
    print("EMAIL TRACKER")
    print("="*60)
    print("Facebook, TikTok, Discord, Spotify, Snapchat, GitHub, Instagram")
    print("Type 'exit' or 'quit' to stop.\n")
    
    proxy_scraper = ProxyScraper()
    proxy_list = []
    
    try:
        proxy_list = proxy_scraper.load()
        if proxy_list:
            print(f"[*] Loaded {len(proxy_list)} proxies from file")
    except:
        pass
    
    if not proxy_list:
        proxy_list = await proxy_scraper.get_working()
        if proxy_list:
            proxy_scraper.save()
    
    while True:
        email = input("\nEnter email: ").strip().lower()
        
        if email.lower() in ['exit', 'quit', '']:
            print("Exiting...")
            break
        
        if '@' not in email or '.' not in email:
            print("Invalid email format.")
            continue
        
        confirm = input(f"Scan '{email}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            continue
        
        start_time = time.time()
        tracker = EmailTracker(email, proxy_list)
        await tracker.scan_all()
        elapsed = time.time() - start_time
        
        tracker.print_summary()
        
        print(f"Completed in {elapsed:.2f} seconds.")

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
