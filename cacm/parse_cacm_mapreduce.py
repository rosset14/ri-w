import re
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization
from multiprocessing import Process
import json


class Mapper(Process):
    def __init__(self, process_num, documents_lines=None):
        Process.__init__(self)
        if documents_lines is not None:
            self._documents_lines = documents_lines
        else:
            self._documents_lines = []
        self._process_num = process_num
        self._buffer = None

    def _get_documents_lines(self):
        return self._documents_lines

    def _set_documents_lines(self, documents_lines):
        self._documents_lines = documents_lines

    def _get_buffer(self):
        return self._buffer

    documents_lines = property(_get_documents_lines, _set_documents_lines)
    buffer = property(_get_buffer)

    def run(self):
        content = False
        frequencies = {}
        self._buffer = []
        docID = -1
        for line in self._documents_lines:
            if line[:2] == ".I":
                if docID != -1:
                    self._buffer.extend([(term, docID, frequencies[term]) for term in frequencies])
                    frequencies = {}
                docID = int(line[3:])
            elif line[:2] in [".T", ".W", ".K"]:  # sections de documents d'interet
                content = True
            elif line[0] == ".":  # autres section
                content = False
            elif content:
                line_content = re.split("\W+", line)[:-1]  # traitement des sections d'interet
                for token in line_content:
                    tok_lower = token.lower()
                    # on applique deja un traitement pour ne pas prendre en compte les majuscules
                    if tok_lower not in common:
                        tok_lem = lem.lemmatize(tok_lower)
                        # on applique ensuite un traitement de lemmatisation (plusieurs sont possibles)
                        if tok_lem not in frequencies:
                            frequencies[tok_lem] = 1
                        else:
                            frequencies[tok_lem] += 1
        self._buffer.extend([(term, docID, frequencies[term]) for term in frequencies])
        with open("../cacm_mapper_" + str(self._process_num) + ".json", 'w') as output_file:
            json.dump(self.buffer, output_file)


class Reducer(Process):
    def __init__(self, process_num, buffer):
        Process.__init__(self)
        self._buffer = buffer
        self._process_num = process_num
        self._result = {}

    def _get_result(self):
        return self._result

    result = property(_get_result)

    def run(self):
        tprev = None
        postings = []
        total = 0
        for tup in sorted([(term_termID[tup[0]], tup[1], tup[2]) for tup in self._buffer]):
            if tup[0] != tprev and tprev is not None:
                self._result[tprev] = [total] + postings
                postings = []
                total = 0
            postings.append((tup[1], tup[2]))
            tprev = tup[0]
            total += int(tup[2])
        self._result[tprev] = [total] + postings
        with open("../cacm_reducer_" + str(self._process_num) + ".json", "w") as output_file:
            json.dump(self._result, output_file)


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

with open("../terms_cacm.json", 'r') as termID_file:
    term_termID = json.load(termID_file)


def mapreduce():
    cacm = open("../cacm.all", 'r')
    lines = cacm.readlines()
    t1, t2 = Mapper(1, documents_lines=lines[:43276]), Mapper(2, documents_lines=lines[43276:])
    cacm.close()
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    b = []
    with open("../cacm_mapper_1.json", 'r') as b1_file:
        b += json.load(b1_file)
    with open("../cacm_mapper_2.json", 'r') as b2_file:
        b += json.load(b2_file)
    b.sort()

    split = -1
    for i in range(len(b)):
        if b[i][0][0] >= "n":
            split = i
            break

    t3, t4 = Reducer(3, b[:split]), Reducer(4, b[split:])

    t3.start()
    t4.start()

    t3.join()
    t4.join()

    with open("../cacm_reducer_3.json", 'r') as r3_output:
        res3 = json.load(r3_output)
    with open("../cacm_reducer_4.json", 'r') as r4_output:
        res4 = json.load(r4_output)
    res = {**res3, **res4}

    with open("../index_cacm_mapreduce.json", 'w') as index_cacm:
        json.dump(res, index_cacm)


mapreduce()
