import json
from crawler import WebCrawler

def main():
    base_url = "https://web-scraping.dev/products"
    max_depth = 20


    crawler = WebCrawler(base_url, max_depth)
    crawler.crawl()


    with open("results.json", "w", encoding="utf-8") as json_file:
        json.dump(crawler.results, json_file, indent=4, ensure_ascii=False)

    print("Résultats sauvegardés dans 'results.json'")

if __name__ == "__main__":
    main()

