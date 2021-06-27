from django.shortcuts import render
import requests
from bs4 import BeautifulSoup as bsf

import html2text
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import RegexpTokenizer
from collections import Counter

import pickle
import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


# Create your views here.
# link_site = 'https://xkcd.com/2173/'
# link_site = 'https://en.wikipedia.org/wiki/Free_content'
link_site = 'https://en.wikipedia.org'


# prefix_link = 'https://xkcd.com'
prefix_link = 'https://en.wikipedia.org'


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
            print("links crawled ",j)
            j += 1
            temp_links = find_links(i)
            crawled[i] = temp_links
        pickle_out = open("crawled.pickle","wb")
        pickle.dump(crawled, pickle_out)
        pickle_out.close()
        iterate_pagerank(crawled, DAMPING)
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

def crawl(request):
    crawled = get_crawled()
    return render(request, 'engine/crawl.html',{
        "sites": list(crawled.keys())
    })

#filters html2Text Html to text ignoring tags and links
#lemmetizer eleminates synonyms, stems a word to its root word
#stopword eleminates common words in english lang.
def filter_page(page):
    h = html2text.HTML2Text()
    h.ignore_links = True
    lemmatizer  = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    txt = h.handle(page)
    wf = 1
    tokenizer = RegexpTokenizer(r"\w+")
    words = tokenizer.tokenize(txt)
    filtered_sentence = []
    for w in words:
        if w not in stop_words:
            filtered_sentence.append(lemmatizer.lemmatize(w))
    FW = dict(Counter(sorted(filtered_sentence)))
    return FW
    #returns a dictionary with word frequency


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
    corpus = get_crawled()
    #print(corpus)
    pagerank = iterate_pagerank(corpus, DAMPING)
    #print(pagerank)
    return render(request,'engine/rank.html',{
        "pagerank":pagerank
    })    


    