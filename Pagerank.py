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
import tkinter 
from tkinter import ttk
from tkinter import *
import requests
import math
from nltk.stem import PorterStemmer
st = PorterStemmer()
from copy import deepcopy
from nltk.corpus import stopwords
stop_list = stopwords.words('english')
import pickle
import operator

def main(query):

    pagerank = {}
    number_of_links = 3050
    with open("./spideredFiles/links","rb") as fil:
        links = pickle.load(fil)
        
        
    file_title_word_count = {}
    reverseurl = {}
    no_of_outlinks = {}
    link_count = len(links.keys())
    for key, value in links.items():
        reverseurl[value] = key
    document_words = {}
    inlink = {}
    outlink = {}
    
    df = {}      #caluclating the df of the words
    
    doc_tokens = {}
    documents = {}
    tf_idf_word = {}
    tf_idf_file = {}
    inverted_document_frequency = {}
    document_frequency = {}  
    
    file_eachword_count = {}
    
    document_frequency_title = {}
    word_title_file_count = {}
    
    len_url = {}
    word_title_length = {}
    doc_title_tokens = {}
    word_title_eachfile_count = {}
    file_eachword_title_count = {}
    title_file_frequecy = {}
    inverted_document_frequency_title = {}
    no_of_inlinks = {}
    tf_idf_title_word = {}
    
    def preprocessing_query(Query):
        query = Query.lower() 
        que = re.findall('[a-zA-Z0-9]+',query)
        query = " "
        for item in que:
            if isinstance(item,(int)) != True:
                query += str(item)+" "
        query_tokens = [st.stem(word) for word in query.split(" ") if word not in stop_list and st.stem(word) not in stop_list and len(st.stem(word)) > 2]
        return query_tokens
    
    def preprocessing():
        
        for file in all_files:
            number = file.split()
            if len(number) < 2: continue
            with open("./spideredFiles/"+file,'r') as filehandle:
                file_content = filehandle.read()
            documents[int(number[1])] = file_content
        for i in documents.keys():
            content = documents[i]
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.find_all(text=True)
            documents[i] = content
        for i in documents.keys():
            content = documents[i]  
            lines = []
            for line in content:
                if line == '\n': continue
                if line.parent.name != 'script' or line.parent.name != 'style' or line.parent.name != 'noscript' or line.parent.name != 'header' or line.parent.name != 'title' or line.parent.name != 'head' or line.parent.name != 'meta':
                    lines.append(line.strip())
                    
            
            content = " "
            for item in lines:
                content += str(item)+" "
            
            content = str(content).lower()
            
            fr = re.findall('[a-zA-Z0-9]+',content)
            content = " "
            for item in fr:
                if isinstance(item,(int)) != True:
                    content += str(item)+" "
            content_tokens = [st.stem(word) for word in content.split(" ") if word not in stop_list and st.stem(word) not in stop_list and len(st.stem(word)) > 2]
            for word in content_tokens:
                if word in df.keys():
                    if i not in df[word].keys():
                        df[word][i] = 0
                    df[word][i] += 1
                else:
                    df[word] = {}
                    if i not in df[word].keys():
                        df[word][i] = 0
                    df[word][i] += 1
            doc_tokens[i] = content_tokens
    
    # creating a vector space model for all the document retrived from the URLs crawled earlier     
    
    def tf_idf_document():    
        
        for item in doc_tokens.keys():
            file_eachword_count[item]={}
            Aggregate = 0
            duplicate_words_in_doc = []
            for term in doc_tokens[item]:  
                file_eachword_count[item][term] = file_eachword_count[item].get(term,0)+1
                if term not in duplicate_words_in_doc:
                    flag = tf_idf_term(item,term)
                    Aggregate = Aggregate + flag**2
            tf_idf_file[item] = math.sqrt(Aggregate)
            
    def tf_idf_term(file,token):
        word_frequency = len(df[token])
        document_frequency[token] = word_frequency
        inverted_document_frequency[token] = math.log(number_of_links/word_frequency,2)
        tf_idf_word[token] = df[token][file]*inverted_document_frequency[token]
        return tf_idf_word[token]
    
    def tf_idf_query(query_tokens):
        flag = 0
        word_frequency_query = {}
        for word in query_tokens:
            word_frequency_query[word] = word_frequency_query.get(word,0)+1
        for word in query_tokens:
            flag = flag + (word_frequency_query[word]*inverted_document_frequency.get(word,0))**2
        return math.sqrt(flag)
    
    def cosinesimilarity(query_tokens,query_tfidf):
        cosine_similarity = {}
        document_frequency_query = {}
        for word in query_tokens:
            document_frequency_query[word] = inverted_document_frequency.get(word,0)
        for word in query_tokens:
            if document_frequency_query[word] > 0:
                for file in df[word].keys():
                    cosine_similarity[file] = cosine_similarity.get(file,0) + (df[word][file]*document_frequency_query[word])
        for file in cosine_similarity.keys():
            cosine_similarity[file] = cosine_similarity[file]/(tf_idf_file[file]*query_tfidf)
        sort_cosine = sorted(cosine_similarity.items(), key=lambda x: x[1], reverse=True)
        cosine_similarity = {}   
        for item in sort_cosine:
            cosine_similarity[item[0]] = item[1]
        return cosine_similarity 
    
    
    
    Query = query
    print("please wait upto 20 - 30 min for the output. It takes time for crawling. Thank you for the patience.")
    
    
    
    
    all_files = os.listdir("./spideredFiles/")
    
    preprocessing()
    
    tf_idf_document()
    
    print("---------passed preprocessing----")
    query_tokens = preprocessing_query(Query)
    
    query_tfidf = tf_idf_query(query_tokens)
    
    
    
    relevant_links = cosinesimilarity(query_tokens,query_tfidf)
    
    
    count = 1
    #---------------------------------------- Caluclating the pagerank scores----------------------------------
    print_links = {}
    for i in relevant_links.keys():
        print_links[count] = links[i]
        count += 1
    print("---------passed cosine----")
    
    for key in links.keys():
        with open("./spideredFiles/document "+str(key),'r') as fil:
            
            content = fil.read()
            soup = BeautifulSoup(content, 'lxml')
            tags = soup.find_all('a')
            #print(tags)
            for tag in tags:
                try:
                    hyperlink = tag['href']
                        #print("tags-----------",hyperlink)
                    if hyperlink != None: 
                        hl = urlparse(hyperlink)
                        hyperlink = (hl.netloc+hl.path).lstrip("www.")
                        hyperlink = hyperlink.rstrip("/")
                        if hyperlink in links.values():
                            
                            h = reverseurl[hyperlink]
                            inlink.setdefault(h,{})[key]= inlink.setdefault(h, {}).get(key, 0) + 1
                            outlink.setdefault(key,{})[h]= outlink.setdefault(key, {}).get(h, 0) + 1
                        
                except:
                    continue
            try:
                title = soup.find_all('title')
                con = str(title)
                
                content = " "
                for word in con.split():
                    
                    fre = re.findall('[a-zA-Z0-9]+',word)
                    word = " "
                    for item in fre:
                        if isinstance(item,(int)) != True:
                            word += str(item)+" "
                    content += word
                content = content.split(" ")
                doc_title_tokens[key] = []
                duplicate = []
                for word in content: 
                    if word not in stop_list and word != '':
    
                        word = word.lower()
                        word = st.stem(word)
                        word_title_length[key] = word_title_length.get(key,0)+1
                        doc_title_tokens[key].append(word)
                        file_title_word_count.setdefault(key,{})[word]= file_title_word_count.setdefault(key, {}).get(word, 0) + 1
                        
                        if word in word_title_eachfile_count.keys():
                            if key not in word_title_eachfile_count[word].keys():
                                word_title_eachfile_count[word][key] = 0
                            word_title_eachfile_count[word][key] += 1
                        else:
                            word_title_eachfile_count[word] = {}
                            if key not in word_title_eachfile_count[word].keys():
                                word_title_eachfile_count[word][key] = 0
                            word_title_eachfile_count[word][key] += 1
                        if word not in duplicate:
                            word_title_file_count[word] = word_title_file_count.get(word,0)+1
            except:
                pass
    tf_idf_title_file = {}
    final_rank = {}
    def tf_idf_title_document():    
        
        for item in doc_title_tokens.keys():
            file_eachword_title_count[item] = {}
            Aggregate = 0
            duplicate_words_in_doc = []
            for term in doc_title_tokens[item]:  
                file_eachword_title_count[item][term] = file_eachword_title_count[item].get(term,0)+1
                if term not in duplicate_words_in_doc:
                    flag = tf_idf_term_title(item,term)
                    Aggregate = Aggregate + flag**2
            tf_idf_title_file[item] = math.sqrt(Aggregate)
            
    def tf_idf_term_title(file,token):
        word_frequency = len(word_title_eachfile_count[token])
        title_file_frequecy[token] = word_frequency
        inverted_document_frequency_title[token] = math.log(number_of_links/word_frequency,2)
        tf_idf_title_word[token] = word_title_eachfile_count[token][file]*inverted_document_frequency_title[token]
        return tf_idf_title_word[token]
    
    tf_idf_title_document()
    tfidf = {}
    tfidf_title = {}
    i = 1
    leaf_nodes = []
    for i in outlink.keys():
        if i in outlink.keys():
            continue
        else:
            leaf_nodes.append(i)
    
    for key,values in outlink.items():
        no_of_outlinks[key] = len(outlink[key].keys())
    for key,values in inlink.items():
        no_of_inlinks[key] = len(inlink[key].keys())
                         
    
    
    for key,value in document_frequency.items():
        document_frequency[key] = 1/value
        
    tfidf = deepcopy(file_eachword_count)
    for key,value in file_eachword_count.items():
        for f,j in value.items():
            tfidf[key][f] = j*document_frequency[f]
    for key,value in title_file_frequecy.items():
        title_file_frequecy[key] = 1/value
    tfidf_title = deepcopy(file_eachword_title_count)
    for key,value in file_eachword_title_count.items():
        for f,j in value.items():
            tfidf_title[key][f] = j*title_file_frequecy[f]
    link_pagerank = {}
    damping_factor = 0.85
    initial_score = 1/link_count
    
    for key in links.keys():
        link_pagerank[key]= initial_score
    
    r = deepcopy(link_pagerank)
    
    for i in range(25):
        pr_no_outlink = 0
        for link in leaf_nodes:
            pr_no_outlink = pr_no_outlink + (damping_factor * (link_pagerank[link]/link_count))
        for key in links.keys():
            rank = 0
            for k,value in inlink[key].items():
                sc = (link_pagerank[k])/(len(outlink[k].keys()))
                rank += sc
            
            r[key] = (damping_factor*rank)+((1-damping_factor)/link_count) + pr_no_outlink
        link_pagerank = deepcopy(r)
    
    order = sorted(link_pagerank.items(), key=lambda x: x[1], reverse=True)
    print("---------passed pagerank----")
    count =1
    link_pagerank = {}
    serial_rank_page = {}
    for item in order:
        link_pagerank[item[0]] = item[1]
        serial_rank_page[item[0]] = count
        count += 1
    
        
    def calculate_query_pagerank():
        highest_query_in_file = {}
        highest_query_in_file_title ={}
        word_query_frequency = 0
        word_query_title_frequency = 0
        query_words_present_ratio = {}
        no_query_terms_file_sum = {}
        no_query_terms_file_mean = {}
        no_query_terms_file_title_mean = {}
        least_query_in_file = {}
        query_words_present = {}
        no_query_terms_file_title_sum = {}
        least_query_in_file_title = {}
        query_words_present_title_ratio = {}
        no_query_terms_file_tfidf_sum = {}
        least_query_in_file_tfidf = {}
        highest_query_in_file_tfidf = {}
        no_query_terms_file_tfidf_mean = {} 
        query_words_present_title = {}
        calculation = {}
        for key in file_eachword_count.keys():
            query_words_present[key] = 0
        for key in file_eachword_title_count.keys():
            query_words_present_title[key] = 0
        for word in query_tokens:
            word_query_frequency += document_frequency.get(word,0)+1
            word_query_title_frequency += title_file_frequecy.get(word,0) + 1
        for word in query_tokens:
            for k,v in file_eachword_count.items():
                no_query_terms_file_sum[k]=no_query_terms_file_sum.get(k,0)+v.get(word,0)
                if least_query_in_file.get(k,0) == 0: 
                    least_query_in_file[k] =0
                else:
                    if least_query_in_file[k] > v.get(word,100000): least_query_in_file[k] = v.get(word,0)
                if highest_query_in_file.get(k,0) == 0:
                    highest_query_in_file[k] = 0
                else:
                    if highest_query_in_file[k] < v.get(word,0): highest_query_in_file[k] = v.get(word,0)
                if v.get(word,0) != 0 : query_words_present[k] = query_words_present.get(k,0)+1
        no_query_terms_file_mean = deepcopy(no_query_terms_file_sum)
        for k,v in no_query_terms_file_mean.items():
            if(query_words_present[k]!=0):
                no_query_terms_file_mean[k] = (no_query_terms_file_mean[k])/(query_words_present[k])
            query_words_present_ratio[k] = v/len(query_tokens) 
            
        for word in query_tokens:
            for k,v in tfidf.items():
                no_query_terms_file_tfidf_sum[k]=no_query_terms_file_tfidf_sum.get(k,0)+v.get(word,0)
                if least_query_in_file_tfidf.get(k,0) == 0: 
                    least_query_in_file_tfidf[k] =0
                else:
                    if least_query_in_file_tfidf[k] > v.get(word,100000): least_query_in_file_tfidf[k] = v.get(word,0)
                if highest_query_in_file_tfidf.get(k,0) == 0:
                    highest_query_in_file_tfidf[k] = 0
                else:
                    if highest_query_in_file_tfidf[k] < v.get(word,0): highest_query_in_file_tfidf[k] = v.get(word,0)
                
        no_query_terms_file_tfidf_mean = deepcopy(no_query_terms_file_tfidf_sum)
        for k,v in no_query_terms_file_tfidf_mean.items():
            if(query_words_present[k]!=0):
                no_query_terms_file_tfidf_mean[k] = (no_query_terms_file_tfidf_mean[k])/(query_words_present[k])
        for file in file_eachword_count.keys():
            calculation[file] = []
        for file in file_eachword_count.keys():
            calculation[file].append((5*query_words_present[file])+(5*query_words_present_ratio[file])+(0.01*word_query_frequency)+(0.01*word_query_title_frequency))
            calculation[file].append((0.001*no_query_terms_file_sum[file])+(0.01*no_query_terms_file_mean[file])+(0.01*least_query_in_file[file])+(0.01*highest_query_in_file[file]))
            calculation[file].append((0.001*no_query_terms_file_tfidf_sum[file])+(0.01*no_query_terms_file_tfidf_mean[file])+(0.01*least_query_in_file_tfidf[file])+(0.01*highest_query_in_file_tfidf[file]))
            
        for word in query_tokens:
            for k,v in file_eachword_title_count.items():
                no_query_terms_file_title_sum[k]=no_query_terms_file_title_sum.get(k,0)+v.get(word,0)
                if least_query_in_file_title.get(k,0) == 0: 
                    least_query_in_file_title[k] =0
                else:
                    if least_query_in_file_title[k] > v.get(word,100000): least_query_in_file_title[k] = v.get(word,0)
                if highest_query_in_file_title.get(k,0) == 0:
                    highest_query_in_file_title[k] = 0
                else:
                    if highest_query_in_file_title[k] < v.get(word,0): highest_query_in_file_title[k] = v.get(word,0)
                if v.get(word,0) != 0 : query_words_present_title[k] = query_words_present_title.get(k,0)+1
        no_query_terms_file_title_mean = deepcopy(no_query_terms_file_title_sum)
        for k,v in no_query_terms_file_title_mean.items():
            if(query_words_present_title[k]!=0):
                no_query_terms_file_title_mean[k] = (no_query_terms_file_title_mean[k])/(query_words_present_title[k])
            query_words_present_title_ratio[k] = v/len(query_tokens)
        
        no_query_terms_file_tfidf_title_sum = {}
        least_query_in_file_tfidf_title = {}
        highest_query_in_file_tfidf_title = {}
        no_query_terms_file_tfidf_mean_title = {}  
            
        for word in query_tokens:
            for k,v in tfidf_title.items():
                no_query_terms_file_tfidf_title_sum[k]=no_query_terms_file_tfidf_title_sum.get(k,0)+v.get(word,0)
                if least_query_in_file_tfidf_title.get(k,0) == 0: 
                    least_query_in_file_tfidf_title[k] =0
                else:
                    if least_query_in_file_tfidf_title[k] > v.get(word,100000): least_query_in_file_tfidf_title[k] = v.get(word,0)
                if highest_query_in_file_tfidf_title.get(k,0) == 0:
                    highest_query_in_file_tfidf_title[k] = 0
                else:
                    if highest_query_in_file_tfidf_title[k] < v.get(word,0): highest_query_in_file_tfidf_title[k] = v.get(word,0)
                
        no_query_terms_file_tfidf_mean_title = deepcopy(no_query_terms_file_tfidf_title_sum)
        for k,v in no_query_terms_file_tfidf_mean_title.items():
            if(query_words_present[k]!=0):
                no_query_terms_file_tfidf_mean_title[k] = (no_query_terms_file_tfidf_mean_title[k])/(query_words_present[k])   
    
        highest_inlink = max(no_of_inlinks.items(), key=operator.itemgetter(1))[1]
        for file in file_eachword_count.keys():
    
            calculation[file].append((2*query_words_present_title.get(file,0))+(2*query_words_present_title_ratio.get(file,0))+(0.00001*no_of_outlinks.get(file,0))+((no_of_inlinks.get(file,0)/highest_inlink)*120))
            calculation[file].append((0.001*no_query_terms_file_title_sum.get(file,0))+(0.01*no_query_terms_file_title_mean.get(file,0))+(0.01*least_query_in_file_title.get(file,0))+(0.01*highest_query_in_file_title.get(file,0)))
            calculation[file].append((0.001*no_query_terms_file_tfidf_title_sum.get(file,0))+(0.01*no_query_terms_file_tfidf_mean_title.get(file,0))+(0.01*least_query_in_file_tfidf_title.get(file,0))+(0.01*highest_query_in_file_tfidf_title.get(file,0)))
            calculation[file].append(link_pagerank.get(file,0)*100)
        for file in calculation.keys():
            calculation[file] = sum(calculation[file])
        rank = sorted(calculation.items(), key=lambda kv: kv[1], reverse=True)
        
        count =1
        
        for item in rank:
            final_rank[item[0]] = count
    
            count += 1
    
    calculate_query_pagerank()
    
    
    final_page_rank_result = {}
    for k,v in final_rank.items():
        final_page_rank_result[v] = links[k]
    
    flag = 1
    flag_1 = 11
    no_of_pages = 0
    
    '''    
    print("-------------")
    while True:
        print("relavant URLs according to page rank:")
        for i in range(flag,flag_1):
            print(print_links[i])
        
        print("-------------------------------------------------")
        print("relavant URLs according to cosine similarity:")
        for i in range(flag, flag_1):
            print(final_page_rank_result[i])
        print("\n")
        ask = input("Want more links. Please enter 'yes' or 'no'?: ")
        if ask == 'yes':
            no_of_pages = int(input("Number of pages you want: "))
        else:
            print("Thank you and visit again :)")
            break
        flag = flag_1
        flag_1 += no_of_pages
    '''
    final_result = []
    for k,v in print_links.keys():
        final_result.append(v)
        
    return final_result
def first():
    result = main(name.get())
    dis.delete(1.0, END)
    dis.insert(END,result)
window = tkinter.Tk()
window.title("WEB SEARCH ENGINE")
window.minsize(750, 7500)
qu = ttk.Label(window, text="Please enter the query:")
qu.grid(column=0, row=1)
name = tkinter.StringVar()
ne = ttk.Entry(window, width=60, textvariable=name)
ne.grid(column=1, row=1)
dis = tkinter.Text(window, width=100,height=40)
dis.grid(columnspan=4,row=4,sticky=W)
but = ttk.Button(window, text="Search", command=first)
but.grid(column=3, row=1)

window.mainloop()

