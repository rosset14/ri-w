import re
import math
import numpy as np
import matplotlib.pyplot as plt
import json
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization
import time

plt.close()

CACM_NUMBER_OF_DOCS = 3204


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
            except KeyError:
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
    s = (CACM_NUMBER_OF_DOCS + 1) * [0]
    for termID in parsed_query:
        nb = parsed_query.count(termID)
        w[-1][termID] = (1 + math.log10(nb)) * math.log10(CACM_NUMBER_OF_DOCS/index[str(termID)][0])
        postings = index[str(termID)][1:]
        for tup in postings:
            docID, freq = tup[0], tup[1]
            if docID not in w:
                w[docID] = {}
            if freq == 0:
                w[docID][termID] = 0
            else:
                w[docID][termID] = (1 + math.log10(freq)) * math.log10(CACM_NUMBER_OF_DOCS / index[str(termID)][0])
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
    s = (CACM_NUMBER_OF_DOCS + 1) * [0]
    for termID in parsed_query:
        nb = parsed_query.count(termID)
        w[-1][termID] = (1 + math.log10(nb)) * math.log10(CACM_NUMBER_OF_DOCS/index[str(termID)][0])
        w[-1]["tot"] += w[-1][termID]**2
        postings = index[str(termID)][1:]
        for tup in postings:
            docID, freq = tup[0], tup[1]
            if docID not in w:
                w[docID] = {"tot": 0}
            if freq == 0:
                w[docID][termID] = 0
            else:
                w[docID][termID] = (1 + math.log10(freq)) * math.log10(CACM_NUMBER_OF_DOCS / index[str(termID)][0])
            w[docID]["tot"] += w[docID][termID]**2
            s[docID] += w[docID][termID]*w[-1][termID]
    nq = math.sqrt(w[-1]["tot"])
    for j in range(CACM_NUMBER_OF_DOCS):
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
    s = (CACM_NUMBER_OF_DOCS + 1) * [0]
    for termID in parsed_query:
        nb = parsed_query.count(termID)
        w[-1][termID] = nb * math.log10(CACM_NUMBER_OF_DOCS / index[str(termID)][0])
        w[-1]["tot"] += w[-1][termID] ** 2
        postings = index[str(termID)][1:]
        for tup in postings:
            docID, freq = tup[0], tup[1]
            if docID not in w:
                w[docID] = {"tot": 0}
            if freq == 0:
                w[docID][termID] = 0
            else:
                w[docID][termID] = freq * math.log10(CACM_NUMBER_OF_DOCS / index[str(termID)][0])
            w[docID]["tot"] += w[docID][termID] ** 2
            s[docID] += w[docID][termID] * w[-1][termID]
    for docID in w:
        if docID >= 0:
            max_freq = max([w[docID][termID] for termID in w[docID]])
            for termID in w[docID]:
                s[docID] += w[docID][termID]*w[-1][termID]/max_freq
    best_documents = np.argsort(s)[::-1][:number_of_documents]
    return [docID for docID in best_documents if s[docID] > 0]


def evaluation(number_of_returned_docs, normalization, beta):
    """
    Effectue l'évaluation (rappel, précision, E-measure, F-measure) de la recherche vectorielle
    :param number_of_returned_docs: le nombre maximal de documents retournés
    :param normalization: le type de normalisation : 'no' si aucune, 'yes' si normalisation tf-idf, 'max' si normalisation par le maximum
    :param beta: le paramètre beta utilisé pour calculer la E-measure
    :return: un tuple contenant les listes de points correspondant au rappel, à la précision, la E-measure et la F-measure au rang k, 1<k<number_of_returned_docs
    """
    if normalization not in ["no", "yes", "max"]:
        raise ValueError("Unknown normalization, use 'no', 'yes' or 'max'")
    with open("../query.text", 'r') as queries_file:
        queries_lines = queries_file.readlines()
    with open("../qrels.text", 'r') as expected_results_file:
        expected_results_lines = expected_results_file.readlines()
    query_results = []
    content = False
    current_query_num = -1
    current_query = ""
    cur_line_qrel = 0
    for line in queries_lines:
        if line[:2] == ".I":
            current_query_num = int(line[3:])
        elif line[:2] == ".W":
            content = True
        elif line[0] == ".":
            content = False
            if len(current_query) > 0:
                if normalization == "no":
                    returned_docs = vectorial_search_cacm(current_query, number_of_returned_docs)
                elif normalization == "yes":
                    returned_docs = vectorial_search_cacm_normalized(current_query, number_of_returned_docs)
                else:
                    returned_docs = vectorial_search_cacm_max_normalized(current_query, number_of_returned_docs)
                elements = expected_results_lines[cur_line_qrel].split(" ")
                expected_docs = []
                while int(elements[0]) == current_query_num and cur_line_qrel < len(expected_results_lines):
                    expected_docs.append(int(elements[1]))
                    cur_line_qrel += 1
                    if cur_line_qrel < len(expected_results_lines):
                        elements = expected_results_lines[cur_line_qrel].split(" ")
                query_results.append({"expected": expected_docs, "result": returned_docs})
                current_query = ""
        elif content:
            current_query = current_query[:-1] + " " + line
    R, P, Emeasure, Fmeasure, nb = number_of_returned_docs * [0], number_of_returned_docs * [0],number_of_returned_docs * [0], number_of_returned_docs * [0], number_of_returned_docs * [0]
    for query_result in query_results:
        rappel, precision = [],[]
        for i in range(len(query_result["result"])):
            r = 1
            if len(query_result["expected"]) > 0:
                r = len([doc for doc in query_result["expected"] if doc in query_result["result"][:i+1]])/len(query_result["expected"])
            p = len([doc for doc in query_result["expected"] if doc in query_result["result"][:i+1]])/(i+1)
            rappel.append(r)
            precision.append(p)
        for j in range(len(precision)):
            nb[j] += 1
            R[j] += rappel[j]
            P[j] += max([precision[i] for i in range(len(precision)) if rappel[i] >= rappel[j]])
            emeasure = 1
            if precision[j] > 0 and rappel[j] > 0:
                emeasure -= ((beta**2+1)*precision[j]*rappel[j]/((beta**2)*precision[j] + rappel[j]))
            Emeasure[j] += emeasure
            Fmeasure[j] += 1-emeasure
    return [R[i]/nb[i] for i in range(number_of_returned_docs)], [P[i]/nb[i] for i in range(number_of_returned_docs)], [Emeasure[i]/nb[i] for i in range(number_of_returned_docs)], [Fmeasure[i]/nb[i] for i in range(number_of_returned_docs)]


def make_chart_rappel_precision():
    """
    Trace la courbe rappel/précision
    """
    tupno = evaluation(100, "no", 1)
    plt.plot(tupno[0], tupno[1], 'b')
    tupyes = evaluation(100, "yes", 1)
    plt.plot(tupyes[0], tupyes[1], 'r')
    tupmax = evaluation(100, "max", 1)
    plt.plot(tupmax[0], tupmax[1], 'g')
    plt.xlabel("Rappel")
    plt.ylabel("Précision")
    plt.show()


def make_chart_Emeasure(beta=1):
    """
       Trace la courbe E-measure
    """
    tupno = evaluation(100, "no", beta)
    plt.plot(range(1, len(tupno[2]) + 1), tupno[2], 'b', label="Sans normalisation")
    tupyes = evaluation(100, "yes", beta)
    plt.plot(range(1, len(tupyes[2]) + 1), tupyes[2], 'r', label="Normalisation tf-idf")
    tupmax = evaluation(100, "max", beta)
    plt.plot(range(1, len(tupmax[2]) + 1), tupmax[2], 'g', label="Normalisation par le max")
    plt.xlabel("Nombre de documents retournés")
    plt.ylabel("E-mesure")
    plt.show()


def make_chart_Fmeasure(beta=1):
    """
        Trace la courbe E-measure
    """
    tupno = evaluation(100, "no", beta)
    plt.plot(range(1, len(tupno[3]) + 1), tupno[3], 'b', label="Sans normalisation")
    tupyes = evaluation(100, "yes", beta)
    plt.plot(range(1, len(tupyes[3]) + 1), tupyes[3], 'r', label="Normalisation tf-idf")
    tupmax = evaluation(100, "max", beta)
    plt.plot(range(1, len(tupmax[3]) + 1), tupmax[3], 'g', label="Normalisation par le max")
    plt.xlabel("Nombre de documents retournés")
    plt.ylabel("F-mesure")
    plt.show()

def make_chart_mean_average_precision():
    """
        Trace la courbe de mean average precision
    """
    tupno = evaluation(100, "no", 1)
    plt.plot(range(1, len(tupno[1]) + 1), tupno[1], 'b', label="Sans normalisation")
    tupyes = evaluation(100, "yes", 1)
    plt.plot(range(1, len(tupyes[1]) + 1), tupyes[1], 'r', label="Normalisation tf-idf")
    tupmax = evaluation(100, "max", 1)
    plt.plot(range(1, len(tupmax[1]) + 1), tupmax[1], 'g', label="Normalisation par le max")
    plt.xlabel("Nombre de documents retournés")
    plt.ylabel("Mean average precision")
    plt.show()


common = [""] + getCommonWords()
lem = WordNetLemmatizer()


with open("../terms_cacm.json", 'r') as termID_file:
    term_termID = json.load(termID_file)

with open("../index_cacm.json", 'r') as index_file:
    index = json.load(index_file)


make_chart_mean_average_precision()
