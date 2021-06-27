from django.shortcuts import render
import requests
from bs4 import BeautifulSoup as bsf
import html2text
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import RegexpTokenizer
from collections import Counter

# Create your views here.
link_site = 'https://xkcd.com/2173/'
# link_site = 'https://en.wikipedia.org/wiki/Free_content'


prefix_link = 'https://xkcd.com'
# prefix_link = 'https://en.wikipedia.org'

crawled = {}

def find_links(site):
    req = requests.get(site)
    soup = bsf(req.text, 'lxml')
    all_links = []
    for link in soup.find_all('a'):
        temp = link.get('href')
        try:
            if(temp[0] == '/'):
                all_links.append(prefix_link + temp)
        except:
            continue
    return all_links

def crawl(request):
    links = find_links(link_site)
    crawled[link_site] = links
    j = 1
    for i in links:
        print("links crawled ",j)
        j += 1
        temp_links = find_links(i)
        crawled[i] = temp_links
    return render(request, 'engine/crawl.html',{
        "sites": list(crawled.keys())
    })

#filters html2Text Html to text ignoring tags and links
#lemmetizer eleminates synonyms, stems a word to its root word
#stopword eleminates common words in english lang.
def filter_page(site):
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
    return dict(Counter(sorted(filtered_sentence)))
    #returns a dictionary with word frequency

