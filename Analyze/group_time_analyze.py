import sys
from pymongo import MongoClient
import requests
import re

HOST='140.112.107.203'
PORT=27020
USERNAME='rootNinja'
DBNAME='CrawlGossiping_formal'
client=MongoClient(host=HOST,port=PORT,username=USERNAME,password="swordtight")

db=client[DBNAME]
groupCollection = db["Group"]
visualCollection = db["Visualization"]

overall_time =[
    ("2018-09-16", 6, 15),
    ("2018-09-23", 5, 15),
    ("2018-09-30", 5, 10),
    ("2018-10-07", 4, 10),
    ("2018-10-14", 5, 15),
    ("2018-10-21", 4, 15),
    ("2018-10-28", 3, 15)
]

def printUsers(date, day_range, group, gate):
    userList = []
    pipeline = [
        {
            "$match":{
                "date":date,
                "day_range":day_range,
                "inter_gate":15
            }
        },
        {
            "$project":{
                "group_list":"$overall_group_list"
            }
        },
        {
            "$unwind":"$group_list"
        },
        {
            "$match":{
                "group_list.overall_group_id":group
            }
        },
        {
            "$project":{
                "user_list":"$group_list.overall_group_users"
            }
        }
    ]
    for result in groupCollection.aggregate(pipeline):
        userList = result["user_list"]

    return(set(userList))

def whichGroup(userid, date, day_range, inter_gate):
    pipeline = [
        {
            "$match":{
                "date":date,
                "day_range":day_range,
                "inter_gate":inter_gate
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
                "nodes.id":userid
            }
        }
    ]

    for result in visualCollection.aggregate(pipeline):
        return(result)

if __name__ == "__main__":
    time_list = list()

    for week in overall_time:
        tmp = set()
        for i in range(1, week[1]+1):
            s = printUsers(week[0], 7, i, week[2])
            tmp = tmp.union(s)
        time_list.append(tmp)

    r = time_list[0]
    for s in time_list:
        r = r.intersection(s)
    
    print(r)
    print(len(r))

    for userId in r:
        for week in overall_time:
            group = whichGroup(userId, week[0], 7, week[2])
            print(group)
        break





    # a = printUsers("2018-09-16", 7, 5, 15)
    # b = printUsers("2018-09-23", 7, 5, 15)
    # c = printUsers("2018-09-30", 7, 5, 10)
    # d = printUsers("2018-10-07", 7, 1, 10)
    # e = printUsers("2018-10-14", 7, 5, 15)
    # f = printUsers("2018-10-21", 7, 3, 15)
    # g = printUsers("2018-10-28", 7, 5, 15)
    # print(len(e))
    # print(len(d))
    # print(len(c.intersection(d)))
    # print(b)
    # print(c)
    # print(d)
