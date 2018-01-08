# import the index and terms_id

file = open('../index_cacm.txt', 'r')
lines = file.readlines()
file.close()

index = eval(lines[1])
terms_id = eval(lines[0])

number_of_documents = 3204 # when NOT is used, the complementary list of documents is needed


# get a request from the user
def get_request():
    """
    Asks the user for a request and takes his/her input
    :return: the user's request
    """
    request = input("Give me a boolean request please. ex: (x AND NOT y) OR (z) ")
    return request

# example of request
requestex = '(NOT single AND binary AND greater) OR (induces AND NOT international) OR (communicating)'

# not
def not_request(posting):
    """
    When a request contains a "NOT word", creates the list of documents that don't contain the word "word"
    :param posting: the list of documents containing the word of interest
    :return: the complementary list : the list of documents that do not contain the word of interest
    """
    list_doc = list(range(1, number_of_documents + 1)) # list of all the documents of CACM
    for i in reversed(range(len(posting))):
        list_doc.pop(posting[i] -1)
    return list_doc


# and
def and_request(posting1, posting2):
    """
    When a request contains "V1 and V2", creates the list of documents that satisfy V1 and V2 simultaneously.
    This version of the function doesn't implement the skip logic.
    :param posting1: the list of documents satisfying the variable V1
    :param posting2: the list of documents satisfying the variable V2
    :return: the list of documents satisfy both of the variables simultaneously
    """
    list_doc = []
    while posting1 != [] and posting2 != []:
        if posting1[0] == posting2[0]:
            list_doc.append(posting1[0])
            posting1.pop(0)
            posting2.pop(0)
        elif posting1[0]>posting2[0]:
            posting2.pop(0)
        else:
            posting1.pop(0)
    return list_doc

def and_request_skip(posting1, posting2):
    """
    When a request contains "V1 and V2", creates the list of documents that satisfy V1 and V2 simultaneously.
    This version of the function implements the skip logic.
    :param posting1: the list of documents satisfying the variable V1
    :param posting2: the list of documents satisfying the variable V2
    :return: the list of documents satisfy both of the variables simultaneously
    """
    pass


# or

def or_request(posting1, posting2):
    """
    When a request contains "V1 or V2", creates the list of documents that satisfy V1 or V2.
    :param posting1: the list of documents satisfying the variable V1
    :param posting2: the list of documents satisfying the variable V2
    :return: the list of documents that satisfies at least one of the variables
    """
    list_doc = []
    while posting1 != [] and posting2 != []:
        if posting1[0] == posting2[0]:
            list_doc.append(posting1[0])
            posting1.pop(0)
            posting2.pop(0)
        elif posting1[0] > posting2[0]:
            list_doc.append(posting2[0])
            posting2.pop(0)
        else:
            list_doc.append(posting1[0])
            posting1.pop(0)
    return list_doc + posting1 + posting2


# manage a full request

def get_posting(word):
    """
    Finds in the index the documents containing the word of interest
    :param word: word of interest
    :return: the documents containing the word of interest
    """
    try:
        term_id = terms_id[word]
        posting = index[term_id][1:]
        for d in range(len(posting)):
            posting[d] = posting[d][0]
        return posting
    except:
        raise Exception(word + " is not in the index, please try another request")


def manage_boolean_request(req):
    """
    From a user's request, finds the documents fulfilling it in the collection CACM
    :param req: the user's request (str)
    :return: the list of documents id fulfilling the request
    """
    req_or = req.split('OR')
    total_postings = []
    for section in req_or:
        req_and = section.split('AND')
        section_postings = []
        for variable in req_and:
            variable = variable.replace(' ', '')
            variable = variable.replace('(', '')
            variable = variable.replace(')', '')
            if variable[:3] == 'NOT':
                variable = variable[3:]
                posting = get_posting(variable)
                posting = not_request(posting)
            else:
                posting = get_posting(variable)
            section_postings.append(posting)
        sort_by_len(section_postings)
        while len(section_postings)>1:
            # could be improved by the skip list algo TODO
            p1 = section_postings.pop()
            p2 = section_postings.pop()
            insert_by_len(section_postings, and_request(p1, p2))
        total_postings.append(section_postings[0])
    sort_by_len(total_postings)
    while len(total_postings) > 1:
        p1 = total_postings.pop()
        p2 = total_postings.pop()
        insert_by_len(total_postings, or_request(p1, p2))
    return(total_postings[0])


def sort_by_len(liste):
    """
    Sorts a list of lists by the length of the lists
    :param liste: list of lists
    :return: list of lists, sorted by their length
    """
    n = len(liste)
    L = []
    for i in range(n):
        s = len(liste[i])
        L.append((s, i))
    L.sort()
    for j in range(n):
        L[j] = liste[L[j][1]]
    return L


def insert_by_len(L, elem):
    """
    Insert a list in a list of list, so as to preserve the growing length of the lists
    :param L: list of lists sorted by their length
    :param elem: a list to be inserted
    :return: the list with the new element, sorted by the length of its elements
    """
    n = len(L)
    i = 0
    if n == 0:
        L.append(elem)
    while i < n:
        if len(L[i]) < len(elem):
            i += 1
            if i == n:
                L.append(elem)
        else:
            L.insert(i, elem)
            i = n
    return L


# return the result to the user in a user friendly way

def request():
    L = manage_boolean_request(requestex)
    print("here are the documents corresponding to your request :")
    print(L)


request()