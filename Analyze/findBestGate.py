import sys
import os
import random
import datetime
import numpy as np
import pandas as pd
from datetime import timedelta
from pymongo import MongoClient

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "gateSimulation")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def validArticle(articleList, date, day_range):
    validList = []
    end_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=int(day_range))
    for item in articleList:
        item_date = datetime.datetime.strptime(item["art_time"], "%Y-%m-%d")
        if (item_date <= end_date) and (item_date >= start_date):
            validList.append(int(item["art_id"]))
    
    return validList

def validUserList(user, day_range, date):
    end_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=int(day_range))
    messageList = user["Message"]
    validMessageList = []
    for message in messageList:
        if message == '':
            continue
        # if re.match(r"\d+/\d+ \d{1,2}:\d{2}", message["Time"]):
        try:
            message_date = datetime.datetime.strptime(message["Time"], "%m/%d %H:%M").replace(year = end_date.year)
            if (message_date <= end_date) and (message_date >= start_date):
                # print(message_date, start_date, end_date)
                validMessageList.append(message)
        except ValueError:
            continue
    
    articleList = user["Article"]
    validArticleList = validArticle(articleList, date, day_range)

    return (len(validMessageList) + len(validArticleList))

def computeRelation(userA, userB, intersection, userCollection, day_range, date):
    A = userCollection.find_one({"id":userA})
    B = userCollection.find_one({"id":userB})
    if A is None or B is None:
        return(-1)
    else:

        listA_len = validUserList(A, day_range, date)
        listB_len = validUserList(B, day_range, date)
        union= listA_len + listB_len - intersection
        # if union == 0:
        #     union = 1
        return(intersection/union)

def simulationAnalyze(date, day_range, sample_size, relationCollection, userCollection):
    # Randomly select the sample
    relationCollection_size = relationCollection.count()
    random_range = int((relationCollection_size - sample_size)*3/4)
    random_jump = random.randint(1, random_range)
    print("Random jump: {}".format(str(random_jump)))

    cursor = relationCollection.find(skip=random_jump, no_cursor_timeout=True, batch_size=30)
    done_relation = 0
    intersection_list = []
    relation_list = []
    for relation in cursor:
        if done_relation == sample_size:
            break

        intersectionList = validArticle(relation["Articleid"], date, day_range)
        intersection_value = len(intersectionList)
        if intersection_value == 0:
            relation_value = 0
        else:
            relation_value = computeRelation(relation['user1id'], relation['user2id'], intersection_value, userCollection, day_range, date)
        
        intersection_list.append(intersection_value)
        relation_list.append(relation_value)

        done_relation += 1
        print("Done sample: {}".format(str(done_relation)), end = '\r')
    
    tmpDict = {"intersection":intersection_list, "relation":relation_list}
    output_df = pd.DataFrame(tmpDict)
    output_df.to_csv(os.path.join(OUTPUT_DIR, "{}_{}_{}".format(date, day_range, sample_size)))

if __name__ == "__main__":

    HOST='140.112.107.203'
    PORT=27020
    USERNAME='rootNinja'
    DBNAME='CrawlGossiping_formal'
    client=MongoClient()

    client=MongoClient(host=HOST,port=PORT,username=USERNAME,password="swordtight")
    db=client[DBNAME]
    relationCollection= db["Relation"]
    userCollection = db["User"]

    simulationAnalyze("2018-09-20", 1, 100, relationCollection, userCollection)