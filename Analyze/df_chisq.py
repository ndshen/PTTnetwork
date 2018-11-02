import sys, os
from pymongo import MongoClient
import requests
import re
import math
import numpy as np
import pandas as pd
from collections import defaultdict

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "terms")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

HOST='140.112.107.203'
PORT=27020
USERNAME='rootNinja'
DBNAME='CrawlGossiping_formal'
client=MongoClient(host=HOST,port=PORT,username=USERNAME,password="swordtight")
db=client[DBNAME]

DATE = "2018-09-30"
DAY_RANGE = 7
INTER_GATE = 10
group_num = 6
group_list = [0,1,2,3,4,5]

termCollection = db["Term"]
top30Collection = db["finalGroup"]

df_dict = defaultdict()
group_size_dict = defaultdict()

def findGroupSize():

    for group_id in group_list:
        doc = top30Collection.find_one({"date":DATE, "day_range": DAY_RANGE, "inter_gate":INTER_GATE, "group_id":group_id})
        group_size_dict[group_id] = doc["top30_len"]


def make_excel(date, day_range, inter_gate):
    findGroupSize()

    count = 0
    total_group_size = 0
    for key, value in group_size_dict.items():
        total_group_size += value
    
    for doc in termCollection.find({"date":date, "day_range":day_range, "inter_gate":inter_gate}, no_cursor_timeout=True, batch_size=30):
        df = 0
        for group_term in doc["group"]:
            df += group_term["df_group"]
        for group_term in doc["group"]:
            exp_df = round(df*group_size_dict[group_term["id"]]/total_group_size, 3)
            df_chi = round(math.pow(group_term["df_group"]-exp_df, 2)/exp_df, 3)
            
            df_group = group_term["df_group"]
            if exp_df > df_group:
                df_chi = df_chi*-1
            
            if df_group < 10:
                df_multi_chi = 0
            else:
                df_multi_chi = math.log2(df_group) * df_chi

            data = {
                "term":[doc["term"]],
                "n11_df":[df_group],
                "total_df":[df],
                "total_tf":doc["tf"],
                "exp_df":[exp_df],
                "df_chi": [df_chi],
                "n11*df_chi": [df_multi_chi]
            }

            tmp_df = pd.DataFrame(data)

            if group_term["id"] not in df_dict:
                df_dict[group_term["id"]] = tmp_df
            else:
                df_dict[group_term["id"]] = df_dict[group_term["id"]].append(tmp_df, ignore_index=True)

        count += 1
        print(count, end='\r')
        

    output_file = pd.ExcelWriter(os.path.join( OUTPUT_DIR, "{}_{}_{}.xlsx".format(DATE, DAY_RANGE, INTER_GATE)))
    for key, value in df_dict.items():
        value.to_excel(output_file, str(key))
    output_file.save()

if __name__ == "__main__":
    make_excel(DATE, DAY_RANGE, INTER_GATE)
    # findGroupSize()
    # for key, value in group_size_dict.items():
    #     print(key, value)