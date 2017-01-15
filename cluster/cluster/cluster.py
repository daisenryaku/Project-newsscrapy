# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import scipy.spatial.distance as dist
import jieba
import re

with open('stopwords.dat','r') as f:
    g=f.readlines()
stopwords=set([x.rstrip('\n').decode('utf8') for x in g])

def calc_hot(df,word_dict):
    hot = 0
    list = []
    for d in df['title']:
        d = d.decode('utf-8')
        words = set(jieba.lcut(d))
        for word in words:
            hot += word_dict.get(word, 0)
        hot /= (2 + np.sqrt(len(words)))
        list.append(hot)
    df['hot'] = list
    return df

def sort_hot(df):
    df = df.sort_values(by='hot',ascending = False)
    df = df.set_index([ range(len(df)) ])
    return df

def calc_dict(document,cutall=True):
    pat_num=re.compile(r'\d{2,}')
    pat_en=re.compile(r'[a-zA-Z]{3,}')
    pat_ch=re.compile(u"[\u4e00-\u9fa5]+")

    word_dict={}
    word_dict['numOfNumbers']=0
    word_dict['numOfNumbers']+=len(pat_num.findall(document))

    sentences = pat_ch.findall(document)
    ch_text = u''.join(sentences)
    word_list=[]
    if cutall == True:
        word_list = jieba.lcut(ch_text,cut_all=True)
    else:
        word_list = jieba.lcut(ch_text)

    word_list+=pat_en.findall(document)
    word_list=[x for x in word_list if x not in stopwords]
    for word in word_list:
        word_dict.setdefault(word,0)
        word_dict[word]+=1
    return word_dict

def calc_list(document,cutall=True):
    pat_num = re.compile(r'\d{2,}')
    pat_en = re.compile(r'[a-zA-Z]{3,}')
    pat_ch = re.compile(u"[\u4e00-\u9fa5]+")

    sentences = pat_ch.findall(document)
    ch_text = u''.join(sentences)
    word_list=[]
    if cutall == True:
        word_list = jieba.lcut(ch_text,cut_all=True)
    else:
        word_list = jieba.lcut(ch_text)

    word_list += pat_en.findall(document)
    word_list += pat_num.findall(document)
    word_list = [x for x in word_list if x not in stopwords]
    word_list = list(set(word_list))
    return word_list

def freq2vec(word_dict,word_list):
    length=len(word_list)
    word2index=dict([(word_list[i],i) for i in range(length)])
    new_vec=[0]*length
    for word,freq in word_dict.iteritems():
        t=word2index.get(word,None)
        if t == None:
            continue
        else:
            new_vec[t] = freq
    return new_vec

def build_doc(df):
    document = ''
    for d in df['title']:
        if isinstance(d,float):
            pass
        else:
            document += d.decode('utf-8')
        document += ','
    for d in df['abstract']:
        if isinstance(d,float):
            pass
        else:
            document += d.decode('utf-8')
        document += ','
    return document

def build_vec(df,word_list):
    vec = []
    for d in df['title']:
        d = d.decode('utf-8')
        word_dict = calc_dict(d)
        new_vec = freq2vec(word_dict,word_list)
        vec.append(new_vec)
    return vec

def jaccard(x,y):
    matV = np.mat([x,y])
    return dist.pdist(matV,'jaccard')

def Euclidean(x,y):
    vector1 = np.mat(x)
    vector2 = np.mat(y)
    return np.sqrt((vector1 - vector2) * ((vector1 - vector2).T))

def Cosine(x,y):
    vector1 = np.mat(x)
    vector2 = np.mat(y).T
    return np.dot(vector1,vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))

def Cosine_Cluster(vec,df):
    for i in range(len(vec)):
        for j in range(1,11):
            x = vec[i]
            if i+j < len(df):
                y = vec[i+j]
                if Cosine(x, y) > 0.5:
                    print df['title'][i]
                    print df['title'][j]
                    print Cosine(x, y)

def jaccard_Cluster(vec,df):
    for i in range(len(vec)):
        for j in range(1,11):
            x = vec[i]
            if i+j < len(df):
                y = vec[i+j]
                if jaccard(x,y) < 0.9:
                    print df['title'][i]
                    print df['title'][j]
                    print jaccard(x, y)
