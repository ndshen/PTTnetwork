import sys
from pymongo import MongoClient
import requests
import re

HOST='140.112.107.203'
PORT=27020
USERNAME='rootNinja'
DBNAME='CrawlGossiping_formal'
client=MongoClient()

DATE = "2018-10-14"
DAY_RANGE = 7

client=MongoClient(host=HOST,port=PORT,username=USERNAME,password="swordtight")
db=client[DBNAME]
keywordCollection= db["finalGroup"]
termCollection = db["Term"]

def findKeyword(date, day_range, group_id ,inter_gate):

    doc = keywordCollection.find_one({"date":date, "day_range":day_range, "group_id":group_id,"inter_gate":inter_gate})
    result = []
    for keyword in doc["result"]:
        result.append(keyword["keyword"])
    return(result)


def findKeywordArticles(keyword, date, day_range, inter_gate):
    doc = termCollection.find_one({"date":date, "day_range":day_range, "inter_gate":inter_gate, "term":keyword})
    return(set(doc["articles"]))

if __name__ == "__main__":
    date = "2018-10-07"
    day_range = 7
    inter_gate = 15
    group_id = 1
    keyword_list = findKeyword(date, day_range, group_id, inter_gate)
    print(keyword_list)

    union_set_list = []
    term_group_list = []

    for index, term in enumerate(keyword_list):
        art_set = findKeywordArticles(term, date, day_range, inter_gate)
        if index == 0 :
            union_set_list.append(art_set)
            term_group_list.append([term])
        else:
            flag = False
            for i, u_set in enumerate(union_set_list):
                if len(u_set.intersection(art_set))/len(art_set) >= 0.3:
                    union_set_list[i] = u_set.union(art_set)
                    term_group_list[i].append(term)
                    flag = True
                    break
            if flag == False:
                union_set_list.append(art_set)
                term_group_list.append([term])

        print(term, len(art_set))
        if index == 50:
            break
    
    print(term_group_list)
