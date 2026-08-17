#!/usr/bin/env python3
# Discord 4-Letter Username Checker 
# Made by BOB

import requests, random, string, time, sys, os, json, threading, queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def run():
    print("\n" + "="*60)
    print("DISCORD 4-LETTER USERNAME CHECKER ")
    print("="*60)
    
    print("[1] Generate and check 4-letter usernames")
    print("[2] Check a specific username")
    print("[3] Back")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        generate_lightning()
    elif choice == '2':
        check_specific()
    else:
        return

def check_username(username, proxy=None, session=None):
    try:
        if session:
            r = session.get(f"https://discord.com/api/v9/users/{username}", timeout=1)
        elif proxy:
            r = requests.get(f"https://discord.com/api/v9/users/{username}", timeout=1, proxies=proxy)
        else:
            r = requests.get(f"https://discord.com/api/v9/users/{username}", timeout=1)
        
        if r.status_code == 200:
            return "TAKEN"
        elif r.status_code == 404:
            return "AVAILABLE"
        else:
            return "TAKEN"
    except:
        return "TAKEN"

def send_webhook(webhook, username):
    if not webhook or not webhook.startswith('https://discord.com/api/webhooks/'):
        return
    try:
        data = {
            "embeds": [{
                "title": "HIT FOUND!",
                "description": f"**Username:** `{username}`\n**Link:** https://discord.com/users/{username}",
                "color": 0x00ff00,
                "footer": {"text": "BlackTiger"},
                "timestamp": datetime.now().isoformat()
            }],
            "username": "BlackTiger"
        }
        requests.post(webhook, json=data, timeout=5)
    except:
        pass

def scrape_proxies():
    proxies = []
    sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        "https://free-proxy-list.net/",
        "https://www.sslproxies.org/",
    ]
    
    for src in sources:
        try:
            r = requests.get(src, timeout=5)
            if r.status_code == 200:
                for line in r.text.split('\n'):
                    if ':' in line and '.' in line:
                        proxy = line.strip()
                        if proxy and not proxy.startswith('#'):
                            proxies.append(proxy)
        except:
            pass
    
    return list(set(proxies))

def generate_lightning():
    print("\n" + "="*60)
    print("LIGHTNING SPEED CHECKER")
    print("="*60)
    
    count = int(input("Number of usernames [5000]: ").strip() or "5000")
    webhook = input("Webhook URL (optional): ").strip()
    
    print("\n[+] Loading proxies...")
    proxies = scrape_proxies()
    print(f"[+] {len(proxies)} proxies loaded")
    
    print(f"\n[+] Checking {count} usernames at 2000+/sec...\n")
    
    available = []
    chars = string.ascii_lowercase + string.digits
    usernames = [''.join(random.choices(chars, k=4)) for _ in range(count)]
    
    results = []
    lock = threading.Lock()
    
    # Create sessions for each thread
    def create_session():
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        return session
    
    def worker(username):
        proxy = random.choice(proxies) if proxies else None
        session = create_session()
        status = check_username(username, proxy, session)
        return username, status
    
    start = time.time()
    
    # Use more threads for faster processing
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(worker, username) for username in usernames]
        for future in as_completed(futures):
            username, status = future.result()
            if status == "AVAILABLE":
                print(f"{GREEN}{username}{RESET}")
                available.append(username)
                if webhook:
                    send_webhook(webhook, username)
            else:
                print(f"{RED}{username}{RESET}")
    
    elapsed = time.time() - start
    
    print("\n" + "="*60)
    print(f"Checked: {count}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Speed: {count/elapsed:.0f}/s")
    print(f"{GREEN}Available: {len(available)}{RESET}")
    
    if available:
        print("\n" + "="*60)
        print("AVAILABLE:")
        print("="*60)
        for name in available:
            print(f"  {GREEN}{name}{RESET}")
        
        try:
            out_dir = os.path.expanduser("~/Downloads/BlackTiger_Output")
            os.makedirs(out_dir, exist_ok=True)
            path = os.path.join(out_dir, "available_usernames.txt")
            with open(path, 'w') as f:
                for name in available:
                    f.write(f"{name}\n")
            print(f"\n[+] Saved to: {path}")
        except:
            pass
    
    input("\nPress Enter to continue...")

def check_specific():
    print("\n" + "="*60)
    print("CHECK SPECIFIC USERNAME")
    print("="*60)
    
    username = input("Enter 4-letter username: ").strip().lower()
    
    if not username:
        print("No username entered")
        input("\nPress Enter to continue...")
        return
    
    if len(username) != 4:
        print("Username must be exactly 4 characters")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n[+] Checking: {username}")
    status = check_username(username)
    
    if status == "AVAILABLE":
        print(f"\n{GREEN}[+] AVAILABLE!{RESET}")
    else:
        print(f"\n{RED}[-] TAKEN{RESET}")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    run()
