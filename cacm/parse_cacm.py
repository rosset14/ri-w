import re

def segmentation(lines):
    content = False
    documents = []
    for line in lines :
        if line[:2] == ".I" :
            documents.append({"id" : int(line[3:]), "tokens" : {}})
        elif line[:2] in [".T", ".W", ".K"] :
            content = True
        elif line[0] == "." :
            content = False
        elif content :
            lineContent = re.split("\W+", line)[:-1]
            for token in lineContent :
                tokLower = token.lower()
                if tokLower in documents[-1]["tokens"] :
                    documents[-1]["tokens"][tokLower] += 1
                else:
                    documents[-1]["tokens"][tokLower] = 1
    return(documents)

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

common = getCommonWords()
print(common)

file = open("../cacm.all",'r')
lines = file.readlines()
s = segmentation(lines)
i = index(s)

print(number_of_tokens(s))
print(size_of_vocabulary(i))
file.close()