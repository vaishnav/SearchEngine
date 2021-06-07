from django.shortcuts import render
import requests
from bs4 import BeautifulSoup as bsf
import pickle

import html2text
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Create your views here.
# link_site = 'https://xkcd.com/2173/'
# link_site = 'https://en.wikipedia.org/wiki/Free_content'
link_site = 'https://en.wikipedia.org'


# prefix_link = 'https://xkcd.com'
prefix_link = 'https://en.wikipedia.org'


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
    words = word_tokenize(txt)
    filtered_sentence = []
    for w in words:
        if w not in stop_words:
            if w not in filtered_sentence:
                filtered_sentence.append(lemmatizer.lemmatize(w))
    return filtered_sentence