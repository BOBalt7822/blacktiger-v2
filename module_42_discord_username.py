

import requests, random, string, time, sys, os, json, threading, queue
from datetime import datetime

def run():
    print("\n" + "="*60)
    print("DISCORD 4-LETTER USERNAME CHECKER")
    print("="*60)
    
    print("[1] Generate and check 4-letter usernames (Fast)")
    print("[2] Check a specific username")
    print("[3] Back")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        generate_fast()
    elif choice == '2':
        check_specific()
    else:
        return

def check_username_fast(username):
    """Check if username exists on Discord - FAST API method"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        r = requests.get(f"https://discord.com/api/v9/users/{username}", headers=headers, timeout=2)
        
        if r.status_code == 200:
            return "taken"
        elif r.status_code == 404:
            return "available"
        else:
            return "unknown"
    except:
        return "unknown"

def send_webhook(webhook, username):
    """Send hit to Discord webhook"""
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

def generate_fast():
    print("\n" + "="*60)
    print("FAST USERNAME GENERATOR & CHECKER")
    print("="*60)
    
    count = int(input("Number of usernames to check [1000]: ").strip() or "1000")
    threads = int(input("Threads [20]: ").strip() or "20")
    
    print("\nWebhook for hits (optional):")
    print("Leave blank for no webhook")
    webhook = input("Webhook URL: ").strip()
    
    if webhook and webhook.startswith('https://discord.com/api/webhooks/'):
        print("[+] Webhook set! Hits will be sent")
    else:
        print("[!] No webhook set. Hits will only be saved to file")
    
    print(f"\n[+] Generating and checking {count} usernames with {threads} threads...")
    print("[+] Press Ctrl+C to stop\n")
    print("="*60)
    
    available = []
    taken = []
    unknown = []
    total_checked = 0
    total_hits = 0
    lock = threading.Lock()
    q = queue.Queue()
    stop_event = threading.Event()
    
    # Fill queue with usernames
    chars = string.ascii_lowercase + string.digits
    for _ in range(count):
        username = ''.join(random.choices(chars, k=4))
        q.put(username)
    
    def worker():
        nonlocal total_checked, total_hits
        while not stop_event.is_set():
            try:
                username = q.get(timeout=1)
            except:
                break
            
            status = check_username_fast(username)
            
            with lock:
                total_checked += 1
                
                if status == "available":
                    available.append(username)
                    total_hits += 1
                    print(f"[HIT] {username} AVAILABLE!")
                    if webhook:
                        send_webhook(webhook, username)
                elif status == "taken":
                    taken.append(username)
                else:
                    unknown.append(username)
                
                if total_checked % 100 == 0:
                    print(f"[+] Checked: {total_checked} | Hits: {total_hits}")
            
            q.task_done()
    
    start = time.time()
    
    # Start threads
    worker_threads = []
    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.start()
        worker_threads.append(t)
    
    try:
        q.join()
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
        stop_event.set()
    
    stop_event.set()
    for t in worker_threads:
        t.join()
    
    elapsed = time.time() - start
    
    # Results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Total checked: {total_checked}")
    print(f"Available: {len(available)}")
    print(f"Taken: {len(taken)}")
    print(f"Unknown: {len(unknown)}")
    print(f"Speed: {total_checked/elapsed:.0f}/s")
    print(f"Time: {elapsed:.2f}s")
    
    if available:
        print("\n" + "="*60)
        print("AVAILABLE USERNAMES:")
        print("="*60)
        for i, name in enumerate(available, 1):
            print(f"  [{i:02d}] {name}")
        
        # Save to file
        try:
            out_dir = os.path.expanduser("~/Downloads/BlackTiger_Output")
            os.makedirs(out_dir, exist_ok=True)
            path = os.path.join(out_dir, "available_usernames.txt")
            with open(path, 'w') as f:
                f.write("AVAILABLE DISCORD USERNAMES\n")
                f.write("="*40 + "\n")
                for name in available:
                    f.write(f"{name}\n")
            print(f"\n[+] Available usernames saved to: {path}")
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
    status = check_username_fast(username)
    
    if status == "available":
        print(f"\n[+] Username '{username}' is AVAILABLE!")
        print("   Try registering it on Discord quickly")
    elif status == "taken":
        print(f"\n[-] Username '{username}' is TAKEN")
    else:
        print(f"\n[?] Could not determine availability")
        print("   Try checking manually on Discord")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    run()
