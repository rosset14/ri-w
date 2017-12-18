import re
import math
import numpy as np
import matplotlib.pyplot as plt
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization


def segmentation(lines):
    """
        Cette fonction permet de construire une liste documents avec des dictionnaires (un par documents) avec les tokens du document et leur frequence.

        :param lines: lignes du document a traiter

        exemple : doc 1 : Le chat est vert, le chat est bleu.
                  doc 2 : Le ciel

        documents : [{"id": "doc 1", "tokens":{"le": 2; "chat": 2, "est": 2; "bleu": 1; "vert": 1}},
                     {"id": "doc 2", "tokens": {"le": 1; "ciel": 1}}]

        Nous avons choisi de passer par des dictionnaires plutot que par une liste de tupple (token, doc) a trier avant de
        construire l'index inverse, car la gestion de la memoire se fait de facon automatique.
        """
    content = False
    buffer = []
    term_termID = {}
    next_termID = 0
    docID = -1
    for line in lines:
        if line[:2] == ".I":
            docID = int(line[3:])
        elif line[:2] in [".T", ".W", ".K"]:  # sections de documents d'interet
            content = True
        elif line[0] == ".":  # autres section
            content = False
        elif content:
            lineContent = re.split("\W+", line)[:-1]  # traitement des sections d'interet
            for token in lineContent:
                tokLower = token.lower()  # on applique deja un traitement pour ne pas prendre en compte les majuscules
                if not tokLower in common:
                    tokLem = lem.lemmatize(tokLower)  # on applique ensuite un traitement de lemmatisation (plusieurs sont possibles)
                    if tokLem in term_termID:
                        termID = term_termID[tokLem]
                    else:
                        termID = next_termID
                        term_termID[tokLem] = termID
                        next_termID += 1
                    buffer.append((termID, docID))
    return buffer, term_termID


def index(buffer):
    """
    creation de l'index inverse a partir des dictionnaires de token de chaque document
    :param segmentation: dictionnaires de token de chaque document
    :return: index inverse
    """
    index = {}
    current_termID = -1
    for t in buffer:
        if t[0] == current_termID:
            index[current_termID][0] += 1  # ajoute a la frequence du token sa frequence d'apparition dans ce document
            found = -1
            for i in range(1, len(index[current_termID])):
                if index[current_termID][i][0] == t[1]:
                    found = i
                    break
            if found == -1:
                index[current_termID].append((t[1], 1))
            else:
                index[current_termID][i] = (index[current_termID][i][0], index[current_termID][i][1] + 1)
        else:
            current_termID = t[0]
            index[current_termID] = [1, (t[1], 1)]
    return index


def number_of_tokens(segmentation):
    """
    determine le nombre de token de la collection
    :param segmentation:
    :return: nombre de tokens de la collection
    """
    count = 0
    for doc in segmentation:
        for token in doc["tokens"]:
            count += doc["tokens"][token]  # on compte le nombre de token grace a leur frequence dans chaque document
    return count


def size_of_vocabulary(index):
    return len(index)


def getCommonWords():
    """
    recupere la liste des mots communs afin de les retirer de l'index
    :return:
    """
    commonFile = open("../common_words")
    return [s[:-1] for s in commonFile.readlines()]


def getFrequencies(index):
    """
    Utile pour tracer les graphes frequence vs rang
    """
    return [index[key][0] for key in index]

lem = WordNetLemmatizer()

# liste des mots courants
common = [""] + getCommonWords()

# recuperation de la collection
file = open("../cacm.all", 'r')
lines = file.readlines()

# creation de l'index inverse
s = segmentation(lines)
term_termID = s[1]
i = index(sorted(s[0]))

print(term_termID)
print(i)
file.close()

file_index = open("../index_cacm.txt", 'w')
file_index.write(str(term_termID) + "\n")
file_index.write(str(i))
file_index.close()

"""
# estimations
print(number_of_tokens(s))
print(size_of_vocabulary(i))

### half of the collection
numberOfDocuments = len(s)
half = numberOfDocuments // 2
sHalf = s[:half]
iHalf = index(sHalf)

print(number_of_tokens(sHalf))
print(size_of_vocabulary(iHalf))


#graphes de frequence/rang
freq = getFrequencies(i)
freq.sort()
freq.reverse()
print(freq)

rank = [i+1 for i in range(len(freq))]

plt.plot(np.array(rank),np.array(freq))
plt.show()

freqLog = [math.log(f) for f in freq]
rankLog = [math.log(r) for r in rank]

plt.plot(np.array(rankLog),np.array(freqLog))
plt.show()

file.close()"""
