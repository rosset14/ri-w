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
                if token in documents[-1]["tokens"] :
                    documents[-1]["tokens"][token] += 1
                else:
                    documents[-1]["tokens"][token] = 1
    return(documents)

def index(segmentation):
    index = {}
    for doc in segmentation:
        for token in doc["tokens"]:
            if token in index:
                index[token][0] += doc["tokens"][token]
                index[token].append((doc["id"], doc["tokens"][token]))
            else:
                index[token] = [doc["tokens"][token], (doc["id"], doc["tokens"][token])]
    return index

def number_of_tokens(index):
    count = 0
    for token in index:
        count += index[token][0]
    return count

def size_of_vocabulary(index):
    return len(index)

file = open("../cacm.all",'r')
lines = file.readlines()
s = segmentation(lines)
i = index(s)

print(number_of_tokens(i))
print(size_of_vocabulary(i))
file.close()