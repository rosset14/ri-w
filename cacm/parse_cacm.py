import re

documents = []

file = open("../cacm.all",'r')

lines = file.readlines()

content = False

for line in lines :
    if line[:2] == ".I" :
        documents.append({"id" : int(line[3:]), "tokens" : {}})
    elif line[:2] in [".T", ".W", ".K"] :
        content = True
    elif line[0] == "." :
        content = False
    elif content :
        lineContent = re.split("\W+", line)[:-1]
        #print(lineContent)
        for token in lineContent :
            if token in documents[-1]["tokens"] :
                documents[-1]["tokens"][token] += 1
            else:
                documents[-1]["tokens"][token] = 1



file.close()