import os
import re
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization


def segmentation(lines, element):
    documents.append({"id": str(element), "tokens": {}})
    for line in lines:
        lineContent = re.split("\W+", line)[:-1]
        for token in lineContent:
            tokLower = token.lower()
            tokLem = lem.lemmatize(tokLower)
            if tokLem in documents[-1]["tokens"]:
                documents[-1]["tokens"][tokLem] += 1
            else:
                documents[-1]["tokens"][tokLem] = 1

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


documents = []
common = getCommonWords()
lem = WordNetLemmatizer()
#phase de segmentation des documents

"""
for directory in os.listdir('../../pa1-data'):
    print(str(directory))
    for element in os.listdir('../../pa1-data/' + str(directory)):
        file = open('../../pa1-data/' + str(directory)+ '/' + str(element), 'r')
        lines = file.readlines()
        file.close()
        segmentation(lines, element)
"""

for element in os.listdir('../../pa1-data/0'):
    file = open('../../pa1-data/0/' + str(element), 'r')
    lines = file.readlines()
    segmentation(lines, element)

#création de l'index inversé
i = index(documents)

print(size_of_vocabulary(i))