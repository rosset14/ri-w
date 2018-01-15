import re
import math
import numpy as np
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization

CACM_NUMBER_OF_DOCS = 3204


def parse_query(query):
    """
    Returns the termIDs list corresponding to the terms in the query
    :param query: the raw user query (string)
    :return: a list of the corresponding termIDs
    """
    parsed_query = []
    content = re.split("\W+", query)
    for token in content:
        tok_lower = token.lower()
        if tok_lower not in common:
            parsed_query.append(term_termID[lem.lemmatize(tok_lower)])
    return parsed_query


def getCommonWords():
    """
    recupere la liste des mots communs afin de les retirer de l'index
    :return:
    """
    commonFile = open("../common_words")
    return [s[:-1] for s in commonFile.readlines()]


def vectorial_search_cacm(query, number_of_documents):
    """
    Retrieves the 'best' number_of_documents corresponding to the query
    :param query: the raw user query
    :param number_of_documents: the number of documents we want to retrieve
    :return:
    """
    parsed_query = parse_query(query)
    w = {-1: {}}
    s = CACM_NUMBER_OF_DOCS * [0]
    for termID in parsed_query:
        nb = parsed_query.count(termID)
        w[-1][termID] = (1 + math.log10(nb)) * math.log10(CACM_NUMBER_OF_DOCS/index[termID][0])
        postings = index[termID][1:]
        for tup in postings:
            docID, freq = tup[0], tup[1]
            if docID not in w:
                w[docID] = {}
            if freq == 0:
                w[docID][termID] = 0
            else:
                w[docID][termID] = (1 + math.log10(freq)) * math.log10(CACM_NUMBER_OF_DOCS / index[termID][0])
            s[docID] += w[docID][termID]*w[-1][termID]
    best_documents = np.argsort(s)[::-1][:number_of_documents]
    return [docID for docID in best_documents if s[docID] > 0]


def vectorial_search_cacm_normalized(query, number_of_documents):
    """
    Retrieves the 'best' number_of_documents corresponding to the query
    :param query: the raw user query
    :param number_of_documents: the number of documents we want to retrieve
    :return:
    """
    parsed_query = parse_query(query)
    w = {-1: {"tot": 0}}
    s = CACM_NUMBER_OF_DOCS * [0]
    for termID in parsed_query:
        nb = parsed_query.count(termID)
        w[-1][termID] = (1 + math.log10(nb)) * math.log10(CACM_NUMBER_OF_DOCS/index[termID][0])
        w[-1]["tot"] += w[-1][termID]**2
        postings = index[termID][1:]
        for tup in postings:
            docID, freq = tup[0], tup[1]
            if docID not in w:
                w[docID] = {"tot": 0}
            if freq == 0:
                w[docID][termID] = 0
            else:
                w[docID][termID] = (1 + math.log10(freq)) * math.log10(CACM_NUMBER_OF_DOCS / index[termID][0])
            w[docID]["tot"] += w[docID][termID]**2
            s[docID] += w[docID][termID]*w[-1][termID]
    nq = math.sqrt(w[-1]["tot"])
    for j in range(CACM_NUMBER_OF_DOCS):
        if s[j] != 0:
            ndj = math.sqrt(w[j]["tot"])
            s[j] *= ndj/nq
    best_documents = np.argsort(s)[::-1][:number_of_documents]
    return [docID for docID in best_documents if s[docID] > 0]


common = [""] + getCommonWords()
lem = WordNetLemmatizer()
termID_file = open("../index_cacm.txt", 'r')
lines = termID_file.readlines()
termID_file.close()

term_termID = eval(lines[0])
index = eval(lines[1])

nlp1 = vectorial_search_cacm("natural language processing", 20)
nlp2 = vectorial_search_cacm_normalized("natural language processing", 20)
print(nlp1)
print(nlp2)
print(nlp1 == nlp2)
