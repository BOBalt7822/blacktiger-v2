

import requests, random, string, time, sys, os, json, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def run():
    print("\n" + "="*60)
    print("DISCORD 4-LETTER USERNAME CHECKER - ULTRA FAST")
    print("="*60)
    
    print("[1] Generate and check 4-letter usernames")
    print("[2] Check a specific username")
    print("[3] Back")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        generate_fast()
    elif choice == '2':
        check_specific()
    else:
        return

def check_username(username, proxy=None):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        if proxy:
            r = requests.get(f"https://discord.com/api/v9/users/{username}", headers=headers, timeout=2, proxies=proxy)
        else:
            r = requests.get(f"https://discord.com/api/v9/users/{username}", headers=headers, timeout=2)
        
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
    """Scrape free proxies from multiple sources"""
    proxies = []
    sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        "https://free-proxy-list.net/",
        "https://www.sslproxies.org/",
        "https://www.us-proxy.org/"
    ]
    
    print("[+] Scraping proxies...")
    for src in sources:
        try:
            r = requests.get(src, timeout=10)
            if r.status_code == 200:
                for line in r.text.split('\n'):
                    if ':' in line and '.' in line:
                        proxy = line.strip()
                        if proxy and not proxy.startswith('#'):
                            proxies.append({'http': proxy, 'https': proxy})
            time.sleep(0.5)
        except:
            pass
    
    # Remove duplicates
    unique = []
    seen = set()
    for p in proxies:
        if p['http'] not in seen:
            seen.add(p['http'])
            unique.append(p)
    
    print(f"[+] Found {len(unique)} proxies")
    return unique

def generate_fast():
    print("\n" + "="*60)
    print("ULTRA FAST USERNAME CHECKER")
    print("="*60)
    
    count = int(input("Number of usernames to check [1000]: ").strip() or "1000")
    threads = int(input("Threads [50]: ").strip() or "50")
    
    print("\nWebhook for hits (optional):")
    webhook = input("Webhook URL: ").strip()
    
    if webhook and webhook.startswith('https://discord.com/api/webhooks/'):
        print("[+] Webhook set!")
    else:
        print("[!] No webhook set")
    
    # Scrape proxies
    proxies = scrape_proxies()
    if not proxies:
        print("[!] No proxies found, running without proxies")
    
    print(f"\n[+] Checking {count} usernames with {threads} threads...")
    print("[+] Press Ctrl+C to stop\n")
    
    available = []
    checked = 0
    lock = threading.Lock()
    chars = string.ascii_lowercase + string.digits
    
    def worker(username):
        nonlocal checked
        proxy = random.choice(proxies) if proxies else None
        status = check_username(username, proxy)
        
        with lock:
            checked += 1
            if checked % 50 == 0:
                print(f"[+] Checked: {checked} | Available: {len(available)}")
            
            if status == "AVAILABLE":
                print(f"{GREEN}{username} AVAILABLE{RESET}")
                available.append(username)
                if webhook:
                    send_webhook(webhook, username)
            else:
                print(f"{RED}{username} TAKEN{RESET}")
    
    # Generate usernames
    usernames = [''.join(random.choices(chars, k=4)) for _ in range(count)]
    
    start = time.time()
    
    # Use ThreadPoolExecutor for ultra fast checking
    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(worker, usernames)
    
    elapsed = time.time() - start
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Checked: {count}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Speed: {count/elapsed:.0f} usernames/sec")
    print(f"{GREEN}Available: {len(available)}{RESET}")
    
    if available:
        print("\n" + "="*60)
        print("AVAILABLE USERNAMES:")
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
        print(f"\n{GREEN}[+] Username '{username}' is AVAILABLE!{RESET}")
    else:
        print(f"\n{RED}[-] Username '{username}' is TAKEN{RESET}")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    run()
