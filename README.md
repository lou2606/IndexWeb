
# IndexWeb

IndexWeb est un projet de scraping et d'indexation de pages web. Il explore des sites web de manière récursive, extrait des informations pertinentes (titre, description, contenu textuel, etc.) et sauvegarde les résultats dans un fichier JSON. 

---

## Fonctionnalités

- **Exploration de sites web** : Crawler capable de naviguer entre les pages à partir d'une URL initiale.
- **Respect du fichier robots.txt** : Vérification des autorisations avant de crawler une URL.
- **Extraction d'informations** : Extraction de plusieurs éléments comme le titre, la description et les avis.
- **Indexation inversée** : Système d'index pour des recherches rapides.
- **Analyse des reviews** : Calcul de la moyenne des évaluations des utilisateurs et récupération de la dernière évaluation.
- **Indexation des caractéristiques (features)** : Indexation détaillée pour les fonctionnalités produit.
- **Persistance des données** : Sauvegarde des résultats dans `results.json` et des index dans des fichiers JSON dédiés.

---

## Prérequis

Avant de commencer, assurez-vous d'avoir :

- Python 3.12.3 ou une version ultérieure
- Les modules Python suivants : 
  - `requests`
  - `beautifulsoup4`
  - `pandas`

Si ces modules ne sont pas installés, vous pouvez les ajouter via pip :

```bash
pip install requests beautifulsoup4 pandas
```

---

## Installation

1. Clonez le dépôt ou téléchargez les fichiers du projet :
   ```bash
   git clone https://github.com/lou2606/IndexWeb.git
   cd indexweb
   ```

2. Installez les dépendances nécessaires (voir Prérequis).

3. Assurez-vous que tous les modules requis sont accessibles.

---

## Utilisation
### Cas crawler

set `mode` à `WebCrawler`
1. Modifiez le fichier `main.py` pour définir l'URL de base (`base_url`) et les paramètres du crawler, tels que :
   - **Profondeur maximale** (`max_depth`)
   - **Nombre maximal de pages** (`max_pages`)

   Exemple dans `main.py` :
   ```python
   base_url = "https://web-scraping.dev/products"
   max_depth = 20
   ```

2. Lancez le script principal :
   ```bash
   python main.py
   ```

3. Les résultats seront sauvegardés dans le fichier `results.json` à la racine du répertoire.

### Cas index
set `mode` à `Index`

## Structure du projet

Voici un aperçu des principaux fichiers et de leurs rôles :

- **`main.py`** : Point d'entrée principal du programme. Définit les paramètres d'exploration et exécute le crawler. Sauvegarde les résultats au format JSON.
- **`crawler.py`** : Contient la classe `WebCrawler`, responsable de :
  - récupérer les pages web,
  - respecter les contraintes du fichier `robots.txt`,
  - extraire les contenus pertinents,
  - naviguer entre les liens.
- **`parser.py`** : Contient la classe `WebParser`. Fournit des fonctions utilitaires pour analyser une page web, récupérer son titre, sa description meta et son texte brut.
- **`index.py`** : Contient la classe Index qui permet de créer, enregistrer les index
---

## Exemple de résultat

Un exemple de structure du fichier `results.json` :

```json
[
    {
        "url": "https://web-scraping.dev/products",
        "title": "web-scraping.dev product page 1",
        "first_paragraph": "",
        "links": [
            "https://web-scraping.dev/products?page=2",
            "https://web-scraping.dev/products?page=3",
            "https://web-scraping.dev/product/1",
            "https://web-scraping.dev/product/4",
            "https://web-scraping.dev/products?page=4",
            "https://web-scraping.dev/products?category=household",
            "https://web-scraping.dev/product/2",
            "https://web-scraping.dev/products?category=consumables",
            "https://web-scraping.dev/product/5",
            "https://web-scraping.dev/product/3",
            "https://web-scraping.dev/products",
            "https://web-scraping.dev/products?page=5",
            "https://web-scraping.dev/products?category=apparel",
            "https://web-scraping.dev/products?page=1"
        ]
    }
]
```


---

## Structure des index

Pour que les données extraites soient facilement accessibles et exploitables après leur traitement, plusieurs types d'index sont construits dans ce projet :

### 1. Index par **titre** et **description**
- **Objet :** Faciliter la recherche des documents par mots-clés présents dans les titres et descriptions.
- **Structure :** 
  ```json
  {
      "mot_clé": ["url_document1", "url_document2"]
  }
  ```

- **Exemple pour l'index titre :**
  ```json
  {
      "ordinateur": ["https://site.com/produit1", "https://site.com/produit2"],
      "portable": ["https://site.com/produit1"]
  }
  ```

### 2. Index par **avis produits** (reviews)
- **Objet :** Fournir des données sur les avis produits : nombre d'avis, moyenne des notes, et la dernière note donnée.
- **Structure :**
  ```json
  {
      "url_produit": [nombre_avis, note_moyenne, dernière_note]
  }
  ```

- **Exemple :**
  ```json
  {
      "https://site.com/produit1": [20, 4.5, 5],
      "https://site.com/produit2": [5, 3.2, 4]
  }
  ```

### 3. Index par **caractéristiques techniques** (features)
- **Objet :** Organiser des données par mots-clés extraits des caractéristiques produits.
- **Structure :**
  ```json
  {
      "nom_feature": {
          "mot_clé": ["url_produit1", "url_produit2"]
      }
  }
  ```

- **Exemple :**
  ```json
  {
      "couleur": {
          "rouge": ["https://site.com/produit1"],
          "bleu": ["https://site.com/produit2"]
      },
      "taille": {
          "grande": ["https://site.com/produit2"]
      }
  }
  ```

### 4. Index des **positions des mots-clés**
- **Objet :** Indiquer les positions précises des mots-clés dans les titres et descriptions des produits.
- **Structure :**
  ```json
  {
      "mot_clé": [(url_document, position)]
  }
  ```

- **Exemple pour les titres :**
  ```json
  {
      "ordinateur": [("https://site.com/produit1", 0), ("https://site.com/produit2", 10)]
  }
  ```

---

## Choix techniques

Voici les choix techniques réalisés pour ce projet :

### 1. **Index inversé avec `defaultdict`**
Les index sont construits à l’aide de `defaultdict`, une structure utile pour associer une liste ou un ensemble dynamique à chaque clé. Cela rend le processus d’ajout de données aux index plus rapide et intuitif.

### 2. **Gestion des données JSON Lines**
Les données sont stockées dans un fichier au format JSON Lines (fichier `.jsonl`) pour permettre un traitement efficace, une simple ligne étant assimilable à une entrée.

### 3. **Tokenisation des textes**
- Utilisation de méthodes simples de tokenisation basées sur :
  1. Suppression de ponctuation
  2. Passage en minuscules
  3. Élimination des mots vides (`stopwords`)
- Cela permet de construire un index qui conserve seulement les termes pertinents.

### 4. **Flexibilité des index**
Les caractéristiques des produits (`features`) sont indexées dynamiquement dans des sous-catégories. Par exemple :
- Si un produit contient la caractéristique "Couleur", un index spécifique `index_couleur` est généré automatiquement, sans structure statique préexistante.

### 5. **Persistance des résultats et des index**
Chaque index est sauvegardé dans un fichier `.json` avec des noms explicites (comme `index_title.json`, `index_features.json`). Cela permet de mieux organiser les données indexées.

### 6. **Gestion des performances**
Les structures comme `defaultdict` et l’approche modulaire garantissent que chaque aspect (building, sauvegarde, parsing) est isolé et optimisé.

---

## Features supplémentaires implémentées

Pour toutes les features, un index est crée de façon dynamique

---

## Exemple de sauvegarde des index

Tous les index sont sauvegardés dans des fichiers JSON dédiés :

- **`index_title.json`** : Contient l'index des titres.
- **`index_description.json`** : Contient l'index des descriptions.
- **`index_review.json`** : Contient l'index des avis.
- **`index_features.json`** : Contient l'index des caractéristiques produits.
- **`index_position_title.json`** / **`index_position_description.json`** : Contiennent l'index des positions des mots-clés.
-  **`index_<name_features>.json`** : Contient l'index de la feature du produit.
Cela optimise la consultation des résultats et facilite l’intégration avec d’autres outils ou analyses.



---

## Fonctionnalités des requêtes

Dans ce projet, plusieurs méthodes sont implémentées pour exécuter des requêtes sur des index préconstruits. Ces requêtes permettent de récupérer des documents (par exemple des produits extraits) en fonction de différents critères comme le titre, la description ou la région.

### 1. **Requête sur le titre (`requete_title`)**

- **Description** : Recherche et classe les documents en fonction de la ressemblance de leur titre avec la requête utilisateur.
- **Entrée** : Une chaîne de texte représentant la requête.
- **Sortie** : Un JSON contenant les métadonnées (nombre de résultats disponibles et analysés) et une liste triée des documents pertinents (top 5).
- **Utilisation** : Idéal pour des recherches simples basées sur des mots-clés dans le titre.

---

### 2. **Requête sur la description (`requete_description`)**

- **Description** : Semblable à `requete_title`, cette méthode s'applique aux descriptions des documents au lieu des titres.
- **Entrée** : Une chaîne de texte représentant la requête.
- **Sortie** : Un JSON contenant les métadonnées (nombre de résultats disponibles et analysés) et une liste triée des documents pertinents (top 5).
- **Utilisation** : Recherchez des informations spécifiques ou du contexte dans les descriptions des documents.

---

### 3. **Requête sur le titre et la description (`requete_title_description`)**

- **Description** : Combine les résultats des recherches dans les titres et les descriptions. Les scores sont pondérés de façon à donner un poids plus important au titre.
- **Entrée** : Une chaîne de texte représentant la requête.
- **Sortie** : Un JSON contenant les métadonnées (nombre de résultats disponibles et analysés) et une liste triée des documents pertinents (top 5).
- **Différences** : Donne une vue holistique en incluant deux dimensions (titre et description) pour obtenir des résultats plus riches.

---

### 4. **Requête sur le titre et une région spécifique (`requete_title_region`)**

- **Description** : Cette recherche s'applique aux titres, tout en filtrant les résultats par une région spécifique.
- **Entrée** : 
  - Une chaîne de texte (requête utilisateur),
  - Une région (facultative) à filtrer,
  - Des mots-clés obligatoires (facultatifs) à inclure dans le titre.
- **Sortie** : Un JSON contenant les métadonnées et la liste des documents pertinents (top 5 après filtrage).
- **Utilisation** : Cette requête est utile pour des applications géographiques où l'origine ou la région des documents est importante.

---

### 5. **Requête sur la description et une région spécifique (`requete_description_region`)**

- **Description** : Recherche sur les descriptions des documents tout en filtrant les résultats par région.
- **Entrée** :
  - Une chaîne de texte (requête utilisateur),
  - Une région (facultative) à filtrer,
  - Des mots-clés obligatoires (facultatifs) à inclure dans la description.
- **Sortie** : Un JSON contenant les métadonnées et la liste des documents pertinents (top 5 après filtrage).
- **Différences** : Spécifique à la description avec filtrage par région.

---

### Différences majeures entre les requêtes

| Fonction                  | Champ de recherche    | Gestion des régions | Prise en compte des mots obligatoires | Pondération des scores | Objectif principal                                                                |
|---------------------------|-----------------------|---------------------|---------------------------------------|------------------------|-----------------------------------------------------------------------------------|
| `requete_title`           | Titre                | Non                 | Non                                   | Non                    | Rechercher des mots-clés spécifiques dans les titres des documents               |
| `requete_description`     | Description          | Non                 | Non                                   | Non                    | Extraire des informations plus contextuelles depuis les descriptions des documents|
| `requete_title_description` | Titre et Description | Non                 | Non                                   | Oui (titre > description)| Obtenir des résultats pertinents en analysant à la fois titre et description     |
| `requete_title_region`    | Titre                | Oui                 | Oui                                   | Non                    | Restreindre les résultats par région tout en intégrant des contraintes sur titre |
| `requete_description_region` | Description        | Oui                 | Oui                                   | Non                    | Restreindre par région avec une recherche approfondie sur les descriptions      |

---

## Structure des réponses

Toutes les requêtes retournent un JSON structuré de cette manière :

```json
{
  "metadata": {
    "nb_elements_apres_filtrage": 5,
    "nb_elements_total": 100
  },
  "result": [
    {
      "url": "https://site.com/produit1",
      "score": 3.5
    },
    {
      "url": "https://site.com/produit2",
      "score": 3.2
    }
  ]
}
```

- **`metadata`** :
  - `nb_elements_apres_filtrage` : Nombre de résultats retournés après le traitement.
  - `nb_elements_total` : Nombre total de documents dans l'index concerné.
- **`result`** :
  - Contient une liste des URL des produits triés par score de pertinence.

---


## Avertissement

- Respectez toujours le fichier `robots.txt` des sites web afin d'éviter tout comportement non autorisé ou abusif.
- Ce projet est uniquement destiné à l'apprentissage ou l'analyse légale de données.

---

## Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT).
