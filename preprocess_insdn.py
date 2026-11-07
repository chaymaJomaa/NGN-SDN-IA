
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path("data/insdn/extracted")
OUTPUT = Path("data/insdn/insdn_processed.csv")

files = sorted(DATA_DIR.rglob("*.csv"))

if not files:
    raise SystemExit("Aucun fichier CSV trouve.")

datasets = []

# 1. Charger les fichiers
for file in files:
    print("Lecture :", file.name)

    df = pd.read_csv(file, low_memory=False)
    df.columns = df.columns.str.strip()

    if "Label" not in df.columns:
        print("Ignore : colonne Label absente")
        continue

    df["Label"] = df["Label"].astype("string").str.strip()
    df = df.dropna(subset=["Label"])

    datasets.append(df)

if not datasets:
    raise SystemExit("Aucune donnee utilisable.")

# 2. Garder les colonnes communes
common = set(datasets[0].columns)

for df in datasets[1:]:
    common &= set(df.columns)

common = sorted(common)
print("Colonnes communes :", len(common))

df = pd.concat(
    [part[common] for part in datasets],
    ignore_index=True
)

# 3. Classification binaire
df["target"] = (
    df["Label"].str.lower() != "normal"
).astype(int)

# 4. Retirer les identifiants et la cible originale
excluded = [
    "Label", "target", "Flow ID",
    "Src IP", "Dst IP",
    "Src Port", "Dst Port",
    "Source IP", "Destination IP",
    "Source Port", "Destination Port",
    "Timestamp", "SimillarHTTP"
]

feature_cols = [
    c for c in df.columns
    if c not in excluded
]

# 5. Conversion numerique
X = df[feature_cols].apply(
    pd.to_numeric,
    errors="coerce"
)

X = X.replace([np.inf, -np.inf], np.nan)

# Retirer les colonnes avec trop peu de valeurs valides
valid_ratio = X.notna().mean()
X = X.loc[:, valid_ratio >= 0.95]

# Retirer les lignes incompletes
valid_rows = X.notna().all(axis=1)
X = X.loc[valid_rows].copy()
y = df.loc[valid_rows, "target"].copy()

# Retirer les caracteristiques constantes
X = X.loc[:, X.nunique(dropna=False) > 1]

# 6. Construire le dataset
processed = X.copy()
processed["target"] = y.to_numpy()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
processed.to_csv(OUTPUT, index=False)

print("\n=== PRETRAITEMENT TERMINE ===")
print("Observations :", len(processed))
print("Caracteristiques :", len(X.columns))
print("\nClasses :")
print(processed["target"].value_counts().sort_index())

print("\nFichier cree :", OUTPUT)
