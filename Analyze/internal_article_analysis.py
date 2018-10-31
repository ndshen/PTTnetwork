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
    # articles = [92899,82047,77254, 79064,85832, 92841, 85625, 80592, 85625]
    # for art in articles:
    #     temp =  db.Article.find_one({'id': art})
    #     print(temp['ArticleName'])
    # sys.exit(1)
    groups = db.Group.find_one({"date" : date_begin, "day_range" : 7, "official" : 1})
    show_art = {}
    for group in groups[ "overall_group_list"]:
        print(f"outside group_id :{group['overall_group_id']}")
        all_res = []

        if not group.get("internal_group_list"):
            continue
        for inner_group in group["internal_group_list"]:
            res = []
            print(f" inner group_id :{inner_group['internal_group_id']}")
            push_list = inner_group['internal_top_articles']['top_push']
            boo_list = inner_group['internal_top_articles']['top_boo']
            leaders = inner_group['internal_group_users']
            res = analysis(push_list, boo_list, leaders, db )
            res['internal_group_id'] = inner_group['internal_group_id']
            all_res.append(res)
        push = {}
        boo = {}
        for i in all_res:
            print(i)
            ids = get_art_id(i['push'])
            for j in ids:
                if j not in push:
                    push[j] = 0 # 0 no relation, 1 same type, 2 oppsite type 
                else:
                    if push[j] == 0:
                        push[j] == 1
                if j in boo:
                    boo[j] = 2
                    push[j] = 2
            ids = get_art_id(i['boo'])
            for j in ids:
                if j not in boo:
                    boo[j] = 0 # 0 no relation, 1 same type, 2 oppsite type 
                else:
                    if boo[j] == 0:
                        boo[j] == 1
                if j in push:
                    boo[j] = 2
                    push[j] = 2
        all_art = boo
        all_art.update(push)
        temp_art = {}
        for key, val in all_art.items():
            temp = {'push': [], 'boo': []}
            if val >= 1:
                for k in all_res:
                    if key in get_art_id(k['push']):
                        temp['push'].append(k['internal_group_id'])
                    if key in get_art_id(k['boo']):
                        temp['boo'].append(k['internal_group_id'])
            temp_art[key] = temp
        show_art[group['overall_group_id']] = temp_art          
    for key, val in show_art.items():
        print(f' group id : {key}')
        for ids, res in val.items():
            if len(res['push']) > 0 and len(res['boo']) > 0:
                art = db.Article.find_one({'id': ids})
                print(art['ArticleName'])
                print(art['URL'])
                print('推:')
                for j in res['push']:
                    print(j)
                print('噓:')
                for j in res['boo']:
                    print(j)



def get_art_id(art):
    return_list = []
    for key, val in art.items():
        return_list.append(key)
    return return_list


def analysis(top_push, top_boo, leaders, db):
    push_dic = {}
    boo_dic = {}
    for user in leaders:
        #print(user)
        leader = db.User.find_one({'id':user})
        cor_art = [o['art_id'] for o in leader['Article']]
        if leader.get('Message') != None:
            cor_mes = [o['ArticleId'] for o in leader.get('Message') if o!= '' ]
        else:
            cor_mes = []
        all_related = set(cor_art + cor_mes)
        #print(leader['Name'])
        #print(f'top_push: {top_push}')
        push_intersection = [i for i in all_related if i in top_push]
        #print(push_intersection)
        for push in push_intersection:
            if push not in push_dic:
                push_dic[push] = 1
            else:
                push_dic[push] += 1
        #print(f'top_boo: {top_boo}')
        boo_intersection = [i for i in all_related if i in top_boo]
        #print(boo_intersection)
        for boo in boo_intersection:
            if boo not in boo_dic:
                boo_dic[boo] = 1
            else:
                boo_dic[boo] += 1
    return {'push':push_dic,'boo':boo_dic}

        
if __name__ == "__main__":
    main(sys.argv)
