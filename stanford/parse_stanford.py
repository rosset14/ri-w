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


def number_of_tokens(segmentation):
    count = 0
    for doc in segmentation:
        for token in doc["tokens"]:
            count += doc["tokens"][token]
    return count


documents = []
for directory in os.listdir('../../pa1-data'):
    print(str(directory))
    for element in os.listdir('../../pa1-data/' + str(directory)):
        file = open('../../pa1-data/' + str(directory)+ '/' + str(element), 'r')
        lines = file.readlines()
        segmentation(lines, element)

print(number_of_tokens(documents))