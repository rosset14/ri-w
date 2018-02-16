import re
import math
import numpy as np
import json
import time
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization

STANFORD_NUMBER_OF_DOCS = 98997


def parse_query(query):
    """
    Retourne la liste de termID correspondants aux termes de la requête
    :param query: la requête de l'utilisateur
    :return: la liste des termIDs
    """
    parsed_query = []
    content = re.split("\W+", query)
    for token in content:
        tok_lower = token.lower()
        if tok_lower not in common:
            try:
                parsed_query.append(term_termID[lem.lemmatize(tok_lower)])
            except ValueError:
                continue
    return parsed_query


def getCommonWords():
    """
    recupere la liste des mots communs afin de les retirer de l'index
    :return: la liste des mots commune
    """
    commonFile = open("../common_words")
    return [s[:-1] for s in commonFile.readlines()]


def vectorial_search_cacm(query, number_of_documents):
    """
    Retourne les meilleurs docIDs correspondant à la requête avec une recherche vectorielle
    :param query: la requête utilisateur
    :param number_of_documents: le nombre de documents retournés
    :return: la liste des docIDs
    """
    parsed_query = parse_query(query)
    w = {-1: {}}
    s = (STANFORD_NUMBER_OF_DOCS + 1) * [0]
    for termID in parsed_query:
        nb = parsed_query.count(termID)
        w[-1][termID] = (1 + math.log10(nb)) * math.log10(STANFORD_NUMBER_OF_DOCS / index[str(termID)][0])
        postings = index[str(termID)][1:]
        for tup in postings:
            docID, freq = tup[0], tup[1]
            if docID not in w:
                w[docID] = {}
            if freq == 0:
                w[docID][termID] = 0
            else:
                w[docID][termID] = (1 + math.log10(freq)) * math.log10(STANFORD_NUMBER_OF_DOCS / index[str(termID)][0])
            s[docID] += w[docID][termID]*w[-1][termID]
    best_documents = np.argsort(s)[::-1][:number_of_documents]
    return [docID for docID in best_documents if s[docID] > 0]


def vectorial_search_cacm_normalized(query, number_of_documents):
    """
    Retourne les meilleurs docIDs correspondant à la requête avec une recherche vectorielle normalisée par tf-idf
    :param query: la requête utilisateur
    :param number_of_documents: le nombre de documents retournés
    :return: la liste des docIDs
    """
    parsed_query = parse_query(query)
    w = {-1: {"tot": 0}}
    s = (STANFORD_NUMBER_OF_DOCS + 1) * [0]
    for termID in parsed_query:
        nb = parsed_query.count(termID)
        w[-1][termID] = (1 + math.log10(nb)) * math.log10(STANFORD_NUMBER_OF_DOCS / index[str(termID)][0])
        w[-1]["tot"] += w[-1][termID]**2
        postings = index[str(termID)][1:]
        for tup in postings:
            docID, freq = tup[0], tup[1]
            if docID not in w:
                w[docID] = {"tot": 0}
            if freq == 0:
                w[docID][termID] = 0
            else:
                w[docID][termID] = (1 + math.log10(freq)) * math.log10(STANFORD_NUMBER_OF_DOCS / index[str(termID)][0])
            w[docID]["tot"] += w[docID][termID]**2
            s[docID] += w[docID][termID]*w[-1][termID]
    nq = math.sqrt(w[-1]["tot"])
    for j in range(STANFORD_NUMBER_OF_DOCS):
        if s[j] != 0:
            ndj = math.sqrt(w[j]["tot"])
            s[j] *= ndj/nq
    best_documents = np.argsort(s)[::-1][:number_of_documents]
    return [docID for docID in best_documents if s[docID] > 0]


def vectorial_search_cacm_max_normalized(query, number_of_documents):
    """
    Retourne les meilleurs docIDs correspondant à la requête avec une recherche vectorielle normalisée par la fréquence maximale
    :param query: la requête utilisateur
    :param number_of_documents: le nombre de documents retournés
    :return: la liste des docIDs
    """
    parsed_query = parse_query(query)
    w = {-1: {"tot": 0}}
    s = (STANFORD_NUMBER_OF_DOCS + 1) * [0]
    for termID in parsed_query:
        nb = parsed_query.count(termID)
        w[-1][termID] = nb * math.log10(STANFORD_NUMBER_OF_DOCS / index[str(termID)][0])
        w[-1]["tot"] += w[-1][termID] ** 2
        postings = index[str(termID)][1:]
        for tup in postings:
            docID, freq = tup[0], tup[1]
            if docID not in w:
                w[docID] = {"tot": 0}
            if freq == 0:
                w[docID][termID] = 0
            else:
                w[docID][termID] = freq * math.log10(STANFORD_NUMBER_OF_DOCS / index[str(termID)][0])
            w[docID]["tot"] += w[docID][termID] ** 2
            s[docID] += w[docID][termID] * w[-1][termID]
    for docID in w:
        if docID >= 0:
            max_freq = max([w[docID][termID] for termID in w[docID]])
            for termID in w[docID]:
                s[docID] += w[docID][termID]*w[-1][termID]/max_freq
    best_documents = np.argsort(s)[::-1][:number_of_documents]
    return [docID for docID in best_documents if s[docID] > 0]


common = [""] + getCommonWords()
lem = WordNetLemmatizer()

with open("../stanford_termIDs.json", 'r') as termID_file:
    term_termID = json.load(termID_file)

with open("../stanford_index.json", 'r') as index_file:
    index = json.load(index_file)

with open("../stanford_docIDs.json", 'r') as index_file:
    docIDs = json.load(index_file)

def main():
    req = input("Enter your query: ")
    norm = input("Which normalization do you want? Enter 'no' for no normalization, 'yes' for tf-idf normalization, 'max' for max frequency normalization: ")
    if norm == 'no' :
        docs = vectorial_search_cacm(req, 20)
        print_docs_names(docs)
    elif norm == "yes" :
        docs = vectorial_search_cacm_normalized(req, 20)
        print_docs_names(docs)
    elif norm == "max" :
        docs = vectorial_search_cacm_max_normalized(req, 20)
        print_docs_names(docs)
    else:
        print("Unknown normalization")

def print_docs_names(docs):
    print("Here are the results:\n")
    for docID in docs:
        print(docIDs[str(docID)])

main()
