"""Logique pure pour l'interface de démonstration du TP3."""
from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd

DEFAULT_SEUIL_INCERTITUDE = 0.60
SEUIL_INCERTITUDE = DEFAULT_SEUIL_INCERTITUDE


def classer_avis(texte: str, seuil: float = DEFAULT_SEUIL_INCERTITUDE) -> dict[str, Any]:
    """Retourne la prédiction du modèle et son statut métier.

    Un score inférieur au seuil déclenche le verdict « à vérifier » au lieu d'une
    décision automatique tranchée.
    """
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("Le texte ne peut pas être vide.")

    from src.predict import predict

    resultat = predict(texte)
    score = float(resultat["score"])
    label = str(resultat["label"])
    verdict = "à vérifier" if score < float(seuil) else label

    return {
        "label": label,
        "score": score,
        "verdict": verdict,
        "seuil": float(seuil),
        "automatique": score >= float(seuil),
    }


def traiter_fichier_csv(fichier: Any, seuil: float = DEFAULT_SEUIL_INCERTITUDE) -> pd.DataFrame:
    """Lit un CSV et ajoute les colonnes de prédiction, confiance et statut."""
    if isinstance(fichier, pd.DataFrame):
        dataframe = fichier.copy()
    elif hasattr(fichier, "read"):
        contenu = fichier.read()
        if isinstance(contenu, bytes):
            contenu = contenu.decode("utf-8")
        dataframe = pd.read_csv(StringIO(contenu))
    else:
        dataframe = pd.read_csv(fichier)

    if "review" not in dataframe.columns:
        raise ValueError("Le fichier doit contenir une colonne 'review'.")

    lignes = []
    for avis in dataframe["review"].fillna(""):
        prediction = classer_avis(str(avis), seuil=seuil)
        lignes.append(prediction)

    dataframe = dataframe.copy()
    dataframe["label"] = [ligne["label"] for ligne in lignes]
    dataframe["score"] = [ligne["score"] for ligne in lignes]
    dataframe["verdict"] = [ligne["verdict"] for ligne in lignes]
    dataframe["automatique"] = [ligne["automatique"] for ligne in lignes]
    dataframe = dataframe.sort_values("score", ascending=False, kind="mergesort").reset_index(drop=True)
    return dataframe


def resumer_lot(dataframe: pd.DataFrame) -> dict[str, int | float]:
    """Calcule le résumé chiffré d'un lot de commentaires."""
    if dataframe.empty:
        return {"total": 0, "positifs": 0, "negatifs": 0, "a_verifier": 0, "taux_a_verifier": 0.0}

    total = int(len(dataframe))
    positifs = int((dataframe["label"] == "positive").sum())
    negatifs = int((dataframe["label"] == "negative").sum())
    a_verifier = int((dataframe["verdict"] == "à vérifier").sum())
    return {
        "total": total,
        "positifs": positifs,
        "negatifs": negatifs,
        "a_verifier": a_verifier,
        "taux_a_verifier": round(a_verifier / total, 4) if total else 0.0,
    }


def exporter_csv(dataframe: pd.DataFrame) -> str:
    """Convertit un DataFrame traité au format CSV exploitable."""
    return dataframe.to_csv(index=False)


analyser_avis = classer_avis
traiter_lot = traiter_fichier_csv
resumer_avis = resumer_lot
exporter_resultats = exporter_csv

__all__ = [
    "DEFAULT_SEUIL_INCERTITUDE",
    "SEUIL_INCERTITUDE",
    "classer_avis",
    "analyser_avis",
    "traiter_fichier_csv",
    "traiter_lot",
    "resumer_lot",
    "resumer_avis",
    "exporter_csv",
    "exporter_resultats",
]
