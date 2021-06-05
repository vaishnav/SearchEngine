from django.shortcuts import render
import requests
from bs4 import BeautifulSoup as bsf


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