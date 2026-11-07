
import joblib
import pandas as pd

# Charger le modele entraine
saved = joblib.load("models/random_forest.pkl")

model = saved["model"]
features = saved["features"]

print("Modele Random Forest charge avec succes !")

# Exemples artificiels pour tester le fonctionnement
samples = pd.DataFrame([
    [1.2, 1.4, 900, 1050],
    [2.0, 2.2, 1500, 1700],
    [35.0, 34.0, 25000, 24500],
    [40.0, 39.0, 31000, 30000]
], columns=features)

predictions = model.predict(samples)

print("\n===== PREDICTIONS IA =====")

for i, prediction in enumerate(predictions):
    label = "ANOMALIE" if prediction == 1 else "NORMAL"

    print(
        f"Observation {i+1} : "
        f"{label} "
        f"(RX={samples.iloc[i]['rx_pps']} pkt/s)"
    )
