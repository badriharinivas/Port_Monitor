#!/usr/bin/env python3
"""
port_monitor.py - Reads port status written by Ryu and displays
a live terminal dashboard.
"""
import json
import os
import time
from datetime import datetime

STATUS_FILE   = "/tmp/port_status.json"
LOG_FILE      = "/tmp/port_monitor.log"
ALERT_FILE    = "/tmp/port_alerts.log"
POLL_INTERVAL = 2

def read_status():
    if not os.path.exists(STATUS_FILE):
        return None
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def read_recent_alerts(n=5):
    if not os.path.exists(ALERT_FILE):
        return []
    with open(ALERT_FILE, 'r') as f:
        lines = f.readlines()
    return [l.strip() for l in lines[-n:]][::-1]

def display(data):
    os.system('clear')
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 55)
    print("       PORT STATUS MONITOR — LIVE VIEW (Ryu)")
    print(f"       Updated: {now}")
    print("=" * 55)

    if not data:
        print("\n  Waiting for Ryu controller data...")
        print("\n  Make sure ryu-manager is running in Terminal 1")
        print("=" * 55)
        return

    switches = data.get("switches", {})
    if not switches:
        print("\n  No switches connected yet...")
    else:
        for dpid, ports in switches.items():
            print(f"\n  Switch DPID: {dpid}")
            print(f"  {'PORT':<10} {'STATUS':<10}")
            print("  " + "-" * 25)
            for port_no, state in sorted(ports.items(), key=lambda x: int(x[0])):
                indicator = "[UP]  " if state == "UP" else "[DOWN]"
                print(f"  {port_no:<10} {indicator}")

    print("\n" + "=" * 55)
    alerts = read_recent_alerts()
    if alerts:
        print("  RECENT ALERTS:")
        print("  " + "-" * 50)
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("  No alerts yet.")

    print("=" * 55)
    print(f"\n  Log    : {LOG_FILE}")
    print(f"  Alerts : {ALERT_FILE}")
    print("\n  Press Ctrl+C to stop")
    print("=" * 55)

def monitor():
    print("[*] Port monitor started. Waiting for Ryu data...\n")
    while True:
        data = read_status()
        display(data)
        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n[*] Monitor stopped.")
