# Port Status Monitoring Tool

A Software Defined Networking (SDN) mini project that monitors switch port states in real time using **Mininet** and the **Ryu SDN Controller** on Ubuntu.

---

## Project Overview

This tool detects port up/down events on an OpenFlow-enabled switch, logs all state changes, generates alerts, and displays a live terminal status dashboard — all powered by Ryu's OpenFlow 1.3 event system.

| Requirement | Implementation |
|---|---|
| Detect port up/down events | Ryu `EventOFPPortStatus` OpenFlow handler |
| Log changes | Timestamped entries written to `/tmp/port_monitor.log` |
| Generate alerts | Console output + `/tmp/port_alerts.log` |
| Display status | Live terminal dashboard refreshing every 2 seconds |

---

## Project Structure

```
port_monitor/
├── topology.py           # Mininet star topology (4 hosts, 1 switch) connecting to Ryu
├── ryu_controller.py     # Ryu SDN app — detects port events, logs, alerts
├── port_monitor.py       # Live terminal status dashboard
└── simulate_events.py    # Simulates port up/down events for testing
```

### Output Files (generated at runtime)

```
/tmp/port_monitor.log     # All events with timestamps
/tmp/port_alerts.log      # Alerts only — one line per state transition
/tmp/port_status.json     # Current port states (read by port_monitor.py)
```

---

## SDN Architecture

```
┌─────────────────────────────────┐
│       Application Layer         │
│       port_monitor.py           │  ← Live terminal dashboard
└────────────────┬────────────────┘
                 │ reads JSON
┌────────────────▼────────────────┐
│        Control Layer            │
│     Ryu Controller (port 6633)  │  ← OpenFlow 1.3 event handling
│     ryu_controller.py           │
└────────────────┬────────────────┘
                 │ OpenFlow 1.3
┌────────────────▼────────────────┐
│    Infrastructure Layer         │
│    Mininet + OVS Switch s1      │  ← Emulated network
│    Hosts: h1, h2, h3, h4        │
└─────────────────────────────────┘
```

---

## Network Topology

```
    h1 (10.0.0.1)
        |
    h2 (10.0.0.2) ── [s1] ── h3 (10.0.0.3)
        |
    h4 (10.0.0.4)
```

- **Switch:** s1 (Open vSwitch, OpenFlow 1.3)
- **Hosts:** h1–h4 with IPs 10.0.0.1–10.0.0.4/24
- **Controller:** Ryu RemoteController on 127.0.0.1:6633

---

## Prerequisites

- VirtualBox with Ubuntu 22.04 LTS
- Python 3.9 (for Ryu compatibility)
- Python 3.12 (system default, for Mininet scripts)

---

## Installation

### Step 1 — Install Mininet
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y mininet net-tools
```

### Step 2 — Install Python 3.9
```bash
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.9 python3.9-dev python3.9-distutils build-essential libffi-dev
```

### Step 3 — Install pip for Python 3.9
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.9 get-pip.py
```

### Step 4 — Install Ryu and dependencies
```bash
sudo python3.9 -m pip install setuptools==58.0.0 --force-reinstall
sudo python3.9 -m pip install cffi cryptography
sudo python3.9 -m pip install eventlet==0.30.2
sudo python3.9 -m pip install ryu
```

### Step 5 — Verify Ryu
```bash
python3.9 -m ryu.cmd.manager --version
# Expected output: ryu 4.34
```

### Step 6 — Clone the repository
```bash
git clone https://github.com/badriharinivas/Port_Monitor.git
cd Port_Monitor
chmod +x topology.py port_monitor.py simulate_events.py ryu_controller.py
```

---

## Running the Project

Open **4 terminals** and run each command in order:

### Terminal 1 — Start Ryu Controller (start this first)
```bash
sudo python3.9 -m ryu.cmd.manager ~/port_monitor/ryu_controller.py
```
Wait until the output stops scrolling and shows `loading app`.

### Terminal 2 — Start Mininet Topology
```bash
cd ~/port_monitor
sudo python3 topology.py
```
You will see the `mininet>` prompt. Leave it running.

### Terminal 3 — Start Live Dashboard
```bash
cd ~/port_monitor
sudo python3 port_monitor.py
```
The terminal will refresh every 2 seconds showing port states.

### Terminal 4 — Simulate Port Events
```bash
cd ~/port_monitor
sudo python3 simulate_events.py
```
This brings ports up and down in 3 cycles with 5-second intervals.

---

## Testing Port Events (Manual)

Inside the Mininet CLI (Terminal 2), you can manually trigger events:

```bash
# Bring a link down
mininet> link s1 h1 down

# Bring a link back up
mininet> link s1 h1 up
```

Watch Terminal 1 (Ryu) for alerts and Terminal 3 for the updated dashboard.

---

## Viewing Logs

Run these in any free terminal:

```bash
# View all logged events
cat /tmp/port_monitor.log

# View alerts only
cat /tmp/port_alerts.log

# Watch logs live
tail -f /tmp/port_monitor.log
```

### Sample Log Output
```
[2024-04-09 19:45:10] [INFO]   Ryu Port Monitor Controller started
[2024-04-09 19:45:23] [STATUS] Switch 1 Port 1 (s1-eth1): UP
[2024-04-09 19:45:30] [CHANGE] Switch 1 Port 1 [PORT MODIFIED]: UP -> DOWN
[2024-04-09 19:45:35] [CHANGE] Switch 1 Port 1 [PORT MODIFIED]: DOWN -> UP
```

### Sample Alert Output
```
[2024-04-09 19:45:30] ALERT: Switch 1 Port 1 changed UP -> DOWN
[2024-04-09 19:45:35] ALERT: Switch 1 Port 1 changed DOWN -> UP
```

---

## How It Works

1. **Ryu connects** to the OVS switch over OpenFlow 1.3 on port 6633
2. On switch connection, Ryu **requests port descriptions** to learn initial states
3. A **table-miss flow rule** is installed so the controller stays active
4. When a port changes state, OVS sends an **EventOFPPortStatus** message to Ryu
5. Ryu checks the `OFPPS_LINK_DOWN` flag to determine UP or DOWN
6. The event is **logged**, an **alert is generated**, and `/tmp/port_status.json` is updated
7. `port_monitor.py` reads the JSON every 2 seconds and **redraws the terminal dashboard**

---

## Student Details

| Field | Details |
|---|---|
| Name | Badri Harinivas |
| SRN | PES2UG24AM037 |
| Subject | Computer Networks |
| Subject Code | UE24CS252B |
| Institution | PES University EC Campus |

---

## License

This project is submitted as part of the academic curriculum at PES University EC Campus.
