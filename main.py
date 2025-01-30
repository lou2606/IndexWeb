import json
from crawler import WebCrawler
from index import Index

def main():
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

