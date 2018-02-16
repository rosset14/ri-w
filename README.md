# ri-w

Contenu : 
  - dossier cacm : codes source permettant d'indexer la collection (BSBI + map/reduce), de faire des requêtes booléennes et vectorielles et d'évaluer les algos
  - dossier Stanford : codes source permettant d'indexer la collection (BSBI + map/reduce) et de faire des requêtes booléennes et vectorielles
  - fichier rapport.pdf : notre rapport
  - autres fichiers : fichiers générés, ne pas les modifier ni les déplacer

Important : avant de faire des requêtes sur la collection Stanford, il FAUT exécuter le module parse_stanford.py afin d'indexer la collection (l'index est trop lourd pour passer sur github donc nous vous laissons le soin de le faire). Des fichiers seront alors générés, ne pas les modifier ni les déplacer

Pour faire des requêtes et/ou évaluations sur la collection CACM, utiliser les fichiers cacm/boolean_request_cacm.py et/ou cacm/vectorial_request_cacm.py
Pour faire des requêtes sur la collection CACM, utiliser les fichiers stanford/boolean_request_cacm.py et/ou stanford/vectorial_request_cacm.py
