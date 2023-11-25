from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin
import requests

#Connect to MongoDB
client = MongoClient('localhost' , 27017)
db = client['crawler']
pages = db.pages

#stores pages
def storePages(url, html):
    pages.insert_one({"url": url, "html": html})

#retrieves URL
def retrieveUrl(url):
    result = requests.get(url)
    return result.text

#crawler
def crawlerThread(frontier):
    visited = set()
    while frontier != 0:
        url = frontier.pop(0)
        visited.add(url)
        html = retrieveUrl(url)
        storePages(url, html)
        soup = BeautifulSoup(html, 'html.parser')
        h1 = soup.find_all('h1')
        if any("Permanent Faculty" in tag.text for tag in h1):
            print("Found target page: ", url)
            storePages(url, html)
            break
        for link in soup.find_all('a'):
            newUrl = link.get('href')
            if newUrl and newUrl not in visited:
                newUrl = urljoin(url, newUrl)
                frontier.append(newUrl)


frontier = ["https://www.cpp.edu/sci/computer-science/"]
crawlerThread(frontier)