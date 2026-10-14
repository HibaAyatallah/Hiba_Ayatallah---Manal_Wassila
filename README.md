# sentiment-app : dépôt du binôme

Application fil rouge du cours *Développement et déploiement d'applications intelligentes*.  
Ce dépôt grandit chaque semaine :
- **Semaine 1 (TP1) :** Cadrage métier, mise en place de l'environnement reproductible, initialisation Git et intégration continue.
- **Semaine 2 (TP2) :** Entraînement, évaluation, analyse des erreurs et sérialisation du modèle de sentiment (TF-IDF + Régression Logistique).

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

### 2. Vérifier l'état et les tests
```bash
python scripts/check_setup.py    # diagnostic de l'environnement, des versions et de Git
pytest -q                        # 42 passed attendus en Semaine 2
```

---

## Commandes de la Semaine 2 (Modèle & Évaluation)

Toutes les commandes se lancent depuis la racine du dépôt :

```bash
# 1. Générer le jeu de données de démonstration (290 avis équilibrés, dont 100 mitigés)
python src/make_demo.py

# 2. Entraîner le modèle de sentiment
python src/train.py              # entraînement sur le jeu démo (F1 macro: 0.879)
python src/train.py --allocine   # entraînement sur 20 000 avis Allociné (F1 macro: 0.920)

# 3. Évaluer les performances et afficher la matrice de confusion
python src/evaluate.py

# 4. Tester une prédiction unitaire
python src/predict.py "Service impeccable et livraison très rapide !"
```

> **Principe MLOps :** Le modèle sérialisé `models/sentiment.joblib` et les données `data/demo_reviews.csv` sont ignorés par Git car régénérables. Seul le fichier de mesure [models/metrics.json](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/models/metrics.json) est versionné.

---

## Par où commencer & Documentation

| Fichier | Description |
| --- | --- |
| `MARCHE-A-SUIVRE-TP2.md` | Guide pas à pas de la semaine 2 et contrôles C1 à C5 |
| `TP2-ENONCE.md` | Énoncé officiel du TP2 : objectifs et démarches |
| `docs/semaine2.md` | Analyse qualitative des erreurs du modèle sur les avis mitigés |
| `Resume/RESUME_TP2.md` | Compte rendu complet et structuré du TP2 (8 sections) |
| `MARCHE-A-SUIVRE.md` / `TP1-ENONCE.md` | Consignes et cadrage de la semaine 1 |
| `docs/cadrage/` | Fiches de cadrage des cas métiers (pharmacie, règlement, avis négatifs) |

---

## Structure du dépôt (Semaine 2)

```text
sentiment-app/
├── README.md, TP1-ENONCE.md, TP2-ENONCE.md, MARCHE-A-SUIVRE*.md, TESTS.md
├── Makefile, requirements.txt, requirements.lock, .gitignore, pytest.ini
├── .github/workflows/ci.yml       # Intégration continue (GitHub Actions)
├── docs/
│   ├── cadrage/                   # cas1-pharmacie.md, cas2-reglement.md, cas3-avis-negatifs.md
│   └── semaine2.md                # Analyse des erreurs (sac de mots, avis mitigés)
├── Resume/
│   ├── RESUME_TP1.pdf             # Synthèse TP1
│   └── RESUME_TP2.md             # Compte rendu global TP1 & TP2
├── src/
│   ├── make_demo.py               # Générateur du jeu de données synthétique
│   ├── train.py                   # Entraînement Pipeline (TfidfVectorizer + LogisticRegression)
│   ├── evaluate.py                # Rapport de classification et matrice de confusion
│   └── predict.py                 # Fonction d'inférence autonome
├── models/
│   ├── .gitkeep
│   ├── metrics.json               # Métriques validées et versionnées dans Git
│   └── sentiment.joblib           # Modèle binaire (local, ignoré par Git)
├── tests/                         # 42 tests unitaires automatisés
│   ├── test_environment.py       # 23 tests d'environnement et de structure
│   ├── test_cadrage.py           # 12 tests des fiches de cadrage
│   ├── test_git_history.py       # 3 tests de l'historique et des commits
│   └── test_model.py             # 4 tests sur le modèle et metrics.json
├── scripts/                       # check_setup, setup, init_depot, verif_clone
└── data/
    ├── sample_reviews.csv         # Échantillon d'avis
    └── demo_reviews.csv          # Données de démo (régénérables par make_demo.py)
```

---

## Membres du binôme

| Rôle | Nom | Identifiant GitHub | Travaux réalisés |
| :--- | :--- | :--- | :--- |
| **Membre A** | Hiba Ayatallah | [@HibaAyatallah](https://github.com/HibaAyatallah) | Semaine 1 : création du dépôt, initialisation Git, cadrage.<br>Semaine 2 : cadrage métier, revue des métriques et documentation GitHub. |
| **Membre B** | Manal Wassila | [@manalwassila](https://github.com/manalwassila) | Semaine 1 : configuration de l'environnement, validation des tests.<br>Semaine 2 : pipeline de modélisation, entraînement Allociné, analyse des erreurs, passage des 42 tests. |
