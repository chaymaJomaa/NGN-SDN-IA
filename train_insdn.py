
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

# 1. Chemins
DATA_PATH = Path("data/insdn/insdn_processed.csv")
MODEL_PATH = Path("models/insdn_random_forest.pkl")
RESULTS_DIR = Path("results/insdn")
FIGURES_DIR = Path("results/figures")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 2. Chargement
print("Chargement du dataset InSDN...")

df = pd.read_csv(DATA_PATH)
print("Dimensions initiales :", df.shape)

if "target" not in df.columns:
    raise ValueError("Colonne target introuvable.")

# 3. Suppression des doublons exacts
before = len(df)
df = df.drop_duplicates().reset_index(drop=True)

print("Doublons supprimes :", before - len(df))

# Supprimer les observations ayant exactement les memes
# caracteristiques mais des etiquettes contradictoires
features = [col for col in df.columns if col != "target"]

conflicts = df.groupby(features, dropna=False)["target"].transform(
    "nunique"
) > 1

print("Lignes avec etiquettes contradictoires :", conflicts.sum())
df = df.loc[~conflicts].copy()

# Eviter une evaluation sur une seule classe
if df["target"].nunique() != 2:
    raise ValueError("Le dataset doit contenir les classes 0 et 1.")

# 4. Variables et etiquettes
X = df[features].astype(np.float32)
y = df["target"].astype(int)

print("\nRepartition des classes :")
print(y.value_counts().sort_index())

# 5. Separation 80 % / 20 %
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nEntrainement :", len(X_train))
print("Test :", len(X_test))

# 6. Modele Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_leaf=2,
    max_features="sqrt",
    class_weight="balanced_subsample",
    max_samples=0.8,
    n_jobs=-1,
    random_state=42
)

print("\nEntrainement en cours...")
model.fit(X_train, y_train)

# Evaluation du surapprentissage
train_pred = model.predict(X_train)

train_accuracy = accuracy_score(y_train, train_pred)
train_f1 = f1_score(y_train, train_pred)

print("\n=== OVERFITTING CHECK ===")
print(f"Train Accuracy : {train_accuracy:.4f}")
print(f"Train F1-score : {train_f1:.4f}")

# 7. Evaluation sur le test uniquement
y_pred = model.predict(X_test)

test_accuracy = accuracy_score(y_test, y_pred)
test_f1 = f1_score(y_test, y_pred)

print(f"Test Accuracy : {test_accuracy:.4f}")
print(f"Test F1-score : {test_f1:.4f}")

print(f"Accuracy Gap : {train_accuracy - test_accuracy:.4f}")
print(f"F1 Gap : {train_f1 - test_f1:.4f}")

metrics = {
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "precision": float(
        precision_score(y_test, y_pred, zero_division=0)
    ),
    "recall": float(
        recall_score(y_test, y_pred, zero_division=0)
    ),
    "f1_score": float(
        f1_score(y_test, y_pred, zero_division=0)
    )
}

cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
tn, fp, fn, tp = cm.ravel()

metrics["false_positive_rate"] = float(
    fp / (fp + tn) if fp + tn else 0
)

print("\n=== RESULTATS RANDOM FOREST ===")
for name, value in metrics.items():
    print(f"{name}: {value:.4f}")

print("\nRapport de classification :")
report = classification_report(
    y_test,
    y_pred,
    target_names=["Normal", "Attack"],
    zero_division=0
)
print(report)

print("\nMatrice de confusion :")
print(cm)

# 8. Sauvegarder les resultats
with open(RESULTS_DIR / "metrics.json", "w") as f:
    json.dump(
        {
            "metrics": metrics,
            "confusion_matrix": cm.tolist(),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features": features,
            "evaluation_protocol": (
                "Exploratory stratified random split "
                "after exact deduplication"
            )
        },
        f,
        indent=4
    )

(RESULTS_DIR / "classification_report.txt").write_text(report)

# 9. Matrice de confusion
disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Normal", "Attack"]
)
disp.plot(cmap="Blues", values_format="d")
plt.title("Random Forest - InSDN Confusion Matrix")
plt.tight_layout()
plt.savefig(
    FIGURES_DIR / "insdn_confusion_matrix.png",
    dpi=300
)
plt.close()

# 10. Importance des caracteristiques
importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

importance.to_csv(
    RESULTS_DIR / "feature_importance.csv",
    header=["importance"]
)

top = importance.head(15).sort_values()

plt.figure(figsize=(10, 7))
top.plot.barh()
plt.title("Top 15 Feature Importances - InSDN")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig(
    FIGURES_DIR / "insdn_feature_importance.png",
    dpi=300
)
plt.close()

# 11. Sauvegarder le modele
joblib.dump(
    {
        "model": model,
        "features": features,
        "classes": ["Normal", "Attack"]
    },
    MODEL_PATH,
    compress=3
)

print("\n=== FICHIERS GENERES ===")
print(MODEL_PATH)
print(RESULTS_DIR / "metrics.json")
print(RESULTS_DIR / "classification_report.txt")
print(FIGURES_DIR / "insdn_confusion_matrix.png")
print(FIGURES_DIR / "insdn_feature_importance.png")
print("\nEntrainement et evaluation termines.")
