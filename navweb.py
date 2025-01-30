import json
import os
import string
import nltk
from charset_normalizer.cli import query_yes_no
from nltk.corpus import stopwords
import math
import pandas as pd


nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

class NavWeb:

    def __init__(self):
        self.load_jsons()

    def __str__(self):
        """
        Print each index with his content
        """
        result = []
        for attr_name in dir(self):
            if attr_name.startswith("index_"):
                attr_value = getattr(self, attr_name)
                result.append(f"{attr_name}:\n\n")
        result.append(str(len(result)))
        return "\n".join(result)

    @staticmethod
    def load_json(path):
        """
        Loads JSON line from a path
        """
        docs = []
        with open("stop_words_english.json", "r", encoding="utf-8") as f:
            for line in f:
                docs.append(json.loads(line))
        return docs


    def load_jsons(self):
        for el in os.listdir():
            if el.endswith("_index.json"):
                doc = json.load(open(el))
                sub_index_name = f"index_{el[:-11]}"
                setattr(self, sub_index_name, doc)

    def synonymes(self):
        syn = NavWeb.load_json("original_synonymes.json")
        return syn


    def tokenize(self, text):
        """
        Simple tokenization with stopwords removal.
        """

        stopwords = STOPWORDS
        tokens = text.lower().translate(str.maketrans("", "", string.punctuation)).split()
        return [token for token in tokens if token not in stopwords]


class Requete:

    def __init__(self, requete):
        self.requete = requete

    def tokenise_requete(self):
        """
                Simple tokenization with stopwords removal.
                """
        stopwords = STOPWORDS
        tokens = self.requete.lower().translate(str.maketrans("", "", string.punctuation)).split()
        return [token for token in tokens if token not in stopwords]

    def requete_synonymes(self):
        """
        Étendre les termes de la requête avec leurs synonymes.
        """
        syn_map = NavWeb.load_json("original_synonymes.json")

        tokens = self.tokenise_requete()

        extended_query = []
        for token in tokens:
            extended_query.append(token)
            if token in syn_map:
                extended_query.extend(syn_map[token])

        return extended_query


    def all_token_no_st_w(self, doc_id, token_req, index):
        for token in token_req:
            if doc_id not in index[token]:
                return False
        return True

    def at_least_one_token(self, doc_id, token_req, index):
        for token in token_req:
            if doc_id not in index[token]:
                return True
        return False


class Ranking:

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.navweb = NavWeb()
        self.index_title = self.navweb.index_title
        self.index_description = self.navweb.index_description
        self.avg_doc_length = 0
        self.docs = Ranking.load_json("rearranged_products.jsonl")
        self.doc_lengths = {doc["url"] :len(doc) for doc in self.docs}

    @staticmethod
    def load_json(path):
        """
        Loads JSON line from a path
        """
        docs = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                docs.append(json.loads(line))
        return docs

    def index_to_work(self, md):
        if md == "title":
            self.index = self.index_title
        else:
            self.index = self.index_description

    def set_index_and_docs(self, index, doc_lengths):
        """
        Configure l'index inversé et les longueurs des documents.
        """
        self.doc_lengths = doc_lengths
        self.avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths)
        print(self.avg_doc_length)

    def bm25(self, query, doc_id):
        """
        Calcule le score BM25 pour un document donné par rapport à une requête.
        """
        score = 0
        for term in query:
            if term in self.index:
                f = sum(len(n) for n in self.index[term])# Fréquence du terme
                N = len(self.doc_lengths)  # Nombre total de documents
                df = len(self.index[term])  # Nombre de docs contenant le terme
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
                numerator = f * (self.k1 + 1)
                denominator = f + self.k1 * (1 - self.b + self.b * (self.doc_lengths[doc_id] / self.avg_doc_length))
                score += idf * numerator / denominator
        return score


    def exact_match(self, query, doc_id, index):
        """
        Vérifie si tous les termes de la requête sont présents dans le document.
        """
        query = Requete(query)
        query_tokens = query.requete_synonymes()
        return query.all_token_no_st_w(doc_id, query_tokens, index)


    def linear_score(self, query, doc, title_score, review_score, frequency_score):
        """
        Combine différents signaux de pertinence en un score linéaire.
        """
        alpha = 0.4  # Poids pour les termes dans le titre
        beta = 0.3  # Poids pour les avis
        gamma = 0.3  # Poids pour la fréquence des termes

        return alpha * title_score + beta * review_score + gamma * frequency_score

    def position_score(self, query, doc_id, index):
        """
        Calcule un score de position basé sur la proximité au début du document.
        """
        position_score = 0
        for term in query:
            if term in index and doc_id in index[term]:
                position_score += 1 / (
                            index[term][doc_id][0] + 1)  # Plus c'est proche du début, meilleur est le score
        return position_score

    def freq_score(self, query, doc_id, index):
        position_score = 0
        freq = 0
        for term in query:
            if term in index and doc_id in index[term]:
                freq += len(index[term][doc_id])
        return freq

    def requete_title(self, requete):
        """
        Génère un classement des documents en fonction d'une requête donnée.
        """
        self.index_to_work("title")
        query = Requete(requete)
        query_tokens = query.requete_synonymes()

        position_score = {}
        self.set_index_and_docs(index=self.index_title, doc_lengths=self.doc_lengths)
        for doc in self.docs:
            title_score = self.position_score(query_tokens, doc["url"], self.index_title)
            review_score = self.navweb.index_reviews[doc["url"]]["mean_mark"]
            frequency_score = self.freq_score(query_tokens, doc["url"], self.index_title)
            score = self.linear_score(query_tokens, doc, title_score, review_score, frequency_score)
            position_score[doc["url"]] = score

        position_score_df = pd.DataFrame(list(position_score.items()), columns=["url", "score"])
        position_score_df = position_score_df.sort_values(by="score", ascending=False)

        filtered_results = position_score_df
        total_elements = len(self.docs)


        response_json = {
            "metadata": {
                "nb_elements_apres_filtrage": len(filtered_results),
                "nb_elements_total": total_elements
            },
            "result": filtered_results.to_dict(orient="records")
        }


        with open("response.json", "w") as outfile:
            json.dump(response_json, outfile)

    def requete_description(self, requete):
        """
        Génère un classement des documents en fonction d'une requête donnée.
        """
        self.index_to_work("description")
        query = Requete(requete)
        query_tokens = query.requete_synonymes()

        position_score = {}
        self.set_index_and_docs(index=self.index_description, doc_lengths=self.doc_lengths)
        for doc in self.docs:
            description_score = self.position_score(query_tokens, doc["url"], self.index_description)
            review_score = self.navweb.index_reviews[doc["url"]]["mean_mark"]
            frequency_score = self.freq_score(query_tokens, doc["url"], self.index_description)
            score = self.linear_score(query_tokens, doc, description_score, review_score, frequency_score)
            position_score[doc["url"]] = score

        position_score_df = pd.DataFrame(list(position_score.items()), columns=["url", "score"])
        position_score_df = position_score_df.sort_values(by="score", ascending=False)

        filtered_results = position_score_df
        total_elements = len(self.docs)

        response_json = {
            "metadata": {
                "nb_elements_apres_filtrage": len(filtered_results),
                "nb_elements_total": total_elements
            },
            "result": filtered_results.to_dict(orient="records")
        }

        with open("response.json", "w") as outfile:
            json.dump(response_json, outfile)


    def requete_title_description(self, requete):
        self.index_to_work("title")
        query = Requete(requete)
        query_tokens = query.requete_synonymes()

        position_score = {}
        self.set_index_and_docs(index=self.index_title, doc_lengths=self.doc_lengths)
        for doc in self.docs:
            title_score = self.position_score(query_tokens, doc["url"], self.index_title)
            review_score = self.navweb.index_reviews[doc["url"]]["mean_mark"]
            frequency_score = self.freq_score(query_tokens, doc["url"], self.index_title)
            score_title = self.linear_score(query_tokens, doc, title_score, review_score, frequency_score)
            print(score_title)

            self.index_to_work("description")
            description_score = self.position_score(query_tokens, doc["url"], self.index_description)
            review_score = self.navweb.index_reviews[doc["url"]]["mean_mark"]
            frequency_score = self.freq_score(query_tokens, doc["url"], self.index_description)
            description_score = self.linear_score(query_tokens, doc, description_score, review_score, frequency_score)


            score = 2 * score_title + 0.5 * description_score
            position_score[doc["url"]] = score

        position_score_df = pd.DataFrame(list(position_score.items()), columns=["url", "score"])
        position_score_df = position_score_df.sort_values(by="score", ascending=False)

        filtered_results = position_score_df
        total_elements = len(self.docs)

        response_json = {
            "metadata": {
                "nb_elements_apres_filtrage": len(filtered_results),
                "nb_elements_total": total_elements
            },
            "result": filtered_results.to_dict(orient="records")
        }

        with open("response.json", "w") as outfile:
            json.dump(response_json, outfile)

    def filter_by_region(self, docs, region, origin_index):
        """
        Filtre les documents selon la région spécifiée.
        """
        if region not in origin_index:
            raise ValueError(f"La région '{region}' est introuvable dans l'index d'origine.")

        region_docs = set(origin_index[region])
        return [doc for doc in docs if doc["url"] in region_docs]

    def filter_by_must_have_terms(self, docs, terms, index):
        """
        Filtre les documents pour inclure seulement ceux contenant tous les termes spécifiés
        dans le titre ou la description.
        """
        filtered_docs = []
        terms = Requete(terms)
        terms = terms.requete_synonymes()
        for doc in docs:
            doc_id = doc["url"]
            if Requete.all_token_no_st_w(self, doc_id, terms, index):
                filtered_docs.append(doc)
        return filtered_docs

    def requete_title_region(self, requete, region=None, must_have_terms=None):
        """
        Génère un classement des documents pour une requête donnée dans une région spécifique
        et avec des mots obligatoires dans le titre.
        """
        self.index_to_work("title")
        query = Requete(requete)
        query_tokens = query.requete_synonymes()
        total_elements = len(self.docs)
        if region:
            origin_index = self.navweb.index_origin
            self.docs = self.filter_by_region(self.docs, region, origin_index)

        if must_have_terms:
            self.docs = self.filter_by_must_have_terms(self.docs, must_have_terms, self.index_title)

        position_score = {}
        self.set_index_and_docs(index=self.index_title, doc_lengths=self.doc_lengths)

        for doc in self.docs:
            title_score = self.position_score(query_tokens, doc["url"], self.index_title)
            review_score = self.navweb.index_reviews[doc["url"]]["mean_mark"]
            frequency_score = self.freq_score(query_tokens, doc["url"], self.index_title)
            score = self.linear_score(query_tokens, doc, title_score, review_score, frequency_score)
            position_score[doc["url"]] = score

        position_score_df = pd.DataFrame(list(position_score.items()), columns=["url", "score"])
        position_score_df = position_score_df.sort_values(by="score", ascending=False)

        filtered_results = position_score_df


        response_json = {
            "metadata": {
                "nb_elements_apres_filtrage": len(filtered_results),
                "nb_elements_total": total_elements
            },
            "result": filtered_results.to_dict(orient="records")
        }

        with open("response.json", "w") as outfile:
            json.dump(response_json, outfile)

    def requete_description_region(self, requete, region=None, must_have_terms=None):
        """
        Génère un classement des documents pour une requête donnée dans une région spécifique
        et avec des mots obligatoires dans la description.
        """
        self.index_to_work("description")
        query = Requete(requete)
        query_tokens = query.requete_synonymes()
        total_elements = len(self.docs)
        if region:

            origin_index = self.navweb.index_origin
            self.docs = self.filter_by_region(self.docs, region, origin_index)

        if must_have_terms:
            self.docs = self.filter_by_must_have_terms(self.docs, must_have_terms, self.index_description)

        position_score = {}
        self.set_index_and_docs(index=self.index_description, doc_lengths=self.doc_lengths)

        for doc in self.docs:
            description_score = self.position_score(query_tokens, doc["url"], self.index_description)
            review_score = self.navweb.index_reviews[doc["url"]]["mean_mark"]
            frequency_score = self.freq_score(query_tokens, doc["url"], self.index_description)
            score = self.linear_score(query_tokens, doc, description_score, review_score, frequency_score)
            position_score[doc["url"]] = score

        position_score_df = pd.DataFrame(list(position_score.items()), columns=["url", "score"])
        position_score_df = position_score_df.sort_values(by="score", ascending=False)

        filtered_results = position_score_df


        response_json = {
            "metadata": {
                "nb_elements_apres_filtrage": len(filtered_results),
                "nb_elements_total": total_elements
            },
            "result": filtered_results.to_dict(orient="records")
        }

        with open("response.json", "w") as outfile:
            json.dump(response_json, outfile)
