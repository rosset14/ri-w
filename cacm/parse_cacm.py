import re
import math
import numpy as np
import matplotlib.pyplot as plt
from nltk.stem.wordnet import WordNetLemmatizer  # pour la lemmatisation
import time


def segmentation(lines):
    """
    A partir des documents, on créé le dictionnaire de terme/ termeID et de documentID/ titre ainsi que
    la liste des paires (termeID, documentID) pour ensuite construire l'index, selon l'algorithme BSBI.
    :param lines: l'ensembles de documents de la collection sous forme d'une liste de lignes
    :return: le buffer c'est à dire la liste des paires (termeID, documentID), le dictionnaire de termes/ termesID
    et le dictionnaire de documentID/titre
    """
    content = False  # pour les sections d'interet
    title = False  # pour le titre
    buffer = []
    term_termID = {}
    docID_doc = {}
    next_termID = 0
    docID = -1
    for line in lines:
        if line[:2] == ".I":
            docID = int(line[3:])
        elif line[:2] in [".T", ".W", ".K"]:
            # sections de documents d'interet, remarquons que les auteurs ne sont pas pris en compte
            content = True
            if line[:2] == ".T":  # titre du document à stocker dans docID_doc est à la prochaine ligne
                title = True
            else :
                title = False
        elif line[0] == ".":  # autres section
            content = False
            title = False
        elif content:
            lineContent = re.split("\W+", line)[:-1]  # traitement des sections d'interet
            for token in lineContent:
                tokLower = token.lower()  # on applique deja un traitement pour ne pas prendre en compte les majuscules
                if not tokLower in common:  # seuls les mots qui ne sont pas communs sont considérés
                    tokLem = lem.lemmatize(tokLower)  # on applique ensuite un traitement de lemmatisation (plusieurs sont possibles)
                    if tokLem in term_termID:
                        termID = term_termID[tokLem]
                    else:
                        termID = next_termID
                        term_termID[tokLem] = termID
                        next_termID += 1
                    buffer.append((termID, docID))
            if title:
                docID_doc[docID] = line[:-1]
    return buffer, term_termID, docID_doc


def index(buffer):
    """
    creation de l'index inverse a partir du buffer
    :param segmentation: liste couple (token, document)
    :return: index inverse
    """
    index = {}
    current_termID = -1
    for t in buffer:
        if t[0] == current_termID:  # si ce terme à déjà été rencontré :
            index[current_termID][0] += 1  # ajoute a la frequence du token sa frequence d'apparition de ce terme
            found = -1
            for i in range(1, len(index[current_termID])):
                if index[current_termID][i][0] == t[1]:  # si on  déjà rencontré la même paire de term, doc
                    found = i  # alors on prend la position dans l'index qui correspond
                    break
            if found == -1:
                index[current_termID].append((t[1], 1))  # si ça n'a pas été trouvé, on ajoute le document avec
                # une fréquence de 1 pour le terme considéré
            else:
                index[current_termID][i] = (index[current_termID][i][0], index[current_termID][i][1] + 1)
                # sinon on incrémente simplement la fréquence d'appartition de ce terme dans le document
        else:  # si c'est la première fois que ce terme est rencontré
            current_termID = t[0]
            index[current_termID] = [1, (t[1], 1)]
    return index


def number_of_tokens(segmetation):
    """
    determine le nombre de token de la collection
    :param segmentation:
    :return: nombre de tokens de la collection
    """
    return len(segmentation)


def size_of_vocabulary(index):
    """
    détermine la taille du vocabulaire
    :param index:
    :return: taille du vocabulaire, ie nombre de termes différents
    """
    return len(index)


def getCommonWords():
    """
    recupere la liste des mots communs afin de les retirer de l'index
    :return: liste des mots communs
    """
    commonFile = open("../common_words")
    return [s[:-1] for s in commonFile.readlines()]


def getFrequencies(index):
    """
    Utile pour tracer les graphes frequence vs rang
    """
    return [index[key][0] for key in index]




# CREATION DE L'INDEX POUR LA COLLECTION CACM:

t1 = time.time()

# pour la lemmatisation
lem = WordNetLemmatizer()

# liste des mots courants
common = [""] + getCommonWords()

# recuperation de la collection
file = open("../cacm.all", 'r')
lines = file.readlines()
file.close()


# creation de l'index inverse, du dictionnaire de termes et du dictionnaire de documents
s = segmentation(lines)

term_termID = s[1]
docID_doc = s[2]
i = index(sorted(s[0]))


# sauvegarde de l'index inverse
file_index = open("../index_cacm.txt", 'w')
file_index.write(str(i))
file_index.close()
# sauvegarde du dictionnaire de termes
file_terms = open("../terms_cacm.txt", 'w')
file_terms.write(str(term_termID))
file_terms.close()
# sauvegarde du dictionnaire de documents
file_docs = open("../docs_cacm.txt", 'w')
file_docs.write(str(docID_doc))
file_docs.close()

t2 = time.time()

print(t2 - t1)






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
