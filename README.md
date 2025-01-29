# IndexWeb

IndexWeb est un projet de scraping et d'indexation de pages web. Il explore des sites web de manière récursive, extrait des informations pertinentes (titre, description, contenu textuel, etc.) et sauvegarde les résultats dans un fichier JSON. 

## Fonctionnalités

- **Exploration de sites web** : Crawler capable de naviguer sur des pages à partir d'une URL de base.
- **Respect du fichier robots.txt** : Vérification des permissions avant de scraper une URL.
- **Extraction de données** : Informations comme le titre, la description, les liens et le premier paragraphe sont extraites.
- **Persistance des données** : Les résultats sont sauvegardés dans le fichier `results.json`.

---

## Prérequis

Avant de commencer, assurez-vous d'avoir :

- Python 3.12.3 ou une version ultérieure
- Les modules Python suivants : 
  - `requests`
  - `beautifulsoup4`

Si ces modules ne sont pas installés, vous pouvez les ajouter via pip :

```bash
pip install requests beautifulsoup4
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

---

## Structure du projet

Voici un aperçu des principaux fichiers et de leurs rôles :

- **`main.py`** : Point d'entrée principal du programme. Définit les paramètres d'exploration et exécute le crawler. Sauvegarde les résultats au format JSON.
- **`crawler.py`** : Contient la classe `WebCrawler`, responsable de :
  - récupérer les pages web,
  - respecter les contraintes du fichier `robots.txt`,
  - extraire les contenus pertinents,
  - naviguer entre les liens.
- **`parser.py`** : Contient la classe `WebParser`. Fournit des fonctions utilitaires pour analyser une page web, récupérer son titre, sa description meta et son texte brut.

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


## Avertissement

- Respectez toujours le fichier `robots.txt` des sites web afin d'éviter tout comportement non autorisé ou abusif.
- Ce projet est uniquement destiné à l'apprentissage ou l'analyse légale de données.

---

## Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT).