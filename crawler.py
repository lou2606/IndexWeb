import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from queue import PriorityQueue
from itertools import count



class WebCrawler:
    def __init__(self, base_url, max_depth=2, max_pages=50, delay=1):
        """
        Initialise le crawler web.
        :param base_url: URL de base pour le crawling
        :param max_depth: Profondeur maximale de crawling
        :param max_pages: Nombre maximal de pages à visiter
        :param delay: Temps (en secondes) entre chaque requête pour respecter les serveurs (politesse)
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.visited = set()
        self.results = []
        self.pages_visited_count = 0  # Compteur du nombre total de pages visitées
        self.counter = count()

        # Initialisation du parser pour robots.txt
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(urljoin(self.base_url, "/robots.txt"))
        self.robot_parser.read()

        # File de priorité pour stocker les URL à visiter
        self.queue = PriorityQueue()
        self.queue.put((0, next(self.counter),base_url, 0))

    def fetch_url(self, url):
        """Récupère le contenu HTML d'une URL donnée."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de l'URL {url}: {e}")
            return None

    def check_robots_permission(self, url):
        """Vérifie si le crawling est autorisé pour une URL donnée selon robots.txt."""
        if not self.robot_parser.can_fetch("*", url):
            print(f"Le crawling de l'URL {url} est interdit par robots.txt.")
            return False
        return True

    def extract_links(self, html, current_url):
        """Extrait tous les liens d'une page HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for anchor in soup.find_all('a', href=True):
            link = urljoin(current_url, anchor['href'])
            if link.startswith(self.base_url) or "product" in link:  # Filtre les liens hors domaine
                links.add(link)
        return links

    def crawl(self):
        """Explore récursivement les pages web à l'aide de la file de priorité."""
        while not self.queue.empty():
            if self._has_reached_max_pages():
                break

            _, _,url, depth = self.queue.get()

            if not self._should_crawl_url(url, depth):
                continue

            self._update_state_for_url(url)

            html = self._fetch_and_process_url(url)
            if html is None:
                continue

            self._process_links(html, url, depth)

            time.sleep(self.delay)  # Pause entre les requêtes HTTP (politesse)

    def _has_reached_max_pages(self):
        """Vérifie si le nombre maximal de pages a été atteint."""
        if self.pages_visited_count >= self.max_pages:
            print("Nombre maximal de pages atteint. Arrêt du crawling.")
            return True
        return False

    def _should_crawl_url(self, url, depth):
        """Vérifie si l'URL doit être crawlé."""
        if url in self.visited or depth > self.max_depth:
            return False
        if not self.check_robots_permission(url):
            return False
        return True

    def _update_state_for_url(self, url):
        """Mise à jour de l'état après le crawling d'une URL."""
        print(f"Crawling: {url}")
        self.visited.add(url)
        self.pages_visited_count += 1

    def _fetch_and_process_url(self, url):
        """Récupère le contenu HTML de l'URL et traite la page."""
        html = self.fetch_url(url)
        if html is not None:
            self.process_page(html, url)
        return html

    def _process_links(self, html, url, depth):
        """Analyse et ajoute les liens à la file de priorité."""
        links = self.extract_links(html, url)
        for link in links:
            if link not in self.visited:
                priority = -1 if "product" in link else 1
                self.queue.put((priority, next(self.counter), link, depth + 1))

    def process_page(self, html, url):
        """Analyse une page et sauvegarde les résultats."""
        soup = BeautifulSoup(html, 'html.parser')

        # Récupère le titre
        title = soup.find('title').text if soup.find('title') else "Pas de titre"

        # Récupère le premier paragraphe
        first_paragraph = ""
        first_p = soup.find('p')
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
