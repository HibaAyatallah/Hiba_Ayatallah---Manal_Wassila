# Compte rendu global des TP1, TP2 et TP3

**Binôme :** Hiba Ayatallah (@HibaAyatallah) et Manal Wassila (@manalwassila)
**Dépôt :** HibaAyatallah/Hiba_Ayatallah---Manal_Wassila
**Date :** 14 octobre 2026
**Module :** Développement et déploiement d'applications intelligentes

## 1. Le besoin et son cadrage

Le projet répond à un besoin de service client : repérer les avis négatifs pour qu'un agent les examine en priorité. Le modèle organise la file, mais ne répond pas au client et ne décide pas d'un remboursement. Les erreurs n'ont pas le même coût : un avis négatif manqué peut retarder sa prise en charge ; un avis positif signalé à tort mobilise inutilement un agent. Le cadrage privilégie donc le rappel négatif, tout en conservant le F1 macro comme mesure globale.

Nous avons retenu le machine learning supervisé pour le cas 3, la priorisation des avis négatifs. **(a) Données étiquetées :** le projet utilise un jeu public d'avis Allociné étiquetés et un jeu généré pour travailler les cas positifs, négatifs et mitigés. En production, il faudrait des étiquettes représentatives des avis de l'entreprise et validées par des personnes compétentes : des données publiques ne garantissent pas l'adéquation au vocabulaire métier.

**(b) Vérifiabilité :** le modèle fournit une classe et un score ; le pipeline linéaire, le jeu de test séparé et l'analyse des erreurs sont inspectables, sans que le score explique entièrement chaque décision. **(c) Coût :** TF-IDF et régression logistique fonctionnent sur CPU, sans appel génératif payant par avis. **(d) Conséquence :** une erreur modifie la priorité, mais l'agent garde la décision finale. La supervision réduit le risque, sans annuler celui d'un avis négatif manqué. Le cahier des charges demande un F1 macro d'au moins 0,85 et un rappel négatif d'au moins 0,90.

## 2. L'architecture du dépôt

Le dépôt sépare consignes, code, interface, tests et artefacts. La racine contient le `README.md`, les énoncés, `requirements.txt`, `pytest.ini`, `Makefile`, `.gitignore` et la CI sous `.github/workflows/`. Les fiches TP1 sont dans `docs/cadrage/` ; [`src/`](../src) contient génération, entraînement, évaluation et prédiction ; [`ui/`](../ui) l'application Streamlit et ses fonctions testables ; [`tests/`](../tests) vérifie environnement, cadrage, Git, modèle et interface. `scripts/` regroupe les outils de configuration, de diagnostic et de vérification d'un clone. [`docs/semaine2.md`](./semaine2.md) et [`docs/semaine3.md`](./semaine3.md) consignent l'analyse d'erreurs et le seuil.

Le contrôle final de cette version donne **45 tests passés**, dont les trois tests d'interface ajoutés au socle des TP précédents.

Dans `data/`, [`sample_reviews.csv`](../data/sample_reviews.csv) est un petit échantillon versionné, tandis que `demo_reviews.csv` se régénère avec `python src/make_demo.py`. Dans `models/`, `.gitkeep` maintient le dossier, `metrics.json` conserve les résultats, mais `sentiment.joblib` reste local. Git suit le code, les tests, la configuration, la documentation et les métriques, mais pas les trois artefacts reconstructibles : `.venv`, `data/demo_reviews.csv` et `models/sentiment.joblib` (produit par `python src/train.py`). Le modèle est indispensable à l'inférence, mais reste un binaire régénérable, peu adapté aux diffs.

`models/metrics.json` est versionné car il est compact, lisible et consigne les résultats : la CI peut y vérifier le seuil de qualité sans charger le modèle. On versionne donc la mesure, pas le pipeline sérialisé. Un clone neuf doit reconstruire l'environnement, les données et le modèle avant une prédiction locale.

## 3. Le modèle

Le pipeline scikit-learn de TP2 réunit `TfidfVectorizer` et `LogisticRegression` dans un objet sauvegardé. Le vecteur utilise des unigrammes et bigrammes (`ngram_range=(1, 2)`), `min_df=2` et une pondération TF sublinéaire ; le classifieur utilise `class_weight="balanced"` et `max_iter=1000`. C'est une baseline compacte, pas un système de compréhension du langage.

La précaution centrale est de découper **avant** la vectorisation. Dans [`src/train.py`](../src/train.py), `train_test_split` réserve 80 % au train et 20 % au test, avec stratification et `random_state=42`. Le pipeline ajuste le vocabulaire uniquement sur le train, puis transforme le test. Vectoriser avant ce découpage ferait intervenir le test dans la représentation apprise (fuite de données) ; graine et stratification assurent reproductibilité et proportions de classes comparables.

Le jeu de démonstration est petit et pédagogique ; Allociné est un corpus public plus volumineux. Le tableau reprend les résultats consignés dans le compte rendu de TP2 et les métriques versionnées ; les valeurs démo sont celles de l'exécution locale.

| Jeu | Avis (train/test) | Vocabulaire | Accuracy | F1 macro | Rappel négatif |
| --- | ---: | ---: | ---: | ---: | ---: |
| Démonstration | 232 / 58 (290 au total) | 316 | 0,8793 | 0,8790 | 0,9310 |
| Allociné | 16 000 / 4 000 (20 000 au total) | 149 529 | 0,9205 | 0,9205 | 0,9113 |

Le jeu démo équilibré contient 145 avis par classe, dont 100 mitigés et 30 neutres rattachés à une classe. Il facilite l'analyse des retournements, mais ne représente pas toute la variété des avis réels. Le score Allociné, plus élevé, ne garantit pas la même performance sur des avis de commerce : le domaine, les étiquettes et le vocabulaire diffèrent. Un usage réel exige donc un test sur des données métier annotées.

Pour le test démo, la matrice de confusion utilise l'ordre `negative`, puis `positive`, sur les lignes et les colonnes :

```text
                    Prédit négatif   Prédit positif
Vérité négative             27                2
Vérité positive              5               24
```

**Ligne négative :** 27/29 avis négatifs sont retrouvés ; 2 sont classés positifs. Ce sont les avis négatifs manqués et ils donnent le rappel 27/29 = 0,931. **Ligne positive :** 24/29 avis positifs sont reconnus ; 5 sont signalés à tort comme négatifs et augmentent la file prioritaire. La matrice montre pourquoi l'accuracy seule ne suffit pas.

## 4. L'analyse des erreurs

Sur les 58 exemples du test démo, 7 sont mal classés ; dans cette exécution, tous sont mitigés et contiennent des polarités opposées. Exemple : *« Service impeccable et livraison en avance sur le papier, sauf que ensuite produit cassé à l'arrivée. »* L'étiquette est négative, mais le modèle prédit positive : les premiers mots positifs l'emportent lexicalement sur la conclusion « produit cassé ». La difficulté est de combiner les deux segments, non d'absence d'indices.

Le pipeline comprend des unigrammes et des bigrammes, donc conserve un ordre local. Mais TF-IDF ne représente pas toute la structure des propositions, la portée de « sauf que » ni le renversement de conclusion ; les associations lexicales peuvent ainsi peser plus que la relation entre les segments. Un modèle contextuel pourrait mieux la représenter, sans garantir une décision correcte.

Il faudrait collecter et annoter davantage d'avis mitigés, puis suivre les faux négatifs. Une segmentation autour de « mais » pourrait être comparée à la baseline sur un test indépendant ; un modèle contextuel serait une autre piste, plus coûteuse. Le TP2 visait d'abord une baseline reproductible et l'analyse de ses limites.

## 5. L'interface et le seuil d'incertitude

Le TP3 rend le pipeline accessible sans terminal. [`ui/app.py`](../ui/app.py) analyse un avis ou un CSV ; [`ui/helpers.py`](../ui/helpers.py) isole les fonctions métier pour les tester sans Streamlit. Le CSV requiert une colonne `review`. Le résultat ajoute label, score et verdict ; l'interface résume les positifs, négatifs et avis à vérifier, trie les résultats et permet l'export. Le modèle est mis en cache.

Le seuil par défaut est **0,60**. Le score est le maximum des probabilités renvoyées par le classifieur : c'est un indicateur de confiance, pas une garantie de calibration. Sous le seuil, l'interface affiche « à vérifier ». Sur le test démo de 58 avis, **16/58 (27,6 %)** sont envoyés à une vérification humaine ; **42 (72,4 %)** reçoivent un verdict automatique.

Cette proportion synthétique n'est pas une prévision du volume réel. Un seuil de 0,50 laisserait les cas limites sans garde-fou ; un seuil plus haut augmenterait la charge manuelle. À 0,60, on limite les décisions les moins assurées sans prétendre supprimer les erreurs. En production, il faudrait choisir le seuil sur des données représentatives, selon le coût des erreurs et la capacité des agents.

## 6. Ce qui a échoué

Le premier blocage documenté concernait Python sous Windows : l'interpréteur système renvoyait `No module named pytest`, alors que les dépendances étaient dans `.venv`. Il a fallu utiliser explicitement `.\.venv\Scripts\python.exe`. Une commande correcte ne suffit pas si elle cible le mauvais environnement.

Au premier contrôle TP2, le résultat était `2 failed, 38 passed, 2 skipped` : `models/metrics.json` manquait. L'entraînement n'avait pas encore été exécuté. La génération du jeu démo puis `python src/train.py` ont créé les artefacts et permis de valider les métriques. Nous avons ainsi distingué les tests exigeant un artefact local de ceux exécutables en CI sans modèle.

Un `git push` a ensuite été rejeté parce qu'un document avait été ajouté directement sur GitHub : les historiques local et distant avaient divergé. Plutôt que de forcer le push, nous avons fait `git fetch`, rebasé les commits sur `origin/main`, puis poussé à nouveau.

Pour la démonstration TP3, le modèle ignoré par Git et Streamlit manquaient dans le venv ; les premiers lancements n'ont pas ouvert l'interface. Il a fallu générer les données, entraîner le modèle et installer les dépendances nécessaires. C'est la conséquence de la stratégie voulue : le clone ne transporte pas les artefacts reconstruisibles.

## 7. Ce que nous ferions autrement

Nous constituerions d'abord un jeu de validation métier : le jeu démo teste le pipeline, mais ses phrases synthétiques ne prédisent pas les résultats sur de vrais clients. Un échantillon autorisé, anonymisé et annoté selon des règles communes permettrait de mesurer faux négatifs, faux positifs et abstentions par catégorie et langue. Les décisions resteraient humaines et les données personnelles soumises à une politique d'accès et de conservation.

Nous comparerions ensuite, sur le même test indépendant, l'ajout d'exemples mitigés, le traitement des connecteurs, la calibration et éventuellement un modèle contextuel ; chaque complexité devrait apporter un gain mesuré. DVC pourrait suivre les données et artefacts, tandis qu'une surveillance de dérive et des erreurs agents guiderait les réentraînements. Les choix de seuil et de modèle devraient rester documentés et réversibles.

## 8. Répartition du travail

| Membre | Ce qu'il a pris en charge |
| --- | --- |
| **Hiba Ayatallah** | Cadrage des cas métier, suivi du dépôt GitHub, conformité des fiches et documentation ; revue de cohérence des métriques et du besoin. |
| **Manal Wassila** | Configuration de l'environnement, pipeline et entraînement, tests, analyse des erreurs et synchronisation Git. |

Cette répartition reprend les contributions consignées dans le README et le compte rendu de TP2. Pour le TP3, l'interface, ses tests et cette version du compte rendu ont été préparés avec Copilot ; les contributions individuelles indiquées doivent correspondre au travail réellement effectué par chacune.

## Outils d'aide à la rédaction

Copilot a été utilisé pour structurer et reformuler le compte rendu et aider à l'interface ; les métriques ont été recoupées avec `models/metrics.json`, et la matrice, l'exemple d'erreur ainsi que le nombre d'avis sous le seuil ont été vérifiés en rejouant l'évaluation sur les données locales.
