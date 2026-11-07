
import pandas as pd

files = {
    "Normal": "data/normal_01.csv",
    "Anomaly": "data/anomaly_01.csv"
}

for name, path in files.items():
    df = pd.read_csv(path)

    # Port de H3
    df = df[df["port"] == 3].copy()

    print("\n" + "=" * 55)
    print("SCENARIO :", name)
    print("=" * 55)

    print("Nombre d'observations :", len(df))

    print("\nStatistiques RX packets/second:")
    print(df["rx_pps"].describe().round(2))

    print("\nRepartition par intensite:")

    inactive = (df["rx_pps"] == 0).sum()
    low = (
        (df["rx_pps"] > 0)
        & (df["rx_pps"] <= 5)
    ).sum()

    medium = (
        (df["rx_pps"] > 5)
        & (df["rx_pps"] <= 20)
    ).sum()

    high = (df["rx_pps"] > 20).sum()

    print("Inactif (0 pps) :", inactive)
    print("Faible (0-5 pps) :", low)
    print("Moyen (5-20 pps) :", medium)
    print("Rapide (>20 pps) :", high)

    print("\nEtiquettes presentes :")
    print(df["label"].value_counts())

    print("\nPremieres observations :")
    print(
        df[["timestamp", "rx_pps", "tx_pps", "label"]]
        .head(10)
        .to_string(index=False)
    )
