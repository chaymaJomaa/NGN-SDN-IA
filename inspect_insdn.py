
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/insdn/extracted")

files = sorted(DATA_DIR.rglob("*.csv"))

print("=" * 60)
print("INS-DN DATASET INSPECTION")
print("=" * 60)

if not files:
    raise SystemExit("Aucun fichier CSV trouve.")

for file in files:
    print("\nFichier :", file)
    print("Taille :", round(file.stat().st_size / (1024**2), 2), "Mo")

    # Lire seulement les premieres lignes
    df = pd.read_csv(file, nrows=10, low_memory=False)

    print("Nombre de colonnes :", len(df.columns))
    print("\nColonnes disponibles :")

    for column in df.columns:
        print(" -", column)

    # Recherche des colonnes de classification
    possible_labels = [
        col for col in df.columns
        if "label" in col.lower()
        or "attack" in col.lower()
        or "class" in col.lower()
    ]

    print("\nColonnes de classification possibles :")
    print(possible_labels)

    if possible_labels:
        # Lecture de la seule colonne de classification
        label = possible_labels[-1]

        labels = pd.read_csv(
            file,
            usecols=[label],
            low_memory=False
        )

        print("\nRepartition des classes :")
        print(labels[label].value_counts(dropna=False).head(30))

print("\nInspection terminee.")
