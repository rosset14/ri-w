import re
import math
import numpy as np
import matplotlib.pyplot as plt


def segmentation(lines):
    content = False
    documents = []
    for line in lines:
        if line[:2] == ".I":
            documents.append({"id": int(line[3:]), "tokens": {}})
        elif line[:2] in [".T", ".W", ".K"]:
            content = True
        elif line[0] == ".":
            content = False
        elif content:
            lineContent = re.split("\W+", line)[:-1]
            for token in lineContent:
                tokLower = token.lower()
                if tokLower in documents[-1]["tokens"]:
                    documents[-1]["tokens"][tokLower] += 1
                else:
                    documents[-1]["tokens"][tokLower] = 1
    return documents


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

"""def mergeSort(index):
    if len(index) in[0,1]:
        return index
    else:
        return merge(mergeSort(index[:len(index)//2]), mergeSort(index[len(index)//2:]))

def merge(index1, index2):
    result = []
    i1, i2 =0, 0
    while i1 < len(index1) or i2 < len(index2):
        if i1 == len(index1):
            result.append(index2[i2])
            i2+=1
        elif i2 == len(index2):
            result.append(index1[i1])
            i1+=1
        else:
            if(index1[i1][1] >= index2[i2][1]):
                result.append(index1[i1])
                i1 += 1
            else:
                result.append(index2[i2])
                i2 += 1
    return result"""

common = [""] + getCommonWords()
#print(common)

file = open("../cacm.all", 'r')
lines = file.readlines()
s = segmentation(lines)
i = index(s)

print(number_of_tokens(s))
print(size_of_vocabulary(i))

### half of the collection
numberOfDocuments = len(s)
half = numberOfDocuments // 2
sHalf = s[:half]
iHalf = index(sHalf)

print(number_of_tokens(sHalf))
print(size_of_vocabulary(iHalf))

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
