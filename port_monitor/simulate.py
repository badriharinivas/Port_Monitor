#!/usr/bin/env python3
import subprocess
import time

def run_cmd(cmd):
    print(f"[CMD] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERR] {result.stderr.strip()}")
    else:
        print(f"[OK]")

def bring_down(switch, port_num):
    iface = f"{switch}-eth{port_num}"
    run_cmd(f"ip link set {iface} down")
    print(f"[EVENT] {iface} -> DOWN\n")

def bring_up(switch, port_num):
    iface = f"{switch}-eth{port_num}"
    run_cmd(f"ip link set {iface} up")
    print(f"[EVENT] {iface} -> UP\n")

def simulate():
    print("\n=== Port Event Simulator ===")
    print("Simulating port down/up events on switch s1\n")

    for cycle in range(3):
        print(f"--- Cycle {cycle + 1} ---")

        bring_down('s1', 1)
        time.sleep(5)
        bring_up('s1', 1)
        time.sleep(5)

        bring_down('s1', 2)
        time.sleep(5)
        bring_up('s1', 2)
        time.sleep(5)

    print("[*] Simulation complete.")

if __name__ == '__main__':
    simulate()
