"""Tests de l'interface de démonstration (TP3)."""

import pandas as pd

from ui.helpers import DEFAULT_SEUIL_INCERTITUDE, classer_avis, resumer_lot, traiter_fichier_csv


def test_analyse_avis_positive():
    resultat = classer_avis("Service impeccable et livraison très rapide !")
    assert resultat["label"] == "positive"
    assert resultat["score"] >= 0.5
    assert resultat["verdict"] == "positive"


def test_analyse_avis_avec_seuil_incertain():
    resultat = classer_avis("Produit correct mais pas exceptionnel", seuil=0.999)
    assert resultat["verdict"] == "à vérifier"
    assert 0.0 <= resultat["score"] <= 1.0


def test_traitement_lot_et_resume():
    dataframe = pd.DataFrame({
        "review": [
            "Service impeccable et livraison très rapide !",
            "Produit cassé et service client injoignable",
            "Très bien, mais pas parfait",
        ]
    })
    traite = traiter_fichier_csv(dataframe, seuil=0.60)
    resume = resumer_lot(traite)

    assert set(traite.columns) >= {"review", "label", "score", "verdict", "automatique"}
    assert resume["total"] == 3
    assert resume["positifs"] + resume["negatifs"] + resume["a_verifier"] == 3
    assert resume["taux_a_verifier"] >= 0.0
