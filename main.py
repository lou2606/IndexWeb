import json
from crawler import WebCrawler
from index import Index
mode = "Index"
def main():
    if mode == "WebCrawler":
        base_url = "https://web-scraping.dev/products"
        max_depth = 20

        crawler = WebCrawler(base_url, max_depth)
        crawler.crawl()

        with open("results.json", "w", encoding="utf-8") as json_file:
            json.dump(crawler.results, json_file, indent=4, ensure_ascii=False)

        print("Résultats sauvegardés dans 'results.json'")

    elif mode == "Index":
        data = Index.load_jsonl("products.jsonl")
        index = Index(data)
        index.build_index()
        index.build_index_features()
        index.build_index_position()
        index.build_index_review()
        index.create_sub_indices()
        index.save_indexes()

if __name__ == "__main__":
    main()

