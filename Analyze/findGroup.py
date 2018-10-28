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
userCollection= db["User"]
visualCollection = db["Visualization"]

group_user_dict = dict()
user_name_set = set()

def findIdbyName(name):
    user = userCollection.find_one({"Name":name})
    if user == None:
        # print("this user not in database")
        return(None)
    return(user["id"])

def findUserGroup(name, date, day_range):
    userName = name
    userID = findIdbyName(name)
    if userID is None:
        return(False)

    pipeline = [
        {
            "$match":{
                "date":date,
                "day_range":day_range
            }
        },
        {
            "$project":{
                "_id":0,
                "nodes":1
            }
        },
        {
            "$unwind":"$nodes"
        },
        {
            "$match":{
                "nodes.id":userID
            }
        }
    ]

    for result in visualCollection.aggregate(pipeline):
        print(result["nodes"])
        if result["nodes"]["group"] not in group_user_dict:
            group_user_dict[result["nodes"]["group"]] = 1
        else:
            group_user_dict[result["nodes"]["group"]] += 1

    # print("===============")

def analyze_article_group(date, day_range):
    name_list = []
    with open("comments.txt", "r", encoding = 'utf8') as f:
        lines = f.read().split('\n')
        for line in lines:
            if line == "":
                continue
            head = line.split(':')[0]
            name = re.match(r".* (\w+)", head)
            if name is not None:
                name_list.append(name.group(1))
    
    for name in name_list:
        # print(name)
        if name not in user_name_set:
        # if True:
            findUserGroup(name, date, day_range)
            user_name_set.add(name)
        # print(name)

if __name__ == "__main__":
    # findUserGroup(sys.argv[1], DATE, DAY_RANGE)
    analyze_article_group(DATE, DAY_RANGE)
    for entry in sorted(group_user_dict.items(), key=lambda x : x[1], reverse=True):
        print(entry)
        