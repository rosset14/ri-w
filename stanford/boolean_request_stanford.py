import time
from math import sqrt
from nltk.stem.wordnet import WordNetLemmatizer  # pour la lemmatisation
import json


# IMPORT DE FICHIERS ---------------------------------------------------------------------------------------------------


# import du dictionnaire des termes et de leurs ID
with open('../stanford_termIDs.json', 'r') as file:
    terms_id = json.load(file)

# import du dictionnaire des documents et de leurs titres
with open('../stanford_docIDs.json', 'r') as file:
    docs_id = json.load(file)

# import de l'index
with open('../stanford_index.json', 'r') as file:
    index = json.load(file)


number_of_documents = 88998 # quand NOT est utilisé, il faut retourner la liste complémentaire de documents
lem = WordNetLemmatizer()

# RECUPERATION DE REQUETES ---------------------------------------------------------------------------------------------

# pour avoir une requête de l'utilisateur
def get_request():
    """
    Pour prendre l'input de l'utisateur comme requête
    :return: la requête de l'utilisateur
    """
    request = input("Give me a boolean request please. ex: (x AND NOT y) OR (z) ")
    return request


# TRAITEMENT DES REQUETES ----------------------------------------------------------------------------------------------

# not
def not_request(posting):
    """
    Quand une requete contient "NOT mot", cette fonction crée la liste de ducuments qui ne contiennent pas 'mot'
    :param posting: la liste des documents cntenant le mot d'intérêt
    :return: la liste complémentaire, ie les documents ne contenant pas le mot d'intérêt
    """
    list_doc = list(range(1, number_of_documents + 1)) # liste de tous les documents de la collection Stanford
    if posting is None:  # si un mot de la requête ne correspond à aucun mot de l'index ...
        return list_doc  # ... on renvoie l'ensemble des documents
    for i in reversed(range(len(posting))):
        list_doc.pop(posting[i] -1)
    return list_doc


# and
def and_request(posting1, posting2):
    """
    Quand une requête contient "V1 AND V2", cette fonction créé la liste des documents qui satisfont
    simultanément V1 et V2.
    Cette version n'implémente pas la logique de skip.
    :param posting1: la liste des documents qui satisfont V1
    :param posting2: la liste des documents qui satisfont V2
    :return: la liste des documents qui satisfont V1 et V2 simultanément
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
    Quand une requête contient "V1 AND V2", cette fonction créé la liste des documents qui satisfont
    simultanément V1 et V2.
    Cette version implémente la logique de skip.
    :param posting1: la liste des documents qui satisfont V1
    :param posting2: la liste des documents qui satisfont V2
    :return: la liste des documents qui satisfont V1 et V2 simultanément
    """
    n1 = int(sqrt(len(posting1)))
    n2 = int(sqrt(len(posting2)))
    list_skip1 = []  # liste des points de comparaison pour faire un skip
    while n1 < len(posting1):
        list_skip1.append(n1)
        n1 += list_skip1[0]
    list_skip2 = []  # liste des points de comparaison pour faire un skip
    while n2 < len(posting2):
        list_skip2.append(n2)
        n2 += list_skip2[0]

    list_doc = []
    c1 = 0
    c2 = 0
    while c1 < len(posting1) and c2 < len(posting2):
        if posting1[c1] == posting2[c2]:
            list_doc.append(posting1[c1])
            c1 += 1
            c2 += 1
        elif (list_skip2 != []) and (posting1[c1] >= posting2[list_skip2[0]]):
            c2 = list_skip2.pop(0)
        elif (list_skip1!= []) and (posting2[c2] >= posting1[list_skip1[0]]):
            c1 = list_skip1.pop(0)
        elif posting1[c1] > posting2[c2]:
            c2 += 1
        else:
            c1 += 1
    return list_doc


# or

def or_request(posting1, posting2):
    """
    Quand une requête contient "V1 OR V2", cette fonction créé la liste des documents qui satisfont
    soit V1 soit V2.
    :param posting1: la liste des documents qui satisfont V1
    :param posting2: la liste des documents qui satisfont V2
    :return: la liste des documents qui satisfont V1 ou V2
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


# gestion d'une requête entière

def get_posting(word):
    """
    Trouve la liste des postings correspondant à un mot dans l'index, c'est à dire la liste de documents
    contenant le mot
    Si le mot n'est pas dans l'index, on retourne None et on affiche un message à l'utilisateur
    :param word: le mot d'intérêt
    :return: la liste de documents contenant le mot d'intérêt
    """
    word = word.lower()
    word = lem.lemmatize(word)
    try:
        term_id = terms_id[word]
        posting = index[str(term_id)][1:]
        for d in range(len(posting)):
            posting[d] = posting[d][0]
        return posting
    except:
        print(word + " is not in the index, please try another request")
        return None


def manage_boolean_request(req):
    """
    A partir de la requête de l'utilisateur, on trouve la liste de documents correspondants dans la collection Stanford
    :param req: la requête de l'utilisateur (str)
    :return: liste de documents correspondants
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
        suppress_None(section_postings)  # on enlève les None qui correspondent aux mots qui ne sont pas l'index
        sort_by_len(section_postings)  # on trie par ordre croissant pour optimiser l'algorithme
        while len(section_postings)>1:
            p1 = section_postings.pop()
            p2 = section_postings.pop()
            insert_by_len(section_postings, and_request_skip(p1, p2))
            # and_request_skip permet d'utiliser la logique de skip, on peut utiliser and_request sinon
        if section_postings == []:
            return []
        total_postings.append(section_postings[0])
    suppress_None(total_postings)  # on enlève les None qui correspondent aux mots qui ne sont pas l'index
    sort_by_len(total_postings)  # on trie par ordre croissant pour optimiser l'algorithme
    while len(total_postings) > 1:
        p1 = total_postings.pop()
        p2 = total_postings.pop()
        insert_by_len(total_postings, or_request(p1, p2))
    return(total_postings[0])


def suppress_None(liste):
    """
    Permet de supprimer tous les None de la liste
    :param liste:
    :return: liste sans les None
    """
    i = 0
    while i < len(liste):
        if liste[i] is None:
            liste.pop(i)
        else:
            i += 1


def sort_by_len(liste):
    """
    Trie la liste par ordre croissant le longueur des listes contenues.
    :param liste: liste of listes
    :return: liste of listes, triées par ordre croissant de longueurs
    """
    n = len(liste)
    L = []
    for i in range(n):
        s = len(liste[i])
        L.append((s, i))
    L.sort()
    for j in range(len(L)):
        L[j] = liste[L[j][1]]
    return L


def insert_by_len(L, elem):
    """
    Insere une liste dans une liste de liste de telle sorte à préserver l'ordre croissant de taille de listes
    :param L: liste de listes triées par ordre croissant de longueur
    :param elem: la liste qui doit être insérée
    :return: la liste avec le nouvel élément, toujour ordonnée
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


# retour à l'utilisateur

def request_display():
    """
    Prend la requête de l'utilisateur, lance la recherche et affiche le resultat à l'utilisateur.
    :return:
    """
    r = get_request()  # demande la requête
    # t1 = time.time()
    L = manage_boolean_request(r)  # traite la requête
    # t2 = time.time()
    # print(t2 - t1)
    print("here are the documents corresponding to your request :")  # affiche le résultat
    for d in L:
        print("     document n°" + str(d) + " : " + docs_id[str(d)])


request_display()