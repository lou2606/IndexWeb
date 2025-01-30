import json
import string
from collections import defaultdict
import pandas as pd


class Index:

    def __init__(self, data):
        self.data = data
        self.index_title = defaultdict(set)
        self.index_description = defaultdict(set)
        self.index_review = defaultdict(set)
        self.index_features = defaultdict(lambda: defaultdict(set))
        self.index_position_title = defaultdict(set)
        self.index_position_description = defaultdict(set)

    def __str__(self):
        """
        Print each index with his content
        """
        result = []
        for attr_name in dir(self):
            if attr_name.startswith("index_"):
                attr_value = getattr(self, attr_name)
                result.append(f"{attr_name}:\n{attr_value}\n")
        return "\n".join(result)

    @staticmethod
    def load_jsonl(path):
        """
        Loads JSON line from a path
        """
        docs = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                docs.append(json.loads(line))
        return docs

    @staticmethod
    def parse_jsonl(jsonl):
        """
        Parses a JSONL (JSON Lines) formatted input and extracts URLs from each lines
        """
        urls = []
        for doc in jsonl:
            urls.append(doc["url"])
        return urls

    @staticmethod
    def extract_id(url):
        """
        Extracts the unique identifier from a given URL. This function checks
        if a query string is present in the last segment of the URL. If found,
        it removes the query string to return only the identifier.
        """
        last = url.split("/")[-1]
        if "?" in last:
            return last.split("?")[0]
        else:
            return last

    @staticmethod
    def extract_variante(url):
        """
        Extracts the variant identifier from a given URL string.
        """
        last = url.split("/")[-1]
        if "?" in last:
            return last.split("=")[1]


    def tokenize(self, text):
        """
        Simple tokenization with stopwords removal.
        """
        ww = []
        with open("stop_words_english.json", "r", encoding="utf-8") as f:
            for line in f:
                ww.append(json.loads(line))
        stopwords = []
        for word in ww:
            stopwords.append(word)

        tokens = text.lower().translate(str.maketrans("", "", string.punctuation)).split()
        return [token for token in tokens if token not in stopwords]

    def build_index(self):
        """
        Build indexes for title and description.
        """
        for doc in self.data:
            doc_id = doc["url"]
            title_tokens = self.tokenize(doc["title"])
            description_tokens = self.tokenize(doc["description"])


            for token in title_tokens:
                self.index_title[token].add(doc_id)


            for token in description_tokens:
                self.index_description[token].add(doc_id)

    def build_index_review(self):
        """
        Build index for reviews.
        """

        for doc in self.data:
            doc_id = doc["url"]
            reviews = doc["product_reviews"]
            if len(reviews) != 0:
                nb_reviews = len(reviews)
                mrating= 0
                for review in reviews:
                    mrating += int(review["rating"])
                if nb_reviews == 0:
                    mrating = 0
                else:
                    mrating = mrating / nb_reviews
                ratings =  pd.DataFrame(reviews)
                ratings = ratings.sort_values(by="date")
                last_rating = ratings.iloc[-1]
                self.index_review[doc_id].add(nb_reviews)
                self.index_review[doc_id].add(mrating)
                self.index_review[doc_id].add(last_rating["rating"])

    def build_index_features(self):
        """
        Build index for features.
        """
        for doc in self.data:
            doc_id = doc["url"]
            features = doc["product_features"]
            for key_feature, feature in features.items():
                feature_tokens = self.tokenize(feature)
                for token in feature_tokens:
                    self.index_features[key_feature][token].add(doc_id)

    def create_sub_indices(self):
        """
        Build indexes for each features according to index_features.
        """
        for key_feature, tokens_dict in self.index_features.items():
            sub_index_name = f"index_{key_feature}"
            setattr(self, sub_index_name, tokens_dict)

    def build_index_position(self):
        """
        Build index of position for title and description.
        """
        for doc in self.data:
            doc_id = doc["url"]
            title_tokens = self.tokenize(doc["title"])
            description_tokens = self.tokenize(doc["description"])

            for token in title_tokens:
                title = doc["title"]
                position =  title.find(token)
                self.index_position_title[token].add((doc_id, position))

            for token in description_tokens:
                description = doc["description"]
                position =  description.find(token)
                self.index_position_description[token].add((doc_id, position))

    def save_indexes(self):
        """
        Save all of the indexes in a json file named after the name of the index.
        """
        try:
            for attr_name in dir(self):
                if attr_name.startswith("index_"):
                    attr_value = getattr(self, attr_name)
                    if isinstance(attr_value, defaultdict):
                        attr_value = {key: list(value) for key, value in attr_value.items()}
                    elif isinstance(attr_value, dict):
                        attr_value = {key: list(value) if isinstance(value, set) else value for key, value in
                                      attr_value.items()}

                    with open(attr_name + ".json", "w", encoding="utf-8") as f:
                        json.dump(attr_value, f, indent=4)

        except Exception:
            pass
