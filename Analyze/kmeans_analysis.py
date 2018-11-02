#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from pymongo import MongoClient
import subprocess
import json
import random
import imp

from scipy import spatial

date_begin = '2018-10-14'
day_range = 7
date_end = '2018-10-08'

BEGIN = datetime.strptime(date_begin,('%Y-%m-%d')).date()
END = datetime.strptime(date_end,('%Y-%m-%d')).date()


def main(args):
    password = args[1]
    client = MongoClient(host="140.112.107.203", port=27020, username="rootNinja", password=password)  #connect to database
    db = client.CrawlGossiping_formal
    # user1 = db.User.find_one({'id': 54}, {'Message': {'$elemMatch':{'Articleid':{'$in':[0,1,2,3,4,5]}}}})
    # print(user1['Message'][0]['Articleid'])
    # sys.exit(1)
    vec_sum = None
    group = db.Group.find_one({'date':date_begin, 'day_range': day_range})
    for big_group in group['overall_group_list']:
        group_id = big_group['overall_group_id']
        top_30_art = db.finalGroup.find_one({'date':date_begin, 'day_range': day_range , 'group_id':group_id})
        if top_30_art is not None:
            if big_group.get('internal_group_list') != None:
                vec_sum = [[] for i in range(len(big_group.get('internal_group_list') ))]
                index = 0
                for small_group in big_group['internal_group_list']:
                    group_leaders = sorted(small_group['internal_group_leaders'])
                    top30 = sorted(top_30_art['top30'])
                    print(len(top30))
                    vec_sum[index] =  vectorize(group_leaders, top30, db)
                    index += 1
                for i in range(len(vec_sum[1])):
                    print(len(vec_sum[1]))
                    cos_similarity(vec_sum[0][0],vec_sum[1][i])
                sys.exit(1)
    #group_relation()

def vectorize(leaders, articles, db):
    articles = reduce_art(articles, db)
    print(leaders)
    all_vec = [[] for i in range(len(leaders))]
    k = 0
    for user in leaders:
        vec = [0 for i in range(len(articles))]
        user_info = db.User.find_one({'id': user})
        for art in user_info.get('Article'):
            if art['art_id'] in articles:
                vec[articles.index(art['art_id'])] = 1 
        for mes in user_info.get('Message'):
            if mes == '':
                continue
            if mes.get('ArticleId') in articles:
                if mes['React'] == '噓':
                    vec[articles.index(mes['ArticleId'])] = -1
                elif mes['React'] == '推':
                    vec[articles.index(mes['ArticleId'])] = 1
        all_vec[k] = vec
        k += 1
    for i in range(len(all_vec)):
        for j in range(i+1,len(all_vec)):
            if i ==0:
                print(i,j)
                cos_similarity(all_vec[i], all_vec[j])
    return all_vec

def cos_similarity(vec1, vec2):
    # for i in range(len(vec1)):
    #     if vec1[i] !=0:
    #         print(1,i,vec1[i])
    # for i in range(len(vec2)):
    #     if vec2[i] !=0:
    #         print(2,i,vec2[i])
    result = 1 - spatial.distance.cosine(vec1, vec2)
    print(result)
    return result


def reduce_art(articles, db):
    length = len(articles)
    len_sum = 0
    art_info = {}
    for i in articles:
        art = db.Article.find_one({'id':i},{'Boo': 1, 'Push': 1, 'Neutral': 1})
        num = len(art['Boo'] + art['Push'] + art['Neutral'])
        art_info[i] = num
        len_sum = len_sum + num
    gate = len_sum / length
    print(f'number of art after filtering : {length}')
    print('finished count')
    sort_artlist = []
    for key, val in art_info.items():
        if val >= gate:
            sort_artlist.append(key)
    print(f'number of art after filtering : {len(sort_artlist)}')
    return sort_artlist


if __name__ == "__main__":
    main(sys.argv)
