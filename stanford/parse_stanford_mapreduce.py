import re
from nltk.stem.wordnet import WordNetLemmatizer  # for lemmatization
from multiprocessing import Process
import json


class Mapper(Process):
    """
       Classe représentant un mapper
    """
    def __init__(self, first_doc_num, last_doc_num, thread_num):
        Process.__init__(self)
        self._first_doc = first_doc_num
        self._last_doc = last_doc_num
        self._thread_num = thread_num
        self._AE, self._FK, self._LP, self._QU, self._VZ = [], [], [], [], []

    def run(self):
        """
            Mapping des documents dans self._documents_lines. Sépare les termes en 5 ensembles selon leur place dans l'alphabet (A-E, F-K, L-P, Q-U, V-Z)
            Cela correspond au fait qu'il y aura 5 reducers. Puis écrit les résultats dans 5 fichiers
        """
        with open("../stanford_docIDs.json", 'r') as docID_file:
            docID_docs = json.load(docID_file)
        frequencies = {}
        nbTokens = 0
        for i in range(self._first_doc, self._last_doc):
            if i >= len(docID_docs):
                break
            file = open("../../pa1-data/" + docID_docs[str(i)], 'r')
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
        with open("../stanford_AE{}.json".format(str(self._thread_num)), 'w') as file:
            json.dump(self._AE, file)
        with open("../stanford_FK{}.json".format(str(self._thread_num)), 'w') as file:
            json.dump(self._FK, file)
        with open("../stanford_LP{}.json".format(str(self._thread_num)), 'w') as file:
            json.dump(self._LP, file)
        with open("../stanford_QU{}.json".format(str(self._thread_num)), 'w') as file:
            json.dump(self._QU, file)
        with open("../stanford_VZ{}.json".format(str(self._thread_num)), 'w') as file:
            json.dump(self._VZ, file)
        print("thread {} completed".format(self._thread_num))


class Reducer(Process):
    """
        Classe représentant un reducer
    """
    def __init__(self, partition):
        Process.__init__(self)
        self._partition = partition
        self._result = {}

    def _get_result(self):
        return self._result

    result = property(_get_result)

    def run(self):
        """
            Reducing des tuples produits par les reducers correspondant à la partie d'alphabet qu'on lui attribue (A-E, F-K, L-P, Q-U, V-Z)
        """
        tprev = None
        total = 0
        postings = []
        tuples = []
        for i in range(5):
            with open("../stanford_" + self._partition + str(i) + ".json", 'r') as file:
                tuples.extend(json.load(file))
        for tup in sorted([(term_termID[tup[0]], tup[1], tup[2]) for tup in tuples]):
            if tup[0] != tprev and tprev is not None:
                self._result[tprev] = [total] + postings
                postings = []
                total = 0
            postings.append((tup[1], tup[2]))
            tprev = tup[0]
            total += int(tup[2])
        self._result[tprev] = [total] + postings
        with open("../stanford_mapreduce_not_sorted{}.json".format(self._partition), 'w') as file:
            json.dump(self._result, file)
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

with open("../stanford_termIDs.json", 'r') as termID_file:
    term_termID = json.load(termID_file)

partitions = ["AE", "FK", "LP", "QU", "VZ"]


def map():
    """
    Effectue le mapping avec 5 mappers
    """
    mappers = []
    for i in range(5):
        t = Mapper(20000*i, 20000*(i+1), i)
        t.start()
        mappers.append(t)
    for mapper in mappers:
        mapper.join()


def reduce():
    """
        Effectue le reducing avec 5 reducers
    """
    print("toto")
    reducers = []
    for partition in partitions:
        t = Reducer(partition)
        reducers.append(t)
        t.start()
    for reducer in reducers:
        reducer.join()



def merge_index():
    """
    Fusionne les index partiels créés par les reducers
    """
    merged_index = {}
    for partition in partitions:
        with open("../stanford_mapreduce_not_sorted{}.json".format(partition), 'r') as file:
            merged_index = {**merged_index, **json.load(file)}
    with open("../stanford_mapreduce_index.json", 'w') as final_file:
        json.dump(merged_index, final_file)


def mapreduce():
    """
    Effectue le map/reduce.
    :return:
    """
    map()
    reduce()
    merge_index()


mapreduce()
