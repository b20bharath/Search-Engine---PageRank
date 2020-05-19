# -*- coding: utf-8 -*-
"""
@author: Bharath
"""
import shutil 
import urllib.error
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import collections as col
import os
import re
import sys
from copy import deepcopy
import requests
import math
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
stop_list = stopwords.words('english')
import pickle

print("-----------------Welcome to the search engine:-----------------")
number_of_links = 20
st = PorterStemmer()
all_retrieved_urls = {}

links ={}
documents = {}

 

def spidering():
    #we are performing spidering for the UIC CS website and crawling the links present in that html file 
    url = 'https://www.cs.uic.edu/'
    
    #Making sure if the crawling stays with in the uic domain
    domain = 'uic.edu'
    
    # Performing a breadth first search on the links that are crawled
    frontier = col.deque()
    url = urlparse(url)
    url = (url.netloc+url.path).lstrip("www.")
    url = url.rstrip("/")
    frontier.append(url)
    count = 1
    foldername = './spideredFiles'
    if os.path.exists(foldername):
        shutil.rmtree(foldername)
    os.makedirs(foldername)

    while(len(frontier)!=0):
        link = frontier.popleft()
        
        try:
            page = requests.get("http://"+link)
            if(page.status_code !=200):
                #print("Error occured while retrieving the page:",url)
                continue
            if (len(links)) >= number_of_links : break
            if link not in links.values():
                links[count] = link
            content_type = page.headers.get('content-type')
            content_type = content_type[:content_type.find(';')]
            if content_type != 'text/html' :
                print('ignoring one of the page because the page format is not html/text')
                continue
            file = "./spideredFiles/document "+ str(count)
            all_retrieved_urls[count] = link
            #print(count,' : ',link)
            count = count + 1
            content = page.text
            dd = os.path.dirname(file)
            os.makedirs(dd, exist_ok=True)
            with open(file, "w") as filehandle:
                filehandle.write(content)
            filehandle.close()
            
            
            soup = BeautifulSoup(content, 'lxml')
            tags = soup.find_all('a')
            file_formats = ['.css','.doc','.exe','.gif','.jpg','.jpeg','.mp3','.avi','.mpg','.mpeg','.pdf','.png','.ram','.rar','.tiff','.wav','.zip']
            #Retrieving all anchor tags from the contant of the html page
            
            for tag in tags:
                
                hyperlink = tag['href']
                #print("tags-----------",hyperlink)
                if hyperlink != None: 
                    hl = urlparse(hyperlink)
                    hyperlink = (hl.netloc+hl.path).lstrip("www.")
                    hyperlink = hyperlink.rstrip("/")
                    
                    if hyperlink not in links.values():
                        #if not hyperlink.startswith('http'): continue
                        # Removing the pond sign or parameters
                        pondpos = hyperlink.find('#')
                        if pondpos > 1 : hyperlink = hyperlink[:pondpos]
                        #if ( hyperlink.endswith('/') ) : hyperlink = hyperlink[:-1]
                        if not any(c in hyperlink for c in file_formats) and domain in hyperlink and hyperlink not in frontier:
                            if hyperlink not in links.values():
                                
                                frontier.append(hyperlink)
                    
            
        except KeyboardInterrupt:
            print('--------------------------------------------')
            print('The program is interrupted by the user')
            break
        except :
            continue



    with open("./spideredFiles/links","wb") as fil:
        pickle.dump(links, fil)

    fil.close()
# After completing the spidering process we would like to preprocess the text from the documents 


    
spidering()






       



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    