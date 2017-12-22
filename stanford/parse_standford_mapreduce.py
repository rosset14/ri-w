import re
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization
from multiprocessing import Process



class Mapper(Process):
    def __init__(self, first_doc_num, last_doc_num):
        Process.__init__(self)
        self._first_doc = first_doc_num
        self._last_doc = last_doc_num
        self._buffer = None

    def _get_buffer(self):
        return self._buffer

    buffer = property(_get_buffer)

    def run(self):
        docID_file = open("../standford_docIDs.txt", 'r')
        docID_docs = eval(docID_file.readlines()[0])
        docID_file.close()
        buffer = []
        frequencies = {}
        for i in range(self._first_doc, self._last_doc):
            if i >= len(docID_docs):
                break
            if i != self._last_doc:
                buffer.extend([(term, i, frequencies[term]) for term in frequencies])
                frequencies = {}
            file = open("../../pa1-data/" + docID_docs[i], 'r')
            lines = file.readlines()
            file.close()
            for line in lines:
                lineContent = re.split("\W+", line)[:-1]
                for token in lineContent:
                    tokLower = token.lower()  # on applique deja un traitement pour ne pas prendre en compte les majuscules
                    if not tokLower in common:
                        tokLem = lem.lemmatize(tokLower)  # on applique ensuite un traitement de lemmatisation
                        if tokLem not in frequencies:
                            frequencies[tokLem] = 0
                        else:
                            frequencies[tokLem] += 1
        buffer.extend([(term, self._last_doc - 1, frequencies[term]) for term in frequencies])
        self._buffer = buffer

class Reducer(Process):
    def __init__(self, lines):
        Process.__init__(self)
        self._lines = lines
        self._result = []

    def _get_result(self):
        return self._result

    result = property(_get_result)

    def run(self):
        tprev = None
        postings = []
        for tup in sorted([(term_termID[eval(tup)[0]], eval(tup)[1], eval(tup)[2]) for tup in self._lines]):
            if tup[0] != tprev and tprev is not None:
                self._result.append((tprev, postings))
                postings = []
            postings.append((tup[1], tup[2]))
            tprev = tup[0]
        self._result.append((tprev, postings))


def getCommonWords():
    """
    recupere la liste des mots communs afin de les retirer de l'index
    :return:
    """
    common_file = open("../common_words", 'r')
    return [s[:-1] for s in common_file.readlines()]

lem = WordNetLemmatizer()
lem.lemmatize("hello")

# liste des mots courants
common = [""] + getCommonWords()

termID = open("../standford_termIDs.txt", 'r')
term_termID = eval(termID.readlines()[0])
termID.close()

"""cacm = open("../cacm.all", 'r')
lines = cacm.readlines()
t1, t2 = Mapper(documents_lines=lines[:43276]), Mapper(documents_lines=lines[43276:])
cacm.close()
t1.start()
t2.start()

t1.join()
t2.join()"""

mappers = []
for i in range(5):
    t = Mapper(20000*i, 20000*(i+1))
    t.start()
    mappers.append(t)

for t in mappers:
    t.join()
    for tup in t.buffer:
        if tup[0][0] < "f":
            file = open("../standford_AE.txt", 'a')
            file.write(str(tup))
            file.close()
        elif tup[0][0] < "l":
            file = open("../standford_FK.txt", 'a')
            file.write(str(tup))
            file.close()
        elif tup[0][0] < "q":
            file = open("../standford_LP.txt", 'a')
            file.write(str(tup))
            file.close()
        elif tup[0][0] < "v":
            file = open("../standford_QU.txt", 'a')
            file.write(str(tup))
            file.close()
        else:
            file = open("../standford_VZ.txt", 'a')
            file.write(str(tup))
            file.close()


reducers = []

for partition in ["AE", "FK", "LP", "QU", "VZ"]:
    tuples_file = open("../standford_" + partition + ".txt", 'r')
    lines = tuples_file.readlines()
    tuples_file.close()
    t = Reducer(lines)
    reducers.append(t)
    t.start()

final_result = []
for t in reducers:
    t.join()
    final_result.extend(t.result)


final_result.sort()

index_cacm = open("../index_standford_mapreduce.txt", 'w')
index_cacm.write(str(final_result))
index_cacm.close()





