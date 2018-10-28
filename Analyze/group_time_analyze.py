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

def printUsers(date, day_range, group):
    userList = []
    pipeline = [
        {
            "$match":{
                "date":date,
                "day_range":day_range
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

if __name__ == "__main__":
    a = printUsers("2018-09-18", 7, 5)
    b = printUsers("2018-09-30", 7, 5)
    c = printUsers("2018-10-14", 7, 5)
    d = printUsers("2018-10-21", 7, 3)
    print(len(c))
    print(len(d))
    print(len(c.intersection(d)))
    # print(b)
    # print(c)
    # print(d)
