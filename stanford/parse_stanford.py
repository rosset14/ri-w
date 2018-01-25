import os
import re
import json
import math
import matplotlib.pyplot as plt
import numpy as np
"""import nltk
nltk.download()"""
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization


def segmentation(lines, docID, buffer, term_termID, next_termID):
    """
    Cette fonction permet d'ajouter a la liste documents les tokens du nouveau document regarde et leur frequence.

    :param lines: lignes du document a traiter
    :param element: titre du document

    exemple : doc 1 : Le chat est vert, le chat est bleu.
              doc 2 : Le ciel

    documents : [{"id": "doc 1", "tokens":{"le": 2; "chat": 2, "est": 2; "bleu": 1; "vert": 1}},
                 {"id": "doc 2", "tokens": {"le": 1; "ciel": 1}}]

    Nous avons choisi de passer par des dictionnaires plutot que par une liste de tupple (token, doc) a trier avant de
    construire l'index inverse, car la gestion de la memoire se fait de facon automatique.
    """
    nextID = next_termID
    for line in lines:
        lineContent = re.split("\W+", line)[:-1]
        for token in lineContent:
            tokLower = token.lower()  # on applique deja un traitement pour ne pas prendre en compte les majuscules
            if not tokLower in common:
                tokLem = lem.lemmatize(tokLower)  # on applique ensuite un traitement de lemmatisation
                                                    # (plusieurs sont possibles)
                if tokLem in term_termID:
                    termID = term_termID[tokLem]
                else:
                    termID = nextID
                    term_termID[tokLem] = termID
                    nextID += 1
                buffer.append((termID, docID))
    return nextID


def index(segmentation):
    index = {}
    for doc in segmentation:
        for token in doc["tokens"]:
            if not (token in common):
                if token in index:
                    index[token][0] += doc["tokens"][token]
                    index[token].append((doc["id"], doc["tokens"][token]))
                else:
                    index[token] = [doc["tokens"][token], (doc["id"], doc["tokens"][token])]
    return index


def number_of_tokens(segmentation):
    count = 0
    for doc in segmentation:
        for token in doc["tokens"]:
            count += doc["tokens"][token]
    return count


def size_of_vocabulary(index):
    return len(index)


def getCommonWords():
    commonFile = open("../common_words")
    return [s[:-1] for s in commonFile.readlines()]


def getFrequencies(index):
    return [index[key][0] for key in index]

"""
for element in os.listdir('../../pa1-data/0')[:1]:
    file = open('../../pa1-data/0/' + str(element), 'r')
    lines = file.readlines()
    segmentation(lines, element)
    file.close()
print(documents)

"""
"""for element in os.listdir('../../pa1-data/0'):
    file = open('../../pa1-data/0/' + str(element), 'r')
    lines = file.readlines()
    file.close()
    segmentation(lines, element)"""


common = [""] + getCommonWords()
lem = WordNetLemmatizer()
#phase de segmentation des documents


def make_blocks_buffers():
    term_termID = {}
    next_termID = 0
    doc_docID = {}
    next_docID = 0

    for directory in os.listdir('../../pa1-data'):
        if directory[0] not in ['.']:  #['.', '5', '6', '7', '8', '9']:  # for half of the collection
            print(str(directory))
            buffer = []
            for element in os.listdir('../../pa1-data/' + str(directory)):
                file = open('../../pa1-data/' + str(directory)+ '/' + str(element), 'r')
                lines = file.readlines()
                file.close()
                docID = next_docID
                next_docID += 1
                doc_docID[docID] = str(directory)+ '/' + str(element)
                next_termID = segmentation(lines, docID, buffer, term_termID, next_termID)
            buffer_file = open("../standford_buffer_" + str(directory)[0] + ".json", 'w')
            json.dump(sorted(buffer), buffer_file)
            buffer_file.close()
    term_termID_file = open("../standford_termIDs.json", 'w')
    json.dump(term_termID, term_termID_file)
    term_termID_file.close()
    doc_docID_file = open("../standford_docIDs.json", 'w')
    json.dump(doc_docID, doc_docID_file)
    doc_docID_file.close()

def merge_block_buffers():
    index = {}
    for i in range(10):
        with open("../standford_buffer_" + str(i) + ".json", 'r') as file_buffer:
            buffer = json.load(file_buffer)
        print("file read")
        freq = 0
        docs = {}
        current = 0
        for posting in buffer:
            if posting[0] != current:
                if freq > 0:
                    if current not in index :
                        index[str(current)] = [freq] + [(docID, docs[docID]) for docID in docs]
                    else:
                        index[str(current)] = [index[str(current)][0] + freq] + index[str(current)][1:] + [(docID, docs[docID]) for
                                                                                            docID in docs]
                freq = 0
                docs = {}
                current = posting[0]
            freq += 1
            if posting[1] in docs:
                docs[posting[1]] += 1
            else:
                docs[posting[1]] = 1
        print("buffer read")
    for key in index:
        index[key] = [index[key][0]] + sorted(index[key][1:])
    index_file = open("../standford_index.json", "w")
    json.dump(index, index_file)
    index_file.close()

#make_blocks_buffers()

#merge_block_buffers()

