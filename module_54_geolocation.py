#!/usr/bin/env python3
# IP Geolocation Module 
import requests
import json
import os
import time

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_ip_location(ip):
    results = {}
    
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=8)
        if r.status_code == 200:
            data = r.json()
            if 'error' not in data:
                results['ipinfo'] = data
    except:
        pass
    
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query", timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data.get('status') != 'fail':
                results['ipapi'] = data
    except:
        pass
    
    return results

def run():
    clear_screen()
    print("\n" + "="*60)
    print("IP GEOLOCATION - MOST ACCURATE")
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
    
    results = get_ip_location(ip)
    
    if not results:
        print("Could not get location data. Check your internet.")
        input("\nPress Enter to continue...")
        return
    
    ipinfo = results.get('ipinfo', {})
    ipapi = results.get('ipapi', {})
    
    country = ipinfo.get('country', ipapi.get('country', 'Unknown'))
    country_code = ipinfo.get('country', ipapi.get('countryCode', ''))
    region = ipinfo.get('region', ipapi.get('regionName', 'Unknown'))
    city = ipinfo.get('city', ipapi.get('city', 'Unknown'))
    postal = ipinfo.get('postal', ipapi.get('zip', 'Unknown'))
    timezone = ipinfo.get('timezone', ipapi.get('timezone', 'Unknown'))
    isp = ipinfo.get('org', ipapi.get('isp', 'Unknown'))
    
    loc = ipinfo.get('loc', '')
    if loc:
        lat, lon = loc.split(',')
    else:
        lat = ipapi.get('lat', 'Unknown')
        lon = ipapi.get('lon', 'Unknown')
    
    print(f"IP Address:    {ip}")
    print(f"Country:       {country}")
    print(f"Region:        {region}")
    print(f"City:          {city}")
    print(f"Postal Code:   {postal}")
    print(f"Latitude:      {lat}")
    print(f"Longitude:     {lon}")
    
    if lat and lon and lat != 'Unknown' and lon != 'Unknown':
        print(f"Google Maps:   https://maps.google.com/maps?q={lat},{lon}")
        print(f"OpenStreetMap: https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=12")
    
    print(f"Timezone:      {timezone}")
    print(f"ISP:           {isp}")
    
    if ipapi.get('mobile'):
        print("Mobile/Proxy:  Mobile connection")
    if ipapi.get('proxy'):
        print("Mobile/Proxy:  Proxy/VPN detected")
    
    org = ipinfo.get('org', '')
    if org and org != isp:
        print(f"Organization:  {org}")
    
    if 'as' in ipapi:
        print(f"AS Number:     {ipapi.get('as', 'Unknown')}")
    
    print("-"*60)
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    run()
