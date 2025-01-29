from bs4 import BeautifulSoup

class WebParser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')

    def get_title(self):
        """Retourne le titre de la page."""
        title_tag = self.soup.find('title')
        return title_tag.text if title_tag else "Pas de titre"

    def get_meta_description(self):
        """Retourne la méta description de la page."""
        meta_tag = self.soup.find('meta', attrs={'name': 'description'})
        return meta_tag['content'] if meta_tag else "Pas de méta description"

    def get_text_content(self):
        """Retourne le texte brut de la page."""
        return self.soup.get_text()
