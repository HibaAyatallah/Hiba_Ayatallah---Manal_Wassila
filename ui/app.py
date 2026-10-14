"""Interface Streamlit du module de sentiment."""
from __future__ import annotations

import streamlit as st

from ui.helpers import DEFAULT_SEUIL_INCERTITUDE, classer_avis, exporter_csv, resumer_lot, traiter_fichier_csv

st.set_page_config(page_title="Analyse de sentiment", page_icon="💬")
st.title("Analyse de sentiment des avis clients")
st.caption("Modèle TF-IDF + Régression logistique, avec seuil d'incertitude métier.")


@st.cache_resource
def charger_modele():
    """Charge le modèle sérialisé une seule fois par processus Streamlit."""
    from src.predict import charger_modele as chargeur

    try:
        return chargeur()
    except FileNotFoundError:
        return None


modele = charger_modele()
if modele is None:
    st.error("Modèle introuvable. Lancez d'abord : python src/train.py")
    st.stop()

onglet_simple, onglet_lot = st.tabs(["Un avis", "Un fichier CSV"])

with onglet_simple:
    texte = st.text_area("Avis à analyser", "Service impeccable et livraison très rapide !", height=120)
    seuil = st.slider("Seuil d'incertitude", min_value=0.50, max_value=0.90, value=DEFAULT_SEUIL_INCERTITUDE, step=0.01)

    if st.button("Analyser", type="primary"):
        if not texte.strip():
            st.warning("Saisissez un avis avant de lancer l'analyse.")
        else:
            resultat = classer_avis(texte, seuil=seuil)
            score = resultat["score"]
            label = resultat["label"]
            verdict = resultat["verdict"]

            if verdict == "à vérifier":
                st.warning(f"À vérifier : le modèle estime un {label} à {score:.0%}, sous le seuil de {seuil:.0%}.")
            elif label == "positive":
                st.success(f"Avis positif · confiance {score:.0%}")
            else:
                st.error(f"Avis négatif · confiance {score:.0%}")

            st.progress(float(score))
            st.caption(f"Seuil retenu : {seuil:.0%} | verdict final : {verdict}")

with onglet_lot:
    fichier = st.file_uploader("Fichier CSV", type=["csv"]) 
    seuil_lot = st.slider("Seuil d'incertitude du lot", min_value=0.50, max_value=0.90, value=DEFAULT_SEUIL_INCERTITUDE, step=0.01, key="seuil_lot")

    if fichier is not None:
        try:
            dataframe = traiter_fichier_csv(fichier, seuil=seuil_lot)
        except ValueError as exc:
            st.error(str(exc))
        else:
            resume = resumer_lot(dataframe)
            col1, col2, col3 = st.columns(3)
            col1.metric("Positifs", resume["positifs"])
            col2.metric("Négatifs", resume["negatifs"])
            col3.metric("À vérifier", resume["a_verifier"])

            st.dataframe(dataframe[["review", "label", "score", "verdict"]].sort_values("score", ascending=False), use_container_width=True)
            st.download_button(
                "Télécharger les résultats",
                exporter_csv(dataframe).encode("utf-8"),
                "resultats_sentiment.csv",
                "text/csv",
            )
