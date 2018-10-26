import sys
import os
import re
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
        if union == 0:
            print("Union is zero Error, userA: {}, userB: {}".format(userA, userB))
            union = 1
        return(intersection/union)

def simulationAnalyze(date, day_range, sample_size, relationCollection, userCollection):
    # Randomly select the sample
    relationCollection_size = relationCollection.count()
    random_range = int((relationCollection_size - sample_size)*1/1000)
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
    output_df.to_csv(os.path.join(OUTPUT_DIR, "{}_{}_{}_{}.csv".format(date, day_range, sample_size, random_jump)))

# 9/11 - 10/20
def simulation(relationCollection, userCollection):
    test_date_list = ["2018-09-25", "2018-09-30", "2018-10-05", "2018-10-10", "2018-10-15", "2018-10-20"]
    for date in test_date_list:
        for i in range(1, 15):
            for j in range(3):
                print("{} {} {}".format(date, i , j+1))
                simulationAnalyze(date, i, 500, relationCollection, userCollection)

def concat_sample_file():
    sample_list = os.listdir(OUTPUT_DIR)
    file_name_re = re.compile(r"(\d{4}-\d{2}-\d{2})_(\d+)_(\d+)_(\d+).csv")
    df_list = []
    for i in range(1, 15):
        main_df = pd.DataFrame()
        for sample_file in sample_list:
            match_object = file_name_re.match(sample_file)
            if match_object is not None:
                if i == int(match_object.group(2)):
                    df = pd.read_csv(os.path.join(OUTPUT_DIR, sample_file), index_col=0)
                    # print(df)
                    main_df = main_df.append(df, ignore_index=True)
        
        df_list.append(main_df)
        # main_df.to_csv("{}-day_result.csv".format(str(i)))

    output_file = pd.ExcelWriter('simulateResult.xlsx')
    for i, df in enumerate(df_list):
        df.to_excel(output_file, str(i+1))
    output_file.save()



if __name__ == "__main__":

    HOST='127.0.0.1'
    PORT=27020
    USERNAME='rootNinja'
    DBNAME='CrawlGossiping_formal'
    client=MongoClient()

    client=MongoClient(host=HOST,port=PORT,username=USERNAME,password="swordtight")
    db=client[DBNAME]
    relationCollection= db["Relation"]
    userCollection = db["User"]

    # simulation(relationCollection, userCollection)
    concat_sample_file()
