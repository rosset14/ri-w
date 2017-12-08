import re
import math
import numpy as np
import matplotlib.pyplot as plt


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
    documents = []
    for line in lines:
        if line[:2] == ".I":
            documents.append({"id": int(line[3:]), "tokens": {}})
        elif line[:2] in [".T", ".W", ".K"]:  # sections de documents d'interet
            content = True
        elif line[0] == ".":  # autres section
            content = False
        elif content:
            lineContent = re.split("\W+", line)[:-1]  # traitement des sections d'interet
            for token in lineContent:
                tokLower = token.lower()  # on applique deja un traitement pour ne pas prendre en compte les majuscules
                if tokLower in documents[-1]["tokens"]:
                    documents[-1]["tokens"][tokLower] += 1
                else:
                    documents[-1]["tokens"][tokLower] = 1
    return documents


def index(segmentation):
    """
    creation de l'index inverse a partir des dictionnaires de token de chaque document
    :param segmentation: dictionnaires de token de chaque document
    :return: index inverse
    """
    index = {}
    for doc in segmentation:
        for token in doc["tokens"]:
            if not (token in common):  # on retire les tokens inutiles
                if token in index:
                    index[token][0] += doc["tokens"][token]  # ajoute a la frequence du token sa frequence d'apparition dans ce document
                    index[token].append((doc["id"], doc["tokens"][token]))  # il nous serait aussi possible de garder en memoire la frequence pour chacun des documents
                else:
                    index[token] = [doc["tokens"][token], (doc["id"], doc["tokens"][token])]

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

# liste des mots courants
common = [""] + getCommonWords()

# recuperation de la collection
file = open("../cacm.all", 'r')
lines = file.readlines()

# creation de l'index inverse
s = segmentation(lines)
i = index(s)

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

file.close()
