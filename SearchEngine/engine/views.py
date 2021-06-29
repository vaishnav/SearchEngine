from django.shortcuts import render
import requests
from bs4 import BeautifulSoup as bsf

import html2text
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import RegexpTokenizer

from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np

import pickle
import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000
vectorizer = TfidfVectorizer()

# Create your views here.
# link_site = 'https://xkcd.com/2173/'
# link_site = 'https://en.wikipedia.org/wiki/Free_content'
# link_site = 'https://en.wikipedia.org'
link_site = 'http://www.scholarpedia.org/article/Main_Page'


# prefix_link = 'https://xkcd.com'
prefix_link = 'http://www.scholarpedia.org'


def index(request):
    return render(request,"engine/index.html")


def get_crawled():
    try:
        pickle_in = open("crawled.pickle","rb")
        crawled = pickle.load(pickle_in)
        print("found")
        return crawled
    except:
        links = find_links(link_site)
        crawled = {}
        crawled[link_site] = links
        print("total= ", len(links))
        j = 1
        for i in links:
            if(i in crawled):
                continue
            print("links crawled ",j)
            j += 1
            temp_links = find_links(i)
            crawled[i] = temp_links
        pickle_out = open("crawled.pickle","wb")
        pickle.dump(crawled, pickle_out)
        pickle_out.close()
        # iterate_pagerank(crawled, DAMPING)
        return crawled

def find_links(site):
    req = requests.get(site)
    soup = bsf(req.text, 'lxml')
    all_links = set()
    for link in soup.find_all('a'):
        temp = link.get('href')
        try:
            if(temp[0] == '/' and temp[1] != '/'):
                all_links.add(prefix_link + temp)
        except:
            continue
    return all_links

# returns set of all the links 
def all_links():
    links = set()
    for i in crawled.keys():
        links.add(i)
        for j in crawled[i]:
            links.add(j)
    return links


# crawled is dictionary with crawled[current_site] = set(links on current_site)
crawled = get_crawled()

# all the links that are crawled
allinks = all_links()
print(len(allinks))

def crawl(request):
    # crawled = get_crawled()
    return render(request, 'engine/crawl.html',{
        # "sites": list(crawled.keys())
        "sites": list(allinks)
    })

#---------------------------SKYHAWK'S CODE--------------------------------------

def filter_page(site):
    '''
    Right after we extract the documents, we have to clean it, so our retrieval process becomes much easier. 
    For each document, we have to remove all unnecessary words, numbers and punctuations, lowercase the word, 
    and remove the doubled space. AND TOKENISE THE WHOLE THING TO STORE IT IN A LIST
    '''
    req = requests.get(site)
    h = html2text.HTML2Text()
    h.ignore_links = True
    lemmatizer  = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    txt = h.handle(req.text)
    tokenizer = RegexpTokenizer(r"[a-zA-Z]+|[1-2][7-9][0-9][0-9]") 
    words = tokenizer.tokenize(txt)
    filtered_sentence = []
    for w in words:
        if w not in stop_words:
            filtered_sentence.append(lemmatizer.lemmatize(w.lower()))
    return sorted(filtered_sentence) #RETURN FILTERED WORDS IN A LIST FORM

def add_to_gc(site, grande_corpus):
    list1 = [" ".join(filter_page(site))]
    grande_corpus[site] = list1
    return grande_corpus
'''
grande corpus is a dictionary that contain page links and content of filtered pages like
grande_corpus = {"link1": ['content'], "link2": ['content2'],......}

'''
def create_gc(links):
    grande_corpus = {}
    for link in links:
        print("adding....."+link)
        grande_corpus = add_to_gc(link, grande_corpus)
    return grande_corpus

def create_df1(links):
    try:
        f = open('grande_corpus.csv')
        return pd.read_csv('grande_corpus.csv', index_col = 'Unnamed: 0')
    except:
        grande_corpus = create_gc(links)
        df1 = pd.DataFrame(grande_corpus)
        df1.to_csv('grande_corpus.csv')
        return df1

def term_doc_matrix(df1):
    try:
        f = open('term_dm.csv')
        #print("file is present")
        return pd.read_csv('term_dm.csv', index_col = 'Unnamed: 0')
    except:
        #print("file was absent")
        doc_vec = vectorizer.fit_transform(df1.iloc[0])
        df2 = pd.DataFrame(doc_vec.toarray().transpose(), index=vectorizer.get_feature_names())
        df2.columns = df1.columns
        df2.to_csv('term_dm.csv')
        print("congrats! matrix created")
        return df2


def get_query_links(q, df):
    q = [q]
    q_vec = vectorizer.fit_transform(df1.iloc[0])
    q_vec = vectorizer.transform(q).toarray().reshape(df.shape[0],)
    result_links = []
    for i in range(len(df.columns)):
        '''
        COSINE SIMILARITY
        The formula calculates the dot product divided by the multiplication of the length on each vector. 
        The value ranges from [1, 0], but in general, the cosine value ranges from [-1, 1]. 
        Because there are no negative values on it, we can ignore the negative value because it never happens.'''
        a = np.dot(df.iloc[:, i].values, q_vec) / np.linalg.norm(df.iloc[:, i]) * np.linalg.norm(q_vec)
        if a != 0.0:
            result_links.append(df.columns[i])
    return result_links

'''very important for creating necessary dataframes
MODIFYING THIS WILL SCREW UP THE WHOLE PROGRAM'''
allinks = list(allinks)
df1 = create_df1(list(crawled.keys())) 
df = term_doc_matrix(df1) 

print("size of matrix",end=' ')
print("{} X {}".format((len(df)), len(df.columns) ))

query = 'people'
result = get_query_links(query, df)
print("THE RESULTS FOR QUERY {} ARE \n {} ".format(query,result))
''' 
HOW TO SEARCH QUERY?
ENTER THE QUERY IN A FORMAT 
query = '<query>'
IN get_query_links function like
result = get_query_links(query, df)
HERE 'df' IS OR RESULTING TERM DOCUMENT MATRIX FROM THE FUNCTION term_doc_matrix(df1)
'''
#-------------------------------SHYHAWK'S CODE END-----------------------------------------------


def iterate_pagerank(corpus, damping_factor):
    """
    Returns PageRank values for each page by iteratively updating
    PageRank values until convergence.
    Returns a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1).
    """
    for page in corpus:
        if len(corpus[page]) == 0:
            corpus.pop(page)
            #corpus[page] = list(corpus[page])
            #for p in corpus:
                #corpus[page].append(p)
         
    revcorpus = rev_corpus(corpus)
    #print("REVERSE")
    #print(revcorpus)
    pagerank_dict = {}
    no_of_pages = len(revcorpus)
    for key in revcorpus:
        pagerank_dict[key] = 1/no_of_pages
    print(pagerank_dict)    
    counter = 0
    while(counter < no_of_pages):
        counter = 0
        for key in revcorpus:
            new_rank = 0
            revcorpus[key] = list(revcorpus[key])
            for value in revcorpus[key]:
                new_rank =  new_rank + (pagerank_dict[value]/len(corpus[value]))    
            new_rank =  (1-damping_factor)/no_of_pages + damping_factor*new_rank
        
            if abs(new_rank - pagerank_dict[key]) <= 0.001:
                counter +=1 
            else:
                pagerank_dict[key] = new_rank                
    return pagerank_dict       

def rev_corpus(corpus):
    dic = {}
    for key in corpus:
        dic[key] = []
    for key in corpus:
        corpus[key] = list(corpus[key])
        for val in corpus[key]:
            if val not in dic:
                dic[val]=[]
            dic[val].append(key)

    return (dic)     


def rank(request):
    # corpus = get_crawled()
    corpus = crawled
    #print(corpus)
    pagerank = iterate_pagerank(corpus, DAMPING)
    #print(pagerank)
    return render(request,'engine/rank.html',{
        "pagerank":pagerank
    })    


    