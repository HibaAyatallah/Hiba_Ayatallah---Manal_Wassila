# sentiment-app : dépôt du binôme

Application fil rouge du cours *Développement et déploiement d'applications intelligentes*.  
Ce dépôt retrace l'intégralité de la démarche, de l'analyse du problème métier jusqu'au déploiement de l'interface utilisateur :
- **Semaine 1 (TP1) :** Cadrage métier, environnement virtuel reproductible, initialisation Git et pipeline d'intégration continue (CI).
- **Semaine 2 (TP2) :** Entraînement sur données massives (Allociné, 20 000 avis), évaluation, analyse qualitative des erreurs et sérialisation du modèle (TF-IDF + Régression Logistique).
- **Semaine 3 (TP3) :** Interface interactive de démonstration **Streamlit**, traitement par lots CSV, séparation stricte de la logique et de l'affichage, et arbitrage métier du seuil d'incertitude.

---

## Démarrage rapide

### 1. Activer l'environnement virtuel
```bash
# Linux, macOS, Git Bash :
source .venv/bin/activate

# Windows PowerShell :
.\.venv\Scripts\Activate.ps1
```

*(Si nécessaire, installer les dépendances : `pip install -r requirements.txt`)*

### 2. Lancer la suite de tests automatisés
```bash
python scripts/check_setup.py    # diagnostic de l'environnement, des versions et de Git
pytest -q                        # 45 passed attendus en Semaine 3 (42 du modèle + 3 d'interface)
```

### 3. Lancer l'interface Streamlit
```bash
streamlit run ui/app.py
# ou via Python :
python -m streamlit run ui/app.py
```
L'interface s'ouvre automatiquement dans votre navigateur à l'adresse [http://localhost:8501](http://localhost:8501).

---

## Utilisation de l'application (Semaine 3)

L'application web Streamlit propose trois onglets conçus pour l'équipe relation client :

1. **Onglet « Un avis » (Contrôle S2) :**
   - Analyse instantanée d'un texte libre avec jauge de score.
   - Trois verdicts visuels : **Avis positif** (vert), **Avis négatif prioritaire** (rouge), ou **À vérifier par un agent** (orange) si la confiance est inférieure au seuil de 60 % (`SEUIL_INCERTITUDE = 0.60`).
2. **Onglet « Un fichier CSV » (Contrôle S3) :**
   - Téléversement d'un lot d'avis (ex. `data/sample_reviews.csv` ou `data/demo_reviews.csv`).
   - Affichage des métriques produit (volume total, part de négatifs, cas à vérifier).
   - Graphique de répartition et tableau dynamique trié avec les avis négatifs prioritaires en tête.
   - Bouton d'export pour télécharger le CSV enrichi avec les verdicts et scores.
3. **Onglet « Comment ça marche » :**
   - Explications méthodologiques, règles MLOps et guide d'interprétation pour les non-techniciens.

---

## Commandes utiles du projet

Toutes les commandes se lancent depuis la racine du dépôt :

```bash
# --- TP3 : Interface Streamlit & Tests ---
streamlit run ui/app.py               # Lancer l'interface web
pytest tests/test_ui.py -v           # Tester les fonctions pures de ui/helpers.py (3 passed)

# --- TP2 : Données & Entraînement ---
python src/make_demo.py              # Générer le jeu de test de démo (290 avis)
python src/train.py                  # Entraîner sur le jeu démo (F1: 0.879)
python src/train.py --allocine       # Entraîner sur le jeu complet Allociné (F1: 0.920)
python src/evaluate.py               # Rapport de classification et matrice de confusion
python src/predict.py "Votre texte"  # Inférence unitaire en ligne de commande

# --- TP1 : Diagnostic & Intégration continue ---
python scripts/check_setup.py        # Vérification complète de la configuration
pytest -q                            # Lancer l'intégralité des 48 tests
```

---

## Documentation et Livrables

| Document | Contenu |
| :--- | :--- |
| **`Resume/RESUME_GLOBAL.md`** | **Compte rendu global complet des 3 TP (8 sections notées sur 20)** |
| `Resume/RESUME_TP2.md` | Synthèse détaillée spécifique au TP2 (modèle & erreurs) |
| `Resume/RESUME_TP1.pdf` | Synthèse du cadrage et de l'environnement TP1 |
| `docs/semaine3.md` | Justification du seuil d'incertitude (0.60) et arbitrage métier |
| `docs/semaine2.md` | Analyse qualitative des erreurs du sac de mots sur les avis mitigés |
| `docs/cadrage/` | Fiches de cadrage des cas d'usage (pharmacie, règlement, avis négatifs) |
| `MARCHE-A-SUIVRE-TP3.md` / `TP3-ENONCE.md` | Guide et consignes officielles de la semaine 3 |

---

## Structure finale du dépôt

```text
sentiment-app/
├── README.md, TP1-ENONCE.md, TP2-ENONCE.md, TP3-ENONCE.md, TESTS.md
├── requirements.txt, requirements.lock, .gitignore, pytest.ini, Makefile
├── .github/workflows/ci.yml       # Intégration continue GitHub Actions
├── ui/                            # Interface utilisateur (TP3)
│   ├── app.py                     # Script d'affichage et composants Streamlit
│   └── helpers.py                 # Fonctions pures testables sans serveur web
├── src/                           # Pipeline ML (TP2)
│   ├── make_demo.py               # Générateur du jeu de démo
│   ├── train.py                   # Entraînement et sérialisation
│   ├── evaluate.py                # Rapport de classification et matrice de confusion
│   └── predict.py                 # Logique de prédiction
├── tests/                         # 48 tests automatisés
│   ├── test_environment.py       # 23 tests d'environnement et de structure (TP1)
│   ├── test_cadrage.py           # 12 tests des fiches de cadrage (TP1)
│   ├── test_git_history.py       # 3 tests de l'historique et des auteurs (TP1)
│   ├── test_model.py             # 4 tests sur le modèle et metrics.json (TP2)
│   └── test_ui.py                # 6 tests sur les helpers Streamlit (TP3)
├── models/
│   ├── .gitkeep
│   ├── metrics.json               # Métriques versionnées (preuve de qualité pour la CI)
│   └── sentiment.joblib           # Binaire du modèle (local, ignoré par Git)
├── Resume/
│   ├── RESUME_GLOBAL.md           # Synthèse globale des TP1, TP2 et TP3
│   ├── RESUME_TP2.md             # Synthèse TP2
│   ├── RESUME_TP1.pdf             # Synthèse TP1
│   └── screenshots/              # Captures d'écran de démonstration Streamlit
├── docs/
│   ├── semaine2.md                # Analyse des erreurs
│   ├── semaine3.md                # Analyse du seuil d'incertitude
│   ├── screenshots/              # Captures d'écran intégrées au compte rendu
│   └── cadrage/                   # Fiches de décision
└── data/
    ├── sample_reviews.csv         # Échantillon de test
    └── demo_reviews.csv          # Données de démo (régénérables par make_demo.py)
```

---

## Membres du binôme

| Rôle | Nom | Identifiant GitHub | Travaux réalisés sur l'ensemble du projet |
| :--- | :--- | :--- | :--- |
| **Membre A** | Hiba Ayatallah | [@HibaAyatallah](https://github.com/HibaAyatallah) | - **TP1 :** Création du dépôt GitHub, cadrage en binôme, documentation.<br>- **TP2 :** Cadrage métier, revue des métriques d'évaluation.<br>- **TP3 :** Conception fonctionnelle de l'interface et validation des cas de tests métier. |
| **Membre B** | Manal Wassila | [@manalwassila](https://github.com/manalwassila) | - **TP1 :** Configuration de l'environnement virtuel, validation des tests CI.<br>- **TP2 :** Pipeline scikit-learn, entraînement Allociné, analyse des erreurs.<br>- **TP3 :** Développement des composants Streamlit, fonctions de helpers, tests unitaires UI. |
