# Compte rendu global des TP1, TP2 et TP3

**Binôme :** Hiba Ayatallah et Manal Wassila  
**GitHub :** [@HibaAyatallah](https://github.com/HibaAyatallah) et [@manalwassila](https://github.com/manalwassila)  
**Module :** Développement et déploiement d'applications intelligentes

## 1. Le besoin et son cadrage

Le besoin métier du projet est clair : détecter rapidement les avis clients négatifs afin de prioriser l'intervention du service client. Ce cas correspond au cas 3 du cadrage, où la priorité n'est pas d'obtenir un discours parfait, mais d'identifier les signalements à risque avec une bonne couverture de la classe négative. Dans ce contexte, un faux négatif est particulièrement coûteux : un avis réel négatif non détecté peut retarder la réponse à un client mécontent, aggravant l'expérience client et le risque de réclamation. À l'inverse, un faux positif impose un traitement inutile à un agent, mais cela reste moins dommageable qu'une omission. C'est pourquoi le critère le plus important dans notre approche est le rappel sur la classe négative, puis le F1 macro sur l'ensemble des classes.

Le filtrage a été validé par les critères du cadrage : les données sont étiquetées, le système reste vérifiable, le coût de calcul est faible et les erreurs restent corrigibles par un agent humain. L'approche par machine learning est donc mieux adaptée que des règles manuelles ou un modèle génératif unique : les avis clients sont structuraux, nombreux et répétitifs, et un classifieur linéaire sur sac de mots est suffisant pour distinguer les signaux de polarité les plus fréquents. En pratique, nous ne cherchons pas à comprendre chaque nuance avec une intelligence artificielle coûteuse ; nous visons un mécanisme stable, reproduisible et assez performant pour donner une vraie aide opérationnelle.

Le cadrage impose un objectif de F1 macro au moins égal à 0,85 et un rappel sur la classe négative au moins de 0,90. Cela correspond bien à une politique de service client : l'outil ne remplace pas l'agent, il le seconde. Le rôle du modèle est d'orienter le tri et d'économiser le temps du staff, sans jamais trancher seul sur des cas sensibles ou ambiguës.

## 2. L'architecture du dépôt

Le dépôt est structuré comme un mini projet MLOps pédagogique : chaque dossier a une fonction claire et la séparation entre code, données, modèles et documentation est explicite. La racine contient les fichiers de cadrage, les consignes de travaux, les tests et la configuration du projet. Il y a aussi un dossier [src](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/src) qui rassemble les scripts techniques du pipeline : génération des données, entraînement, évaluation et prédiction. C'est le cœur du projet, car c'est là que la logique de modélisation est réellement implémentée.

La donnée brute de démonstration est générée dans [src/make_demo.py](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/src/make_demo.py) puis enregistrée dans [data/demo_reviews.csv](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/data/demo_reviews.csv). Cette donnée est régénérable et, comme le précise le bon usage du projet, elle n'est pas versionnée dans Git. Le même principe s'applique au modèle sérialisé [models/sentiment.joblib](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/models/sentiment.joblib) : il est essentiel pour l'inférence, mais trop volumineux et reproductible pour être stocké dans le dépôt.

À l'inverse, [models/metrics.json](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/models/metrics.json) est versionné. C'est la mesure de performance du modèle, stable, compacte et utile pour l'évaluation en CI. En d'autres termes, le dépôt conserve ce qui donne un signal de qualité, sans conserver des artefacts lourds que l'on peut reconstruire à partir du code et de la donnée. Cette distinction est centralement importante dans un projet MLOps : le code et les métriques sont versionnés, tandis que les modèles et les jeux de données trop lourds sont produits à la demande.

Les tests sont organisés dans [tests](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/tests), avec des contrôles d'environnement, de cadrage, de qualité Git et de modélisation. L'interface du TP3 est séparée dans [ui](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/ui), ce qui permet de tester le comportement métier sans lancer Streamlit. La documentation est quant à elle répartie entre [docs](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/docs), [Resume](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/Resume) et les fichiers d'énoncé. Cette structure évite que le projet ne se transforme en script monolithique : chaque niveau a une responsabilité claire.

## 3. Le modèle

Le modèle de référence du projet est un pipeline scikit-learn composé d'un vectoriseur TF-IDF et d'une régression logistique. Le point clé de la méthode est l'ordre des opérations : on découpe les données en ensemble d'entraînement et de test avant toute transformation, puis on applique la vectorisation sur les seules données d'entraînement. Cette étape est indispensable, car si l'on vectorise l'ensemble complet avant le split, le jeu de test fuite dans la phase d'apprentissage, ce qui gonfle artificiellement les performances. Dans [src/train.py](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/src/train.py), le découpage est réalisé avec `train_test_split(..., random_state=42, stratify=df["label"])` pour garantir une répartition équilibrée et reproductible.

Le vectoriseur est configuré avec un n-gramme de `(1, 2)` et un `min_df=2`, ce qui limite le vocabulaire aux termes suffisamment fréquents. La régression logistique est ensuite entraînée avec `class_weight="balanced"` pour ne pas dégrader la performance sur la classe négative, qui est la plus importante pour le besoin métier. Ce choix est cohérent avec les objectifs du cas 3 : éviter que le classifieur les plus fréquents l'emportent sur les cas de signalements critiques.

Le jeu de démonstration généré par [src/make_demo.py](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/src/make_demo.py) contient 290 avis, dont 100 avis mitigés et 30 neutres introduits volontairement. Cette composition n'est pas anodine : elle force le modèle à gérer des phrases ambiguës, où des éléments positifs et négatifs coexistent avant la conclusion du message. C'est précisément ce type de phrase qui est le plus délicat pour un modèle basé sur un sac de mots, car l'ordre d'apparition et la structure syntaxique peuvent être plus importants que la simple présence de mots-clés. Le modèle est donc confronté à un cas réaliste : l'orientation globale du commentaire compte plus que la présence d'un adjectif isolé.

Les métriques produites sur notre jeu de démonstration sont les suivantes, et elles correspondent à notre [models/metrics.json](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/models/metrics.json) :

- F1 macro : 0,879
- Accuracy : 0,8793
- Recall sur la classe négative : 0,931
- Nombre d'avis d'entraînement : 232
- Nombre d'avis de test : 58

Ces scores dépassent bien le seuil fixé à 0,85 pour le F1 macro et sont confortables pour la exigence de service client. Le rappel négatif de 0,931 est particulièrement satisfaisant : il montre que le modèle repère la majorité des avis négatifs et réduit le risque d'omission. L'évaluation est également lisible avec la matrice de confusion, ce qui permet de comprendre où les erreurs sont concentrées. On voit notamment que les erreurs surviennent surtout sur les avis mitigés ou les phrases dans lesquelles la conclusion est inversée par une structure de type "mais..." ou "sauf que...".

## 4. L'analyse des erreurs

Les erreurs du modèle sont très instructives. En pratique, elles ne sont pas dues à un mauvais apprentissage en général, mais à une limite structurelle du sac de mots. Un modèle TF-IDF ne conserve pas l'ordre précis des mots ni leur rôle syntaxique. Il sait que des termes comme "bon", "mauvais", "cassé", "service", "livraison" existent, mais il ne comprend pas toujours la logique de la phrase. Un avis mitigé tel que "livraison rapide mais produit cassé" peut être bien classé par un modèle avancé, tandis qu'un système purement lexical risque d'ignorer la partie qui finit par trancher la décision.

Cette limite est visible sur les avis qui contiennent des oppositions explicites. Le modèle a tendance à se concentrer sur des éléments saillants, sans reconstruire le sens complet de la phrase. Par exemple, un commentaire qui dit "excellent au départ, mais finalement décevant" peut encore recevoir une bonne prédiction si le vocabulaire est bien équilibré, mais les phrases où la conclusion est moralement inversée par des connecteurs et des retournements d'opinion restent difficiles. C'est exactement pour cette raison que le TP2 a insisté sur la génération de 100 avis mitigés dans les données de démonstration.

Il faut souligner que les erreurs sont utiles : elles montrent que la simple présence d'un mot positif ou négatif n'est pas suffisante. Elles confirment l'intérêt d'un seuil d'incertitude dans l'interface du TP3. Une phrase ambiguë ne doit pas être classée trop fermement par l'outil si sa confiance est trop faible. Le modèle n'est pas censé “tout comprendre”, il doit surtout trier le flux de manière utile et sûre.

## 5. L'interface et le seuil d'incertitude

Le TP3 a introduit une nouvelle exigence de conception : rendre le modèle exploitable par des utilisateurs non techniques. L'interface Streamlit a donc été pensée pour présenter les résultats de manière lisible sans exposer l'implémentation interne. Son principe est simple : si le modèle est sûr, il affiche un verdict tranché ; si sa confiance est insuffisante, il affiche un statut "à vérifier". Cette logique est exactement la bonne réponse à un modèle probabiliste : le score n'est pas seulement une étiquette, c'est aussi un indicateur de sécurité décisionnelle.

Le seuil retenu a été fixé à 0,60. Cela signifie qu'un avis est automatiquement classé uniquement si le score de confiance du modèle dépasse 60 %. En dessous de cette valeur, il est envoyé vers un agent humain pour vérification. Ce choix n'est pas arbitraire : il représente un compromis entre automatisation et fiabilité. Un seuil trop bas (par exemple 0,50) produit une surconfiance et fait traiter par le système des avis ambigus, ce qui augmente le risque d'erreur. Un seuil trop haut (0,75 ou 0,80) rend l'automatisation presque inexistante et nuit au gain de productivité.

En pratique, un seuil de 60 % garde l'automatisation pour les cas clairs et laisse le soin à l'humain aux cas limites. Cette logique est cohérente avec la réalité d'un service client : il est souvent préférable de remettre un avis ambigu vers un agent plutôt que de risquer une mauvaise réponse automatique. C'est aussi un bon exemple de conception responsable de l'IA, où la machine n'est pas utilisée pour “choisir sans marge de sécurité” mais pour orienter le travail humain.

## 6. Ce qui a échoué

Le projet a connu plusieurs blocages concrets, et il faut en parler honnêtement car ils font partie de l'apprentissage. Le premier a été la configuration de l'environnement Python. Nous avons dû nous assurer que les commandes étaient lancées dans le bon interpréteur du projet, notamment avec l'environnement virtuel .venv. Sans cela, pytest ou les dépendances n'étaient pas retrouvés, ce qui provoquait des erreurs difficiles à interpréter.

Le second blocage a été la production du modèle lui-même. Avant l'entraînement, plusieurs tests échouaient parce que [models/sentiment.joblib](C:/Users/hibaa/OneDrive/Desktop/Dev-IA/sentiment-app/models/sentiment.joblib) n'existait pas encore. Cela a confirmé l’importance de l'ordre des étapes : générer les données, entraîner le modèle, puis valider les tests. Ce n'est pas un bug de code, mais un oubli de workflow de développement machine learning.

Le troisième obstacle, davantage organisationnel, a été le besoin de relier la progression du TP à un dépôt Git propre et lisible. Il fallait vérifier les fichiers versionnés, maintenir des commits cohérents et éviter de “forcer” la synchronisation sans comprendre la logique de Git. À un moment, il a fallu réajuster l'historique et vérifier les éléments ajoutés par le binôme avant de finaliser le dépôt.

Chacun de ces échecs a été résolu par une démarche méthodique : compréhension du problème, validation des prérequis, puis exécution ciblée des commandes de génération, d'entraînement et de tests. Ce sont précisément ces étapes qui nous ont fait comprendre que le projet n'est pas seulement un ensemble de scripts Python, mais une chaîne de production de données et modèles.

## 7. Ce que nous ferions autrement

Avec le recul du projet, plusieurs améliorations seraient pertinentes dans un cadre réel d'équipe produit. Premièrement, l'usage de DVC pour la traçabilité des données et des modèles serait naturellement justifié. Cela permettrait de versionner correctement des artefacts volumineux tout en gardant le dépôt Git léger. Deuxièmement, un prétraitement plus avancé des avis mitigés serait utile : détecter les tournures de phrase comme “mais”, “cependant”, “sauf que”, “finalement” et leur attribuer un sens plus explicite, sans dépendre uniquement du simple vocabulaire.

Une autre piste forte serait l'ajout d'un mécanisme de veille sur la dérive des données. Le vocabulaire des avis clients évolue dans le temps, et le modèle risque de perdre en qualité si les nouveaux cas de signalements ne sont plus représentés. Une surveillance régulière des erreurs de prédiction, associée à un réentraînement ou à une validation métier périodique, serait un vrai atout pour l'équipe. Enfin, dans un environnement de production, le seuil d'incertitude pourrait être calibré à partir de données réelles de validation ou de retours agents, afin d'optimiser le compromis entre productivité et taux de vérification.

## 8. Répartition du travail

- **Hiba Ayatallah** : cadrage métier, structuration du dépôt, documentation, suivi des consignes du TP et validation des fichiers de projet. Elle a également participé au contrôle de cohérence entre les écrits et les choix techniques du projet.
- **Manal Wassila** : mise en place de l'environnement, entraînement du modèle, vérification des métriques, exécution des tests et analyse du comportement du classifieur. Elle a aussi contribué à la validation des scripts de données et de prédiction.

La contribution a été complémentaire, et les tâches ont été réparties selon les compétences de chacun, sans masquer les difficultés rencontrées. Le projet a été mené dans un esprit de travail collaboratif, avec des vérifications croisées sur les fichiers, les résultats et la documentation.

---

Nous avons utilisé l'assistant d'IA de Copilot pour reformuler certaines sections, vérifier la cohérence du texte et aider à la finalisation du compte rendu. Nous avons ensuite relu et validé les éléments techniques et les chiffres nous-mêmes, en nous assurant qu'ils sont conformes aux résultats du projet.
