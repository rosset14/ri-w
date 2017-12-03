import os
import re


def segmentation(lines, element):
    documents.append({"id": str(element), "tokens": {}})
    for line in lines:
        lineContent = re.split("\W+", line)[:-1]
        for token in lineContent:
            tokLower = token.lower()
            if tokLower in documents[-1]["tokens"]:
                documents[-1]["tokens"][tokLower] += 1
            else:
                documents[-1]["tokens"][tokLower] = 1



documents = []
for element in os.listdir('../../pa1-data/0'):
    file = open('../../pa1-data/0/' + str(element), 'r')
    lines = file.readlines()
    segmentation(lines, element)

print(documents[0])