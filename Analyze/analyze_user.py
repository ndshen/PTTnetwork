import sys
import os
import re
import random
import datetime
import numpy as np
import pandas as pd
from datetime import timedelta
from pymongo import MongoClient

def analyzeUser(User):
    main_frame = pd.DataFrame()
    for doc in User.find():
        correlaatedUser_count = len(doc["CorrelatedUser"])
        IP_count = len(doc["IPAddress"])
        article_count = len(doc["Article"])
        message_count = len(doc["Message"])
        
        temp_dict = {
            "message":message_count,
            "article":article_count,
            "cor_user":correlaatedUser_count,
            "ip":IP_count
        }
        temp_frame = pd.DataFrame(temp_dict)
        main_frame = main_frame.append(temp_frame, ignore_index=True)

    return(main_frame)


if __name__ == "__main__":
    HOST='127.0.0.1'
    PORT=27020
    USERNAME='rootNinja'
    DBNAME='CrawlGossiping_formal'
    client=MongoClient()

    client=MongoClient(host=HOST,port=PORT,username=USERNAME,password="swordtight")
    db=client[DBNAME]
    userCollection = db["User"]
    main_frame = analyzeUser(userCollection)
    main_frame.to_csv("User_Analyze.csv")