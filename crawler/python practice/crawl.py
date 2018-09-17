import requests  #package for request something form website
from bs4 import BeautifulSoup  #parse tool
import re #regular expression
from urllib.request import urlretrieve #import urlretrieve from url library file
import os


def download_images(articles):
    for article in articles:
        print(article.text,article['href'])
        if not os.path.isdir(os.path.join('download',article.text)):#create file in download file
            os.mkdir(os.path.join('download',article.text))
        res=requests.get("https://www.ptt.cc"+article['href'])
        images = reg_imgur_file.findall(res.text)
        print(images)
        for image in set(images):
            if re.search("http[s]?://[i.]*imgur.com/(\w+\.(?:jpg|png|gif))",image)!=None:
                ID=re.search("http[s]?://[i.]*imgur.com/(\w+\.(?:jpg|png|gif))",image).group(1)
                print(ID)
                urlretrieve(image,os.path.join('download',article.text,ID)) #save image in right file
    
def crawler(pages=3):
    if not os.path.isdir('download'):
        os.mkdir('download')
    url="https://www.ptt.cc/bbs/Beauty/index.html"
    reg_imgur_file  = re.compile('http[s]?://[i.]*imgur.com/\w+\.(?:jpg|png|gif)')
    for round in range(pages):
        res=requests.get(url)
        soup=BeautifulSoup(res.text,'html.parser')
        tagname= "div.title a"  #the div which class is title
        articles= soup.select(tagname)

        paging = soup.select('div.btn-group-paging a')
        next_url="https://www.ptt.cc"+paging[1]['href']  #preceding page
        url=next_url
        download_images(articles)
        
    
    
reg_imgur_file = re.compile('http[s]?://[i.]*imgur.com/\w+\.(?:jpg|png|gif)')
crawler()
