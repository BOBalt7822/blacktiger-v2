#!/usr/bin/env python3
import sys
import os
import subprocess
import importlib
import tempfile
import shutil
import time

def get_platform():
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux"

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True
    except:
        return False

def install_package(pkg):
    plat = get_platform()
    try:
        importlib.import_module(pkg)
        return True
    except ImportError:
        pass
    
    if plat == "windows":
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True, check=True)
            return True
        except:
            pass
    else:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", pkg], capture_output=True, check=True)
            try:
                importlib.import_module(pkg)
                return True
            except:
                pass
        except:
            pass
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", pkg], capture_output=True, check=True)
            try:
                importlib.import_module(pkg)
                return True
            except:
                pass
        except:
            pass
    
    return False

def create_venv_and_run():
    temp_dir = tempfile.mkdtemp()
    venv_path = os.path.join(temp_dir, "venv")
    subprocess.run([sys.executable, "-m", "venv", venv_path], capture_output=True)
    if sys.platform == "win32":
        pip_path = os.path.join(venv_path, "Scripts", "pip")
        python_path = os.path.join(venv_path, "Scripts", "python")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
        python_path = os.path.join(venv_path, "bin", "python")
    subprocess.run([pip_path, "install", "aiohttp", "beautifulsoup4", "holehe"], capture_output=True, check=False)
    script_path = os.path.join(temp_dir, "runner.py")
    with open(__file__, 'r') as f:
        content = f.read()
    content = content.replace("import sys", "import sys\nIN_VENV = True", 1)
    with open(script_path, 'w') as f:
        f.write(content)
    subprocess.run([python_path, script_path] + sys.argv[1:])
    shutil.rmtree(temp_dir, ignore_errors=True)
    sys.exit(0)

if not hasattr(sys, 'IN_VENV'):
    packages = ["aiohttp", "beautifulsoup4", "holehe"]
    missing = []
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("Installing dependencies...")
        installed_all = True
        for pkg in missing:
            if not install_package(pkg):
                installed_all = False
        if not installed_all:
            print("Creating isolated virtual environment...")
            create_venv_and_run()
        for pkg in missing:
            try:
                importlib.import_module(pkg)
            except ImportError:
                create_venv_and_run()

import asyncio
import re
import json
import aiohttp
from typing import Dict, List, Tuple, Optional

try:
    import holehe
except ImportError:
    create_venv_and_run()

TARGET_MODULES = [
    'facebook',
    'tiktok',
    'discord',
    'spotify',
    'snapchat',
    'github',
    'instagram',
    'twitter',
    'reddit',
    'pinterest',
    'tumblr',
    'twitch',
    'paypal',
    'adobe',
    'wordpress',
    'protonmail',
    'mailru',
    'yahoo',
    'microsoft',
    'linkedin'
]

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
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
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return self.extract_proxies(text)
        except:
            pass
        return []
    
    async def scrape_all(self) -> List[str]:
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}) as session:
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
    
    async def validate_all(self, max_check: int = 100) -> List[str]:
        if not self.proxies:
            return []
        to_check = self.proxies[:max_check]
        connector = aiohttp.TCPConnector(limit=50)
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

class CountryDetector:
    @staticmethod
    def get_domain_country(email: str) -> Dict:
        domain = email.split('@')[-1].lower()
        
        domain_country_map = {
            '.uk': {'country': 'United Kingdom', 'code': 'GB'},
            '.co.uk': {'country': 'United Kingdom', 'code': 'GB'},
            '.org.uk': {'country': 'United Kingdom', 'code': 'GB'},
            '.ac.uk': {'country': 'United Kingdom', 'code': 'GB'},
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
            '.hu': {'country': 'Hungary', 'code': 'HU'},
            '.gr': {'country': 'Greece', 'code': 'GR'},
            '.ru': {'country': 'Russia', 'code': 'RU'},
            '.ua': {'country': 'Ukraine', 'code': 'UA'},
            '.ro': {'country': 'Romania', 'code': 'RO'},
            '.bg': {'country': 'Bulgaria', 'code': 'BG'},
            '.hr': {'country': 'Croatia', 'code': 'HR'},
            '.sk': {'country': 'Slovakia', 'code': 'SK'},
            '.si': {'country': 'Slovenia', 'code': 'SI'},
            '.lt': {'country': 'Lithuania', 'code': 'LT'},
            '.lv': {'country': 'Latvia', 'code': 'LV'},
            '.ee': {'country': 'Estonia', 'code': 'EE'},
            '.ie': {'country': 'Ireland', 'code': 'IE'},
            '.is': {'country': 'Iceland', 'code': 'IS'},
            '.ca': {'country': 'Canada', 'code': 'CA'},
            '.mx': {'country': 'Mexico', 'code': 'MX'},
            '.br': {'country': 'Brazil', 'code': 'BR'},
            '.ar': {'country': 'Argentina', 'code': 'AR'},
            '.cl': {'country': 'Chile', 'code': 'CL'},
            '.co': {'country': 'Colombia', 'code': 'CO'},
            '.pe': {'country': 'Peru', 'code': 'PE'},
            '.jp': {'country': 'Japan', 'code': 'JP'},
            '.cn': {'country': 'China', 'code': 'CN'},
            '.in': {'country': 'India', 'code': 'IN'},
            '.kr': {'country': 'South Korea', 'code': 'KR'},
            '.sg': {'country': 'Singapore', 'code': 'SG'},
            '.my': {'country': 'Malaysia', 'code': 'MY'},
            '.ph': {'country': 'Philippines', 'code': 'PH'},
            '.vn': {'country': 'Vietnam', 'code': 'VN'},
            '.th': {'country': 'Thailand', 'code': 'TH'},
            '.id': {'country': 'Indonesia', 'code': 'ID'},
            '.pk': {'country': 'Pakistan', 'code': 'PK'},
            '.bd': {'country': 'Bangladesh', 'code': 'BD'},
            '.lk': {'country': 'Sri Lanka', 'code': 'LK'},
            '.np': {'country': 'Nepal', 'code': 'NP'},
            '.il': {'country': 'Israel', 'code': 'IL'},
            '.sa': {'country': 'Saudi Arabia', 'code': 'SA'},
            '.ae': {'country': 'UAE', 'code': 'AE'},
            '.tr': {'country': 'Turkey', 'code': 'TR'},
            '.au': {'country': 'Australia', 'code': 'AU'},
            '.nz': {'country': 'New Zealand', 'code': 'NZ'},
            '.za': {'country': 'South Africa', 'code': 'ZA'},
            '.ng': {'country': 'Nigeria', 'code': 'NG'},
            '.ke': {'country': 'Kenya', 'code': 'KE'},
            '.eg': {'country': 'Egypt', 'code': 'EG'}
        }
        
        if domain in domain_country_map:
            return domain_country_map[domain]
        
        for tld, info in domain_country_map.items():
            if domain.endswith(tld):
                return info
        
        domain_specific = {
            'gmail.com': {'country': 'United States', 'code': 'US'},
            'yahoo.com': {'country': 'United States', 'code': 'US'},
            'yahoo.co.uk': {'country': 'United Kingdom', 'code': 'GB'},
            'hotmail.com': {'country': 'United States', 'code': 'US'},
            'outlook.com': {'country': 'United States', 'code': 'US'},
            'live.com': {'country': 'United States', 'code': 'US'},
            'msn.com': {'country': 'United States', 'code': 'US'},
            'aol.com': {'country': 'United States', 'code': 'US'},
            'protonmail.com': {'country': 'Switzerland', 'code': 'CH'},
            'protonmail.ch': {'country': 'Switzerland', 'code': 'CH'},
            'mail.com': {'country': 'United States', 'code': 'US'},
            'yandex.com': {'country': 'Russia', 'code': 'RU'},
            'yandex.ru': {'country': 'Russia', 'code': 'RU'},
            'mail.ru': {'country': 'Russia', 'code': 'RU'},
            'rambler.ru': {'country': 'Russia', 'code': 'RU'},
            'icloud.com': {'country': 'United States', 'code': 'US'},
            'me.com': {'country': 'United States', 'code': 'US'},
            'mac.com': {'country': 'United States', 'code': 'US'},
            'facebook.com': {'country': 'United States', 'code': 'US'},
            'twitter.com': {'country': 'United States', 'code': 'US'},
            'instagram.com': {'country': 'United States', 'code': 'US'},
            'reddit.com': {'country': 'United States', 'code': 'US'},
            'github.com': {'country': 'United States', 'code': 'US'},
            'gitlab.com': {'country': 'United States', 'code': 'US'},
            'bitbucket.com': {'country': 'United States', 'code': 'US'},
            'dropbox.com': {'country': 'United States', 'code': 'US'},
            'mega.nz': {'country': 'New Zealand', 'code': 'NZ'},
            'tutanota.com': {'country': 'Germany', 'code': 'DE'},
            'tutanota.de': {'country': 'Germany', 'code': 'DE'},
            'posteo.de': {'country': 'Germany', 'code': 'DE'},
            'mailbox.org': {'country': 'Germany', 'code': 'DE'},
            'kolabnow.com': {'country': 'Switzerland', 'code': 'CH'},
            'fastmail.com': {'country': 'United States', 'code': 'US'},
            'fastmail.fm': {'country': 'United States', 'code': 'US'},
            'zoho.com': {'country': 'India', 'code': 'IN'},
            'zoho.eu': {'country': 'India', 'code': 'IN'},
            'hushmail.com': {'country': 'Canada', 'code': 'CA'},
            'hush.ai': {'country': 'Canada', 'code': 'CA'},
            'cyberia.net': {'country': 'Saudi Arabia', 'code': 'SA'},
            'inbox.lv': {'country': 'Latvia', 'code': 'LV'},
            'inbox.com': {'country': 'United States', 'code': 'US'},
            'lycos.com': {'country': 'United States', 'code': 'US'},
            'lycos.es': {'country': 'Spain', 'code': 'ES'},
            'lycos.it': {'country': 'Italy', 'code': 'IT'},
            'lycos.fr': {'country': 'France', 'code': 'FR'},
            'terra.com': {'country': 'Brazil', 'code': 'BR'},
            'terra.com.br': {'country': 'Brazil', 'code': 'BR'},
            'ig.com.br': {'country': 'Brazil', 'code': 'BR'},
            'uol.com.br': {'country': 'Brazil', 'code': 'BR'},
            'globo.com': {'country': 'Brazil', 'code': 'BR'},
            'globomail.com': {'country': 'Brazil', 'code': 'BR'},
            'xtra.co.nz': {'country': 'New Zealand', 'code': 'NZ'},
            'clear.net.nz': {'country': 'New Zealand', 'code': 'NZ'},
            'vodafone.co.nz': {'country': 'New Zealand', 'code': 'NZ'},
            'spark.co.nz': {'country': 'New Zealand', 'code': 'NZ'},
            'bigpond.com': {'country': 'Australia', 'code': 'AU'},
            'bigpond.net.au': {'country': 'Australia', 'code': 'AU'},
            'optusnet.com.au': {'country': 'Australia', 'code': 'AU'},
            'iinet.net.au': {'country': 'Australia', 'code': 'AU'},
            'internode.on.net': {'country': 'Australia', 'code': 'AU'},
            'tpg.com.au': {'country': 'Australia', 'code': 'AU'},
            'live.co.uk': {'country': 'United Kingdom', 'code': 'GB'},
            'live.fr': {'country': 'France', 'code': 'FR'},
            'live.de': {'country': 'Germany', 'code': 'DE'}
        }
        
        if domain in domain_specific:
            return domain_specific[domain]
        
        return {'country': 'Unknown', 'code': 'XX'}

class EmailTracker:
    def __init__(self, email: str, proxy_list: List[str] = None):
        self.email = email
        self.proxy_list = proxy_list or []
        self.proxy_index = 0
        self.results = {}
        self.total_modules = len(TARGET_MODULES)
        self.checked = 0
        self.found_accounts = []
        self.rate_limited = []
        self.errors = []
        self.country_info = CountryDetector.get_domain_country(email)
    
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
            
            exists = False
            if isinstance(result, dict):
                exists = result.get('rateLimit', False) or result.get('exists', False)
                if not exists:
                    exists = result.get('found', False)
                if not exists:
                    email_check = result.get('email', '')
                    if isinstance(email_check, str) and email_check.lower() == self.email.lower():
                        exists = True
            
            return (module_name, exists, result)
        except Exception as e:
            return (module_name, False, {"error": str(e)})
    
    async def scan_all(self) -> Dict:
        print(f"\n[*] Scanning for accounts using: {self.email}")
        print(f"[*] Domain: {self.email.split('@')[1]}")
        print(f"[*] Country: {self.country_info['country']} ({self.country_info['code']})")
        print(f"[*] Checking {self.total_modules} platforms...")
        print(f"[*] Using {len(self.proxy_list)} proxies\n")
        
        tasks = [self.check_module(m) for m in TARGET_MODULES]
        
        for future in asyncio.as_completed(tasks):
            module_name, exists, result = await future
            self.checked += 1
            
            if exists:
                self.found_accounts.append((module_name, result))
            
            if result.get('rateLimit', False):
                self.rate_limited.append(module_name)
            
            if 'error' in result and result['error']:
                self.errors.append((module_name, result['error']))
            
            self.results[module_name] = {
                "exists": exists,
                "data": result
            }
            
            if exists:
                status = "FOUND"
                color = "\033[91m"
            else:
                status = "NOT FOUND"
                color = "\033[92m"
            
            print(f"  [{self.checked:02d}/{self.total_modules}] {module_name:12} {color}{status}\033[0m")
        
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
            'instagram': 'https://instagram.com/',
            'twitter': 'https://twitter.com/',
            'reddit': 'https://reddit.com/user/',
            'pinterest': 'https://pinterest.com/',
            'tumblr': 'https://tumblr.com/',
            'twitch': 'https://twitch.tv/',
            'paypal': 'https://paypal.com/',
            'adobe': 'https://adobe.com/',
            'wordpress': 'https://wordpress.com/',
            'protonmail': 'https://protonmail.com/',
            'mailru': 'https://mail.ru/',
            'yahoo': 'https://yahoo.com/',
            'microsoft': 'https://microsoft.com/',
            'linkedin': 'https://linkedin.com/in/'
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
                    "rate_limit": result.get('rateLimit', False),
                    "username": result.get('username', '')
                })
        return links
    
    def print_summary(self):
        links = self.get_profile_links()
        found_count = len(links)
        
        print("\n" + "="*70)
        print(f"ACCOUNTS FOUND FOR: {self.email}")
        print("="*70)
        print(f"Country: {self.country_info['country']} ({self.country_info['code']})")
        print(f"Platforms checked: {self.total_modules}")
        print(f"Accounts found: {found_count}")
        print(f"Rate limited: {len(self.rate_limited)}")
        print(f"Errors: {len(self.errors)}")
        
        if links:
            print("\nFOUND ACCOUNTS:")
            print("-"*70)
            for link in sorted(links, key=lambda x: x['platform']):
                rate_limit = " [RATE LIMITED]" if link['rate_limit'] else ""
                username = f" (@{link['username']})" if link['username'] else ""
                print(f"  {link['platform']:12} -> {link['url']}{username}{rate_limit}")
        else:
            print("\nNo accounts found.")
        
        if self.errors:
            print("\nERRORS:")
            for module, error in self.errors:
                print(f"  {module}: {error[:100]}")
        
        print("="*70 + "\n")
    
    def save_results(self, filename: str = "results.json"):
        output = {
            "email": self.email,
            "domain": self.email.split('@')[1],
            "country": self.country_info,
            "timestamp": time.time(),
            "total_checked": self.total_modules,
            "accounts_found": len(self.get_profile_links()),
            "results": self.results
        }
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

async def main_async():
    print("\n" + "="*70)
    print("EMAIL TRACKER v3 - Fixed Country Detection")
    print("="*70)
    print("Checks: Facebook, TikTok, Discord, Spotify, Snapchat,")
    print("GitHub, Instagram, Twitter, Reddit, Pinterest, Tumblr,")
    print("Twitch, PayPal, Adobe, Wordpress, Protonmail, Mailru,")
    print("Yahoo, Microsoft, LinkedIn")
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
        print("[*] No proxies found. Scraping new ones...")
        proxy_list = await proxy_scraper.get_working()
        if proxy_list:
            proxy_scraper.save()
            print(f"[*] Saved {len(proxy_list)} proxies to proxies.txt")
    
    if not proxy_list:
        print("[!] No working proxies found. Running without proxies...")
    
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
        tracker.save_results(f"results_{email.split('@')[0]}.json")
        
        print(f"Completed in {elapsed:.2f} seconds.")
        print(f"Results saved to results_{email.split('@')[0]}.json")

def run():
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    run()
