from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup as bsf

import html2text
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import RegexpTokenizer
from spellchecker import SpellChecker
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np

import pickle
import os
import random
import re
import sys
import math

#imports/global variables by Harshita
DAMPING = 0.85
SAMPLES = 10000
from .models import Rank
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import csv
#imports end
vectorizer = TfidfVectorizer()
spell = SpellChecker()
# Create your views here.
# link_site = 'https://xkcd.com/2173/'
# link_site = 'https://en.wikipedia.org/wiki/Free_content'
# link_site = 'https://en.wikipedia.org'
# link_site = 'http://www.scholarpedia.org/article/Main_Page'
link_site = 'http://127.0.0.1:8000/sample/one'



# prefix_link = 'https://xkcd.com'
# prefix_link = 'http://www.scholarpedia.org'
prefix_link = 'http://127.0.0.1:8000'


def index(request):
    return render(request,"engine/index.html")


# def get_crawled():
#     try:
#         pickle_in = open("crawled.pickle","rb")
#         crawled = pickle.load(pickle_in)
#         print("found")
#         return crawled
#     except:
#         links = find_links(link_site)
#         crawled = {}
#         crawled[link_site] = links
#         print("total= ", len(links))
#         j = 1
#         for i in links:
#             if(i in crawled):
#                 continue
#             print("links crawled ",j)
#             j += 1
#             temp_links = find_links(i)
#             crawled[i] = temp_links
#         pickle_out = open("crawled.pickle","wb")
#         pickle.dump(crawled, pickle_out)
#         pickle_out.close()
#         # iterate_pagerank(crawled, DAMPING)
#         return crawled

def get_crawled():
    try:
        pickle_in = open("crawled.pickle","rb")
        crawled = pickle.load(pickle_in)
        print("found")
        return crawled
    except:
        links = find_links(link_site)
        links = list(links)          #converted to list because for loop needs list
        crawled = {}
        crawled[link_site] = set(links)
        # print("total= ", len(links))
        j = 1
        while(len(crawled.keys()) <= 9):
            for i in links:
                # print(i)
                if(i not in crawled):
                    print("links crawled ",j)
                    j += 1
                    temp_links = find_links(i)
                    crawled[i] = temp_links
                    links.extend(temp_links)
                    
                
        pickle_out = open("crawled.pickle","wb")
        pickle.dump(crawled, pickle_out)
        pickle_out.close()
        # iterate_pagerank(crawled, DAMPING)
        return crawled

# def find_links(site):
#     req = requests.get(site)
#     soup = bsf(req.text, 'lxml')
#     all_links = set()
#     for link in soup.find_all('a'):
#         temp = link.get('href')
#         try:
#             if(temp[0] == '/' and temp[1] != '/'):
#                 all_links.add(prefix_link + temp)
#         except:
#             continue
#     return all_links

def find_links(site):
    req = requests.get(site)
    soup = bsf(req.text, 'lxml')
    all_links = set()
    for link in soup.find_all('a'):
        temp = link.get('href')
        # try:
        #     if(temp[0] == '/' and temp[1] != '/'):
        #         all_links.add(prefix_link + temp)
        # except:
        #     continue
        all_links.add(prefix_link + temp)
    return all_links

# returns set of all the links 
def all_links(crawled):
    links = set()
    for i in crawled.keys():
        links.add(i)
        for j in crawled[i]:
            links.add(j)
    return links


# crawled is dictionary with crawled[current_site] = set(links on current_site)
# crawled = get_crawled()

# all the links that are crawled
# allinks = all_links()
# print(len(allinks))



#---------------------------SKYHAWK'S CODE--------------------------------------

def filter_page(site):
    req = requests.get(site)
    h = html2text.HTML2Text()
    h.ignore_links = True
    lemmatizer  = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    txt = h.handle(req.text)
    tokenizer = RegexpTokenizer(r"[a-zA-Z]{3,}|[1-2][7-9][0-9][0-9]") 
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

    
def rumi(list):
    y = len([x for x in list if x>0])
    return y


def get_query_links(q, df, df1):
    q = [q]
    q_vec = vectorizer.fit_transform(df1.iloc[0])
    q_vec = vectorizer.transform(q).toarray().reshape(df.shape[0],)
    result_links = []
    for i in range(len(df.columns)):
        '''
        COSINE SIMILARITY
        '''
        a = np.dot(df.iloc[:, i].values, q_vec) / np.linalg.norm(df.iloc[:, i]) * np.linalg.norm(q_vec)
        if a != 0.0:
            z = rumi(list(df.iloc[:, i].values*q_vec))
            result_links.append([df.columns[i],z,a])
    result_links = sorted(result_links, key = lambda x: (x[1], x[2]),reverse = True)
    result_links = [x[0] for x in result_links]
    return result_links

'''Check Spelling'''
def checkSpell(query):
    query = query.split()
    if(bool(spell.unknown(query))):
        cort = []
        for word in query:
            if(spell.unknown(word)):
                word = spell.correction(word)
            cort.append(word)
        cort = " ".join(cort)
        print(f"did you mean {cort}")
        return(cort)
    else:
        return

'''MODIFYING THIS WILL SCREW UP THE WHOLE PROGRAM'''
# allinks = list(allinks)
# # df1 = create_df1(list(crawled.keys()))
# df1 = create_df1(['http://127.0.0.1:8000/sample/one'])      #for test
# df = term_doc_matrix(df1) 

# print("size of matrix",end=' ')
# print("{} X {}".format((len(df)), len(df.columns) ))

# query = 'people'
# result = get_query_links(query, df)
# print("THE RESULTS FOR QUERY {} ARE \n {} ".format(query,result))
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
    EDIT: Now this function will also work to store the pagerank values in DataBase
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
    print("PAGERANK DICTIONARY IS")
    print(pagerank_dict)            
                
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

def crawl(request):
    crawled = get_crawled()
    print(crawled)
    return render(request, 'engine/crawl.html',{
        "sites": list(crawled.keys())
        # "sites": list(allinks)
    })

def rank(request):
    corpus = get_crawled()
    pagerank = iterate_pagerank(corpus, DAMPING)
    for value in pagerank:
        #print(value)
        if not Rank.objects.filter(page_link=value).exists():
            entry = Rank(page_link = value,pagerank = pagerank[value])  
            entry.save() 
    return render(request,'engine/rank.html',{
        "pagerank":pagerank
    })    


def indexer():
    crawled = get_crawled()
    allinks = list(all_links(crawled))
    # df1 = create_df1(list(crawled.keys()))
    df1 = create_df1(allinks)
    # df1 = create_df1(['http://127.0.0.1:8000/sample/one'])      #for test
    df = term_doc_matrix(df1) 

    print("size of matrix",end=' ')
    print("{} X {}".format((len(df)), len(df.columns) ))

    return df

    

def index_call(request):
    indexer()
    return HttpResponse("RanFine")

@csrf_exempt
def query(request):
    print("QUERY FUNCTION REACHED")
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        #print(data)
        #query = data.get("query")
        query = "Programming"
        crawled = get_crawled()
        allinks = list(all_links(crawled))
        df1 = create_df1(allinks)
        temp = []
        df = pd.read_csv('term_dm.csv', index_col = 'Unnamed: 0')
        result = get_query_links(query,df, df1)
        print("THE RESULTS FOR QUERY {} ARE \n {} ".format(query,result))
        
        return JsonResponse({"message": "Query request sent successfully."}, status=201)

@csrf_exempt       
def q(request):
    print("q function reached")
    if request.method == "POST":
        query = request.POST["search"]
        #query ="PROGRAMMING"
        crawled = get_crawled()
        allinks = list(all_links(crawled))
        df1 = create_df1(allinks)
        temp = []
        df = pd.read_csv('term_dm.csv', index_col = 'Unnamed: 0')
        result = get_query_links(query,df, df1)
        print(result)
        return render(request, "engine/serp.html",{
            "search_results":result
        })
    
