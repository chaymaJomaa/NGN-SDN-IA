
import csv
import os
import time

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import (
    MAIN_DISPATCHER,
    DEAD_DISPATCHER,
    set_ev_cls
)
from ryu.lib import hub


class IntelligentSDNController(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.datapaths = {}
        self.previous = {}
        self.interval = 2
        self.label = os.environ.get("TRAFFIC_LABEL", "normal")

        os.makedirs("data", exist_ok=True)
        self.csv_path = os.environ.get(
            "TRAFFIC_CSV",
            "data/traffic.csv"
                                    )
        self.fields = [
            "timestamp", "switch_id", "port",
            "rx_packets", "tx_packets",
            "rx_bytes", "tx_bytes",
            "rx_pps", "tx_pps",
            "rx_bps", "tx_bps",
            "label"
        ]

        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.fields)

        self.monitor_thread = hub.spawn(self.monitor)
        self.logger.info("Controleur SDN initialise")

    @set_ev_cls(
        ofp_event.EventOFPStateChange,
        [MAIN_DISPATCHER, DEAD_DISPATCHER]
    )
    def state_change(self, ev):
        dp = ev.datapath

        if ev.state == MAIN_DISPATCHER:
            self.datapaths[dp.id] = dp
            self.logger.info("Switch connecte: %s", dp.id)

        elif ev.state == DEAD_DISPATCHER:
            self.datapaths.pop(dp.id, None)
            self.previous = {
                key: value
                for key, value in self.previous.items()
                if key[0] != dp.id
            }

    def monitor(self):
        while True:
            for dp in list(self.datapaths.values()):
                parser = dp.ofproto_parser
                req = parser.OFPPortStatsRequest(
                    dp, 0, dp.ofproto.OFPP_ANY
                )
                dp.send_msg(req)

            hub.sleep(self.interval)

    @set_ev_cls(
        ofp_event.EventOFPPortStatsReply,
        MAIN_DISPATCHER
    )
    def port_stats_reply(self, ev):
        dp = ev.msg.datapath
        now = time.time()

        for stat in ev.msg.body:
            if stat.port_no > 0xFFFFFF00:
                continue

            key = (dp.id, stat.port_no)

            current = (
                stat.rx_packets,
                stat.tx_packets,
                stat.rx_bytes,
                stat.tx_bytes,
                now
            )

            if key in self.previous:
                old = self.previous[key]
                dt = now - old[4]

                differences = [
                    current[i] - old[i]
                    for i in range(4)
                ]

                if dt > 0 and all(x >= 0 for x in differences):
                    rx_pps = differences[0] / dt
                    tx_pps = differences[1] / dt
                    rx_bps = differences[2] * 8 / dt
                    tx_bps = differences[3] * 8 / dt

                    row = [
                        now, dp.id, stat.port_no,
                        stat.rx_packets, stat.tx_packets,
                        stat.rx_bytes, stat.tx_bytes,
                        round(rx_pps, 2),
                        round(tx_pps, 2),
                        round(rx_bps, 2),
                        round(tx_bps, 2),
                        self.label
                    ]

                    with open(
                        self.csv_path, "a", newline=""
                    ) as f:
                        csv.writer(f).writerow(row)

                    self.logger.info(
                        "Port %s | RX %.2f pkt/s | TX %.2f pkt/s",
                        stat.port_no, rx_pps, tx_pps
                    )

            self.previous[key] = current

