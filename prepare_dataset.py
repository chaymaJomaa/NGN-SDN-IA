
import pandas as pd
from pathlib import Path

DATA = Path("data")

normal = pd.read_csv(DATA / "normal_01.csv")
anomaly = pd.read_csv(DATA / "anomaly_01.csv")

# Analyser uniquement le port 3 (H3)
normal = normal[normal["port"] == 3].copy()
anomaly = anomaly[anomaly["port"] == 3].copy()

# Supprimer les périodes sans trafic
normal = normal[normal["rx_pps"] > 0].copy()
anomaly = anomaly[anomaly["rx_pps"] > 0].copy()

# Étiquettes expérimentales
normal["target"] = 0
anomaly["target"] = 1

features = [
    "rx_pps",
    "tx_pps",
    "rx_bps",
    "tx_bps"
]

columns = features + ["target"]

dataset = pd.concat(
    [normal[columns], anomaly[columns]],
    ignore_index=True
)

dataset.to_csv(DATA / "dataset_ml.csv", index=False)

print("Dataset prépare avec succès !")
print("\nNombre d'observations :", len(dataset))
print("\nRépartition des classes :")
print(dataset["target"].value_counts())
print("\nStatistiques :")
print(dataset.groupby("target")[features].mean())
