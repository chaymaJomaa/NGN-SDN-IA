
import csv
from pathlib import Path
from statistics import mean, median

DATA_DIR = Path("data")

files = {
    "NORMAL": DATA_DIR / "normal_01.csv",
    "ANOMALY": DATA_DIR / "anomaly_01.csv"
}

def load_data(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def analyze(name, path):
    rows = load_data(path)

    print(f"\n===== {name} =====")
    print("Total observations :", len(rows))

    for port in ["1", "2", "3"]:
        selected = [
            r for r in rows
            if r["port"] == port
        ]

        if not selected:
            continue

        rx_pps = [float(r["rx_pps"]) for r in selected]
        tx_pps = [float(r["tx_pps"]) for r in selected]

        active = sum(v > 0 for v in rx_pps)

        print(f"\nPort {port}")
        print("Observations :", len(selected))
        print("Periodes RX actives :", active)
        print("RX moyen :", round(mean(rx_pps), 2))
        print("RX median :", round(median(rx_pps), 2))
        print("RX maximum :", round(max(rx_pps), 2))
        print("TX moyen :", round(mean(tx_pps), 2))
        print("TX maximum :", round(max(tx_pps), 2))

for name, path in files.items():
    analyze(name, path)

print("\nAnalyse terminee.")
