#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from pymongo import MongoClient
import subprocess
import json
import random
import imp

from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.cluster import KMeans
import numpy as np

date_begin = '2018-10-14'
day_range = 7
date_end = '2018-10-08'

NEG_VAL = -1000
NEG_VAL_2 = -100
INTER_GATE = 15
OFFICIAL = 1
ART_RES_GATE = 10
USER_GATE = 10
RELATION_GATE = 0.1
NEG_RELATION_GATE = -0.1
REDUCE_ART_GATE = 1.2


BEGIN = datetime.strptime(date_begin,('%Y-%m-%d')).date()
END = datetime.strptime(date_end,('%Y-%m-%d')).date()

# relation below gate will be ignored and will not be print in the output
GATE = -100
# get group from SLM output
def group_relation(db):
    groups = db.Group.find_one({
        'date': date_begin, 'day_range': day_range, 'inter_gate': INTER_GATE
    })
    #!!!!! add 
    print('groups reconstruction finished')
    return groups['overall_group_list']


def vectorize(group_id, users, db):
    print('start count group id: %d' % group_id)
    # needd to add inter gate
    group = db.finalGroup.find_one({'group_id': group_id, 'date': date_begin, 'day_range': day_range, 'inter_gate': INTER_GATE})
    if not group:
        print('group ignore')
        return None, None, None
    group_arts = group['top30']
    if not group_arts:
        print('None top30 aritcle')
        return None, None, None
    group_arts = list(set(group_arts))
    group_arts.sort()
    group_arts = reduce_art(group_arts, db)
    length = len(users)
    users_vector = []
    for i in range(length):
        vector = [1 for art in group_arts]
        user = db.User.find_one({'id': users[i]})
        related_art = user['Article'] if user['Article'] else []
        for art in related_art:
            if art['art_id'] not in group_arts:
                continue
            try:
                vector[group_arts.index(art['art_id'])] = 2
            except Exception as e:
                print(e)
                continue
        for mes in user['Message']:
            if mes == '':
                continue
            if mes.get('ArticleId') is None :
                continue
            if mes['ArticleId'] not in group_arts:
                continue
            else:
                if mes['React'] == '推':
                    try:
                        vector[group_arts.index(mes['ArticleId'])] = 2
                    except Exception as e:
                        continue
                elif mes['React']  == '噓':
                    try:
                        vector[group_arts.index(mes['ArticleId'])] = 0
                    except :
                        continue
                else:
                    continue
        length = len(group_arts)
        users_vector.append(vector)
        
    user_group, leaders = cluster(users_vector, users) 
    return user_group, leaders, group_arts


def reduce_art(articles, db):
    length = len(articles)
    len_sum = 0
    art_info = {}
    for i in articles:
        art = db.Article.find_one({'id':i},{'Boo': 1, 'Push': 1, 'Neutral': 1})
        num = len(art['Boo'] + art['Push'] + art['Neutral'])
        art_info[i] = num
        len_sum = len_sum + num
    gate = len_sum / length * REDUCE_ART_GATE 
    print(f'number of art before filtering : {length}')
    print('finished count')
    sort_artlist = []
    for key, val in art_info.items():
        if val >= gate:
            sort_artlist.append(key)
    print(f'number of art after filtering : {len(sort_artlist)}')
    return sort_artlist


def cluster(vector, user_list):
    num_of_cluster = 1
    score_list = []
    diff_list = []
    result = None
    distance = None
    while True:
        users = np.array(vector)
        kmeans = KMeans(n_clusters=num_of_cluster, random_state=None).fit(users)
        score = kmeans.score(users)
        score_list.append(abs(score))
        if num_of_cluster > 1:
            diff_list.append(score_list[num_of_cluster-2]-score_list[num_of_cluster-1])
            if num_of_cluster > 2:
                if  diff_list[num_of_cluster-3]  >  diff_list[num_of_cluster-2] *2.5  or num_of_cluster > 5:
                    num_of_cluster -= 1
                    kmeans = KMeans(n_clusters=num_of_cluster, random_state=None).fit(users) 
                    result = kmeans.labels_
                    distance = kmeans.transform(users)
                    break
        num_of_cluster += 1
    closest_user = [[] for i in range((num_of_cluster))]
    user_group = [[] for i in range((num_of_cluster))]
    for a,p,d in zip(result, user_list, distance):
        user_group[int(a)].append((p, d[int(a)]))
    i = 0
    for data in user_group:
        data.sort(key=takeSecond)
        closest_user[i] = getFirst(data)[:10]
        #print(closest_user[i])
        i += 1

    return (list(result), closest_user)
    

def takeSecond(elem):
    return elem[1]


def getFirst(data):
    result = []
    for a,b in data:
        result.append(a)
    return result




def count_relation(group_id, users, db):
    print('start count group id: %d relation' % group_id)
    length = len(users)
    group = db.finalGroup.find_one({'group_id': group_id, 'date': date_begin, 'day_range': day_range, 'inter_gate': INTER_GATE})
    if not group:
        print('group ignore')
        return 
    group_arts = set(group['top30'])
    if len(group_arts) == 0:
        print('None top30 aritcle')
        return
    relation_list = []

    start_date = datetime.strptime(date_begin,('%Y-%m-%d')).date()
    end_date =datetime.strptime(date_end,('%Y-%m-%d')).date()
    for i in range(length):
        for j in range(i+1, length):
            #intersection
            relation = db.Relation.find_one({'user1id': users[i], 'user2id': users[j]})
            if not relation:
                #print('no intesection between user1id: %d and user2id: %d in group id: %d'% (users[i], users[j], group_id))
                continue
            print('intesection between user1id: %d and user2id: %d in group id: %d '% (users[i], users[j], group_id))
            article_data = relation['Articleid']
            article_list = set()
            
            for art in article_data:
                art_time = datetime.strptime(art['art_time'],('%Y-%m-%d')).date()
                if art_time  > BEGIN or art_time < END:
                    continue
                article_list.add(art['art_id'])
            art_intersection = article_list
            if len(art_intersection) == 0:
                continue
            relation_value = user_perspective(users[i], users[j], art_intersection, db)
            if relation_value < RELATION_GATE and relation_value > NEG_RELATION_GATE:
                continue
            relation = {'source': users[i], 'target': users[j], 'weight': relation_value}
            relation_list.append(relation)
    save_links(group_id, relation_list, db)


def user_perspective(user1, user2, articles, db):
    user1 = db.User.find_one({'id': user1})
    user2 = db.User.find_one({'id': user2})
    denominator = len(articles)
    numerator = 0
    for art in articles:
        user1_react = None
        user2_react = None
        for article in user1['Article']:
            if art == article['art_id']:
                user1_react = 1
                break
        if not user1_react:
            for mes in user1['Message']:
                if mes == "":
                    continue
                if mes.get('ArticleId') == art:
                    if mes['React'] == '推':
                        user1_react = 1
                    elif mes['React'] == '噓':
                        user1_react = -1 
                    break
        for article in user2['Article']:
            if art == article['art_id']:
                user2_react = 1
                break
        if not user2_react:
            for mes in user2['Message']:
                if mes == "":
                    continue
                if mes.get('ArticleId') == art:
                    if mes['React'] == '推':
                        user2_react = 1
                    elif mes['React'] == '噓':
                        user2_react = -1 
                    break
        if user1_react == user2_react:
            numerator += 1
        else:
            numerator -= 1

    return numerator / denominator



def save_links(group_id, relation_list, db):
    # save to db
    group_relation = db.Visualization_inner
    temp_data = group_relation.find_one({'date': date_begin, 'day_range': day_range, 'group_id': group_id, 'inter_gate': INTER_GATE})
    if temp_data is not None:
        group_relation.update_one({'date': date_begin, 'day_range': day_range, 'group_id': group_id, 'inter_gate': INTER_GATE}, {'$addToSet':{
            'links': {'$each': relation_list}
        }})
    else:
        temp_check = group_relation.find({'date': date_begin, 'day_range': day_range})
        flag = 0
        for group in temp_check:
            if not group.get('inter_gate'):
                continue
            if group['inter_gate'] != INTER_GATE and group['official'] == 1:
                flag = 1
                break
        insert_data = {'date': date_begin , 'day_range': day_range, 'group_id': group_id, 'links': relation_list , 'inter_gate': INTER_GATE, 'official': OFFICIAL - flag}
        group_relation.insert(insert_data)
    print('finish insert relation into database: inner group:%d' % group_id)


def save_nodes(group_id, data, db):
    group_relation = db.Visualization_inner
    nodes = []
    for one in data['internal_group_users']:
        node = {'id': one,'group': data['internal_group_id']}
        nodes.append(node)
    temp_data = group_relation.find_one({'date': date_begin, 'day_range': day_range, 'group_id': group_id, 'inter_gate': INTER_GATE})
    if temp_data is not None:
        group_relation.update_one({'date': date_begin, 'day_range': day_range, 'group_id': group_id, 'inter_gate': INTER_GATE}, {'$addToSet':{
            'nodes': {'$each': nodes}
        }})
    else:
        temp_check = group_relation.find({'date': date_begin, 'day_range': day_range})
        flag = 0
        for group in temp_check:
            if not group.get('inter_gate'):
                continue
            if group['inter_gate'] != INTER_GATE and group['official'] == 1:
                flag = 1
                break
        insert_data = {'date': date_begin , 'day_range': day_range, 'group_id':group_id, 'nodes':nodes, 'inter_gate': INTER_GATE, 'official': OFFICIAL-flag }
        group_relation.insert(insert_data)

    print('finish insert relation into database: inner group:%d' % group_id)



def find_top_art(group_arts, users, db):
    length = len(users)
    all_res = [{'push':0, 'boo':0, 'push_state':1, 'boo_state': 1} for art in group_arts]
    for i in range(length):
        user = db.User.find_one({'id': users[i]})
        related_art = user['Article'] if user['Article'] else []
        for art in related_art:
            if art['art_id'] not in group_arts:
                continue
            try:
                all_res [group_arts.index(art['art_id'])]['push'] += 1
            except Exception as e:
                print(e)
                break
                continue
        for mes in user['Message']:
            if mes == '':
                continue
            if mes.get('ArticleId') is None :
                continue
            if mes['ArticleId'] not in group_arts:
                continue
            else:
                if mes['React'] == '推':
                    try:
                        all_res[group_arts.index(mes['ArticleId'])]['push'] += 1
                    except Exception as e:
                        print(e)
                        break
                        continue
                elif mes['React']  == '噓':
                    try:
                        all_res [group_arts.index(mes['ArticleId'])]['boo'] += 1
                    except :
                        print(e)
                        break
                        continue
                else:
                    continue
    boo_list = []
    push_list = []
    for i in range(ART_RES_GATE):
        index = all_res.index(max(all_res, key=getPush))
        if all_res[index]['push_state'] and (all_res[index]['push'] > all_res[index]['boo']):
            push_list.append(group_arts[index])
            all_res[index]['push_state'] = 0
        index = all_res.index(max(all_res, key=getBoo))
        if all_res[index]['boo_state'] and (all_res[index]['boo'] > all_res[index]['push']):
            boo_list.append(group_arts[index])
            all_res[index]['boo_state'] = 0
    return {'top_push':push_list, 'top_boo': boo_list}


def getPush(val):
    if val['push_state'] :
        if val['push'] - val['boo'] > 0:
            return val['push'] - val['boo']
        return NEG_VAL_2
    return NEG_VAL

def getBoo(val):
    if val['boo_state'] ==1:
        if val['boo'] - val['push'] > 0:
            return val['boo'] - val['push']
        return NEG_VAL_2
    return NEG_VAL

def main(args):
    password = args[1]
    client = MongoClient(host="140.112.107.203", port=27020, username="rootNinja", password=password)  #connect to database
    db = client.CrawlGossiping_formal
    # user1 = db.User.find_one({'id': 54}, {'Message': {'$elemMatch':{'Articleid':{'$in':[0,1,2,3,4,5]}}}})
    # print(user1['Message'][0]['Articleid'])
    # sys.exit(1)
    groups = group_relation(db)
    for group in groups:
        if group.get('overall_group_users'):
            # count relation inside one group
            group_id = group['overall_group_id']
            user_list = group['overall_group_users']
            user_list.sort()
            print(len(user_list))
            if len(user_list) < USER_GATE:
                print('skip grouop')
                continue
            user_group, leaders, groups_art = vectorize(group_id, user_list, db)
            if not user_group :
                print('skip grouop')
                continue
            
            print('top push and boo finished')
            group_infos = []
            group_ids = []
            for p, a in zip(user_list, user_group):
                if a not in group_ids:
                    group_ids.append(a)
                    group_infos.append({'internal_group_users':[p], 'internal_group_id': int(a), 'internal_group_leaders': leaders[int(a)] })
                else:
                    for data in group_infos:
                        if data['internal_group_id'] == a:
                            data['internal_group_users'].append(p)
            
            for info in group_infos:
                #group collection
                top_art = find_top_art(groups_art, info['internal_group_users'], db)
                info['internal_top_articles'] = top_art
                db.Group.update(
                    {
                        'date': date_begin, 'day_range' :day_range, 'inter_gate': INTER_GATE,'overall_group_list.overall_group_id':group_id
                    },
                    {
                        '$addToSet': {'overall_group_list.$.internal_group_list': info}
                    }
                )
                # inner_visualization
                # nodes 
                save_nodes(group_id, info, db)
                users = sorted(info['internal_group_users'])
                count_relation(group_id, users, db)
        else:   
            continue
    
    #group_relation()


if __name__ == "__main__":
    main(sys.argv)