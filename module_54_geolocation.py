#!/usr/bin/env python3
# IP Geolocation Module

import requests
import json
import os

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def run():
    clear_screen()
    print("\n" + "="*60)
    print("IP GEOLOCATION")
    print("="*60)
    
    ip = input("IP address (or 'me' for your IP): ").strip()
    
    if ip.lower() == 'me':
        try:
            r = requests.get('https://api.ipify.org?format=json', timeout=5)
            ip = r.json()['ip']
            print(f"Your IP: {ip}")
        except Exception as e:
            print(f"Could not get your IP: {e}")
            input("\nPress Enter to continue...")
            return
    
    if not ip:
        print("No IP entered.")
        input("\nPress Enter to continue...")
        return
    
    print(f"\nLooking up: {ip}")
    print("-"*60)
    
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=8)
        
        if r.status_code == 200:
            data = r.json()
            
            if 'error' in data:
                print(f"Error: {data['error']}")
                input("\nPress Enter to continue...")
                return
            
            print(f"IP Address:    {data.get('ip', ip)}")
            print(f"Country:       {data.get('country', 'Unknown')}")
            print(f"Region:        {data.get('region', 'Unknown')}")
            print(f"City:          {data.get('city', 'Unknown')}")
            print(f"Postal Code:   {data.get('postal', 'Unknown')}")
            
            loc = data.get('loc', '')
            if loc:
                lat, lon = loc.split(',')
                print(f"Latitude:      {lat}")
                print(f"Longitude:     {lon}")
                print(f"Google Maps:   https://maps.google.com/maps?q={lat},{lon}")
            
            print(f"Timezone:      {data.get('timezone', 'Unknown')}")
            print(f"ISP:           {data.get('org', 'Unknown')}")
            
        else:
            print(f"HTTP Error: {r.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Connection error. Check your internet.")
    except requests.exceptions.Timeout:
        print("Request timed out. Try again.")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-"*60)
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    run()
