# Choix du seuil d'incertitude (Semaine 3)

Le seuil d'incertitude de 60 % (la valeur retenue pour `SEUIL_INCERTITUDE`) permet de conserver l'automatisation pour les avis clairs tout en renvoyant les cas ambigus vers un agent humain. Un avis requiert au moins 60 % de probabilité estimée pour recevoir un verdict tranché (« positive » ou « negative ») ; en deçà, il est marqué « à vérifier ».

Sur notre jeu de démonstration particulièrement riche en retournements (`demo_reviews.csv`), ce seuil envoie 117 avis sur 290 (soit environ 40.3 %) en vérification humaine, tandis que sur un flux opérationnel plus standard (`sample_reviews.csv`), il n'isole que 7 avis sur 30 (23.3 %).

Ce compromis évite de classer trop brutalement les avis mitigés, qui sont précisément ceux où le modèle sans ordre commet le plus d'erreurs (cf. TP2). Le résultat est un équilibre idéal entre efficacité opérationnelle et fiabilité métier pour l'équipe relation client, sans bloquer toute l'automatisation sur des commentaires à risque.
