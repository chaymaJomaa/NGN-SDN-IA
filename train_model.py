
import pandas as pd
import joblib
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# 1. Charger le dataset
data = pd.read_csv("data/dataset_ml.csv")

features = [
    "rx_pps",
    "tx_pps",
    "rx_bps",
    "tx_bps"
]

X = data[features]
y = data["target"]

print("Nombre d'observations :", len(data))
print("Repartition :", y.value_counts().to_dict())

# 2. Creer le modele Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42,
    class_weight="balanced"
)

# 3. Entrainer le modele preliminaire
model.fit(X, y)

# 4. Diagnostic sur les donnees d'entrainement
# Ce n'est PAS une evaluation sur des donnees independantes.
y_pred = model.predict(X)

print("\n===== DIAGNOSTIC D'ENTRAINEMENT =====")
print("Accuracy :", accuracy_score(y, y_pred))
print("Precision :", precision_score(y, y_pred, zero_division=0))
print("Recall :", recall_score(y, y_pred, zero_division=0))
print("F1-score :", f1_score(y, y_pred, zero_division=0))

print("\nMatrice de confusion :")
print(confusion_matrix(y, y_pred))

print("\nRapport de classification :")
print(classification_report(y, y_pred, zero_division=0))

print("\nImportance des variables :")
for name, importance in zip(
    features, model.feature_importances_
):
    print(name, ":", round(importance, 4))

# 5. Sauvegarder le modele
os.makedirs("models", exist_ok=True)

joblib.dump(
    {"model": model, "features": features},
    "models/random_forest.pkl"
)

print("\nModele enregistre : models/random_forest.pkl")
