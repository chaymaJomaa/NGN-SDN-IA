
import pandas as pd

# Charger les predictions du controleur
df = pd.read_csv("data/predictions_live.csv")

# Selectionner les anomalies detectees
anomalies = df[df["prediction"] == 1].copy()

print("===== ANALYSE DES PREDICTIONS =====")
print("Nombre total :", len(df))
print("Nombre d'anomalies :", len(anomalies))

if not anomalies.empty:
    print("\n===== ANOMALIES DETECTEES =====")

    print(anomalies[[
        "timestamp",
        "rx_pps",
        "tx_pps",
        "rx_bps",
        "tx_bps",
        "probability"
    ]].to_string(index=False))

    print("\n===== STATISTIQUES =====")
    print("RX moyen :", round(anomalies["rx_pps"].mean(), 2))
    print("RX maximum :", round(anomalies["rx_pps"].max(), 2))
    print(
        "Probabilite moyenne :",
        round(anomalies["probability"].mean(), 4)
    )
else:
    print("Aucune anomalie detectee.")
