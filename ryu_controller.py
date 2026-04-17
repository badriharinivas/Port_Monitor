#!/usr/bin/env python3
"""
ryu_controller.py - Ryu SDN controller that detects port up/down events,
logs them, generates alerts, and writes status for the monitor to display.
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
import json
import os
from datetime import datetime

LOG_FILE    = "/tmp/port_monitor.log"
ALERT_FILE  = "/tmp/port_alerts.log"
STATUS_FILE = "/tmp/port_status.json"

class PortMonitorController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PortMonitorController, self).__init__(*args, **kwargs)
        self.port_status = {}   # { dpid: { port_no: state } }
        self.log_event("Ryu Port Monitor Controller started", "INFO")

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def log_event(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        print(entry)
        with open(LOG_FILE, 'a') as f:
            f.write(entry + "\n")

    def generate_alert(self, dpid, port_no, old_state, new_state):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = (f"[{timestamp}] ALERT: Switch {dpid} Port {port_no} "
               f"changed {old_state} -> {new_state}")
        with open(ALERT_FILE, 'a') as f:
            f.write(msg + "\n")

        print("\n" + "=" * 55)
        print(f"  !! PORT STATE CHANGE DETECTED")
        print(f"     Switch : {dpid}")
        print(f"     Port   : {port_no}")
        print(f"     Change : {old_state} -> {new_state}")
        print(f"     Time   : {timestamp}")
        print("=" * 55 + "\n")

    def save_status(self):
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "switches": {
                str(dpid): {
                    str(port): state
                    for port, state in ports.items()
                }
                for dpid, ports in self.port_status.items()
            }
        }
        with open(STATUS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------------------ #
    #  Switch connects — learn all existing ports                         #
    # ------------------------------------------------------------------ #

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        dpid     = datapath.id
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser

        self.log_event(f"Switch connected: dpid={dpid}", "INFO")
        self.port_status.setdefault(dpid, {})

        # Install table-miss flow so packets are sent to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

        # Request port descriptions to learn initial state
        req = parser.OFPPortDescStatsRequest(datapath, 0)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_reply_handler(self, ev):
        datapath = ev.msg.datapath
        dpid     = datapath.id
        ofproto  = datapath.ofproto

        self.port_status.setdefault(dpid, {})

        for port in ev.msg.body:
            if port.port_no >= ofproto.OFPP_MAX:
                continue
            state = "DOWN" if (port.state & ofproto.OFPPS_LINK_DOWN) else "UP"
            self.port_status[dpid][port.port_no] = state
            self.log_event(
                f"Initial state — Switch {dpid} Port {port.port_no} "
                f"({port.name.decode()}): {state}", "STATUS"
            )

        self.save_status()

    # ------------------------------------------------------------------ #
    #  Port status change event — core detection logic                    #
    # ------------------------------------------------------------------ #

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg      = ev.msg
        datapath = msg.datapath
        dpid     = datapath.id
        ofproto  = datapath.ofproto
        port     = msg.desc
        port_no  = port.port_no
        reason   = msg.reason

        if port_no >= ofproto.OFPP_MAX:
            return

        new_state = "DOWN" if (port.state & ofproto.OFPPS_LINK_DOWN) else "UP"
        old_state = self.port_status.get(dpid, {}).get(port_no, "UNKNOWN")

        reason_map = {
            ofproto.OFPPR_ADD:    "PORT ADDED",
            ofproto.OFPPR_DELETE: "PORT DELETED",
            ofproto.OFPPR_MODIFY: "PORT MODIFIED",
        }
        reason_str = reason_map.get(reason, "UNKNOWN")

        self.log_event(
            f"Switch {dpid} Port {port_no} [{reason_str}]: "
            f"{old_state} -> {new_state}", "CHANGE"
        )

        if old_state != new_state:
            self.generate_alert(dpid, port_no, old_state, new_state)

        self.port_status.setdefault(dpid, {})[port_no] = new_state
        self.save_status()
