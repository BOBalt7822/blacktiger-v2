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
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query", timeout=8)
        
        if r.status_code == 200:
            data = r.json()
            
            if data.get('status') == 'fail':
                print("Geolocation failed. Invalid IP or rate limited.")
                print(f"Message: {data.get('message', 'Unknown error')}")
                input("\nPress Enter to continue...")
                return
            
            print(f"IP Address:    {data.get('query', ip)}")
            print(f"Country:       {data.get('country', 'Unknown')}")
            print(f"Region:        {data.get('regionName', 'Unknown')}")
            print(f"City:          {data.get('city', 'Unknown')}")
            print(f"Postal Code:   {data.get('zip', 'Unknown')}")
            print(f"Latitude:      {data.get('lat', 'Unknown')}")
            print(f"Longitude:     {data.get('lon', 'Unknown')}")
            print(f"Timezone:      {data.get('timezone', 'Unknown')}")
            print(f"ISP:           {data.get('isp', 'Unknown')}")
            print(f"Organization:  {data.get('org', 'Unknown')}")
            print(f"AS Number:     {data.get('as', 'Unknown')}")
            
            lat = data.get('lat')
            lon = data.get('lon')
            if lat and lon:
                print(f"Google Maps:   https://maps.google.com/maps?q={lat},{lon}")
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
