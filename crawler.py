import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class WebCrawler:
    def __init__(self, base_url, max_depth=2):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
        self.results = []

    def fetch_url(self, url):
        """Récupère le contenu HTML d'une URL donnée."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de l'URL {url}: {e}")
            return None

    def extract_links(self, html, current_url):
        """Extrait tous les liens d'une page HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for anchor in soup.find_all('a', href=True):
            link = urljoin(current_url, anchor['href'])
            if link.startswith(self.base_url):  # Filtre les liens hors domaine
                links.add(link)
        return links

    def crawl(self, url, depth=0):
        """Explore récursivement les pages web."""
        if url in self.visited or depth > self.max_depth:
            return

        print(f"Crawling: {url} (profondeur: {depth})")
        self.visited.add(url)

        html = self.fetch_url(url)
        if html is None:
            return

        # Analyse et sauvegarde les données de la page
        self.process_page(html, url)

        # Récupère les liens et continue le crawling
        links = self.extract_links(html, url)
        for link in links:
            self.crawl(link, depth + 1)

    def process_page(self, html, url):
        """Analyse une page et sauvegarde les résultats."""
        soup = BeautifulSoup(html, 'html.parser')

        # Récupère le titre
        title = soup.find('title').text if soup.find('title') else "Pas de titre"

        # Récupère le premier paragraphe
        first_paragraph = ""
        first_p = soup.find('p') or soup.find('div') or soup.find('span')
        if first_p:
            first_paragraph = first_p.text.strip()

        # Récupère les liens pertinents
        links = list(self.extract_links(html, url))

        # Sauvegarde les résultats
        self.results.append({
            "url": url,
            "title": title,
            "first_paragraph": first_paragraph,
            "links": links,
        })

