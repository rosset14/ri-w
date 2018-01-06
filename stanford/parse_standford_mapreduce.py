import re
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization
from multiprocessing import Process


class Mapper(Process):
    def __init__(self, first_doc_num, last_doc_num, thread_num):
        Process.__init__(self)
        self._first_doc = first_doc_num
        self._last_doc = last_doc_num
        self._thread_num = thread_num
        self._AE, self._FK, self._LP, self._QU, self._VZ = [], [], [], [], []

    def run(self):
        docID_file = open("../standford_docIDs.txt", 'r')
        docID_docs = eval(docID_file.readlines()[0])
        docID_file.close()
        frequencies = {}
        nbTokens = 0
        for i in range(self._first_doc, self._last_doc):
            if i >= len(docID_docs):
                break
            file = open("../../pa1-data/" + docID_docs[i], 'r')
            lines = file.readlines()
            file.close()
            for line in lines:
                lineContent = re.split("\W+", line)[:-1]
                for token in lineContent:
                    tokLower = token.lower()  # on applique deja un traitement pour ne pas prendre en compte
                    # les majuscules
                    if tokLower not in common:
                        tokLem = lem.lemmatize(tokLower)  # on applique ensuite un traitement de lemmatisation
                        if tokLem not in frequencies:
                            frequencies[tokLem] = 1
                        else:
                            frequencies[tokLem] += 1
                        nbTokens += 1
            for term in frequencies:
                if term < "f":
                    self._AE.append((term, i, frequencies[term]))
                elif term < "l":
                    self._FK.append((term, i, frequencies[term]))
                elif term < "q":
                    self._LP.append((term, i, frequencies[term]))
                elif term < "v":
                    self._QU.append((term, i, frequencies[term]))
                else:
                    self._VZ.append((term, i, frequencies[term]))
            frequencies = {}
            print("thread {}, document {}".format(self._thread_num, i))
        for term in frequencies:
            if term < "f":
                self._AE.append((term, self._last_doc - 1, frequencies[term]))
            elif term < "l":
                self._FK.append((term, self._last_doc - 1, frequencies[term]))
            elif term < "q":
                self._LP.append((term, self._last_doc - 1, frequencies[term]))
            elif term < "v":
                self._QU.append((term, self._last_doc - 1, frequencies[term]))
            else:
                self._VZ.append((term, self._last_doc - 1, frequencies[term]))
        file = open("../standford_AE.txt", 'a')
        file.write(str(self._AE) + "\n")
        file.close()
        file = open("../standford_FK.txt", 'a')
        file.write(str(self._FK) + "\n")
        file.close()
        file = open("../standford_LP.txt", 'a')
        file.write(str(self._LP) + '\n')
        file.close()
        file = open("../standford_QU.txt", 'a')
        file.write(str(self._QU) + "\n")
        file.close()
        file = open("../standford_VZ.txt", 'a')
        file.write(str(self._VZ) + "\n")
        file.close()
        print("thread {} completed".format(self._thread_num))


class Reducer(Process):
    def __init__(self, partition):
        Process.__init__(self)
        self._partition = partition
        self._result = {}

    def _get_result(self):
        return self._result

    result = property(_get_result)

    def run(self):
        tprev = None
        total = 0
        postings = []
        tuples_file = open("../standford_" + self._partition + ".txt", 'r')
        lines = tuples_file.readlines()
        tuples_file.close()
        tuples = []
        for line in lines:
            tuples.extend(eval(line))
        for tup in sorted([(term_termID[tup[0]], tup[1], tup[2]) for tup in tuples]):
            if tup[0] != tprev and tprev is not None:
                self._result[tprev] = [total] + postings
                postings = []
                total = 0
            postings.append((tup[1], tup[2]))
            tprev = tup[0]
            total += int(tup[2])
        self._result[tprev] = [total] + postings
        file_result = open("../standford_mapreduce_not_sorted.txt", 'a')
        file_result.write(str(self._result) + "\n")
        file_result.close()
        print("reducer completed")


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

partitions = ["AE", "FK", "LP", "QU", "VZ"]


def map():
    mappers = []
    for i in range(5):
        t = Mapper(20000*i, 20000*(i+1), i)
        t.start()
        mappers.append(t)


def reduce():
    reducers = []
    for partition in partitions:
        t = Reducer(partition)
        reducers.append(t)
        t.start()


def merge_index():
    file_not_sorted = open("../standford_mapreduce_not_sorted.txt", 'r')
    indexes = file_not_sorted.readlines()
    file_not_sorted.close()
    merged_index = {}
    for index in indexes:
        merged_index = {**merged_index, **(eval(index))}
    merged_index_file = open("../standford_mapreduce_index.txt", 'a')
    merged_index_file.write(str(merged_index))
    merged_index_file.close()


# map()

# reduce()

# merge_index()
