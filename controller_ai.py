
import os
import csv
import time
import joblib
import pandas as pd

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

        # Charger le modele IA
        saved = joblib.load("models/random_forest.pkl")
        self.model = saved["model"]
        self.features = saved["features"]

        self.datapaths = {}
        self.previous = {}
        self.interval = 2

        # H3 est connecte au port 3
        self.monitored_port = 3

        # Deux alertes consecutives necessaires
        self.anomaly_count = 0

        os.makedirs("data", exist_ok=True)
        self.csv_path = "data/predictions_live.csv"

        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "port",
                "rx_pps", "tx_pps",
                "rx_bps", "tx_bps",
                "prediction", "probability"
            ])

        self.monitor_thread = hub.spawn(self.monitor)

        self.logger.info("Modele Random Forest charge")
        self.logger.info("Detection IA active sur port 3")

    @set_ev_cls(
        ofp_event.EventOFPStateChange,
        [MAIN_DISPATCHER, DEAD_DISPATCHER]
    )
    def state_change(self, ev):
        dp = ev.datapath

        if ev.state == MAIN_DISPATCHER:
            self.datapaths[dp.id] = dp
            self.logger.info("Switch connecte : %s", dp.id)

        elif ev.state == DEAD_DISPATCHER:
            self.datapaths.pop(dp.id, None)
            self.previous = {
                k: v for k, v in self.previous.items()
                if k[0] != dp.id
            }
            self.anomaly_count = 0

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

            # Analyser uniquement le port H3
            if stat.port_no != self.monitored_port:
                continue

            key = (dp.id, stat.port_no)

            current = (
                stat.rx_packets,
                stat.tx_packets,
                stat.rx_bytes,
                stat.tx_bytes,
                now
            )

            if key not in self.previous:
                self.previous[key] = current
                continue

            old = self.previous[key]
            self.previous[key] = current

            dt = now - old[4]

            differences = [
                current[i] - old[i]
                for i in range(4)
            ]

            if dt <= 0 or any(d < 0 for d in differences):
                self.anomaly_count = 0
                continue

            rx_pps = differences[0] / dt
            tx_pps = differences[1] / dt
            rx_bps = differences[2] * 8 / dt
            tx_bps = differences[3] * 8 / dt

            sample = pd.DataFrame([{
                "rx_pps": rx_pps,
                "tx_pps": tx_pps,
                "rx_bps": rx_bps,
                "tx_bps": tx_bps
            }])

            sample = sample[self.features]

            prediction = int(self.model.predict(sample)[0])

            probabilities = self.model.predict_proba(sample)[0]
            classes = list(self.model.classes_)
            probability = float(
                probabilities[classes.index(1)]
            )

            if prediction == 1:
                self.anomaly_count += 1

                self.logger.warning(
                    "ANOMALIE | RX %.2f pkt/s | Prob %.2f",
                    rx_pps, probability
                )

                if self.anomaly_count >= 2:
                    self.logger.warning(
                        "ALERTE : trafic suspect persistant sur H3"
                    )
            else:
                self.anomaly_count = 0

                self.logger.info(
                    "NORMAL | RX %.2f pkt/s | Prob %.2f",
                    rx_pps, probability
                )

            with open(self.csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    now,
                    stat.port_no,
                    round(rx_pps, 2),
                    round(tx_pps, 2),
                    round(rx_bps, 2),
                    round(tx_bps, 2),
                    prediction,
                    round(probability, 4)
                ])
