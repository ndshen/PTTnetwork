import sys
import os
import re
import random
import datetime
import numpy as np
import pandas as pd
from datetime import timedelta
from pymongo import MongoClient

def link_node_relation(visualCollection):
    for doc in visualCollection.find():
        print("day_range: {}, node_len: {}, link_len: {}".format(doc["day_range"], len(doc["nodes"]), len(doc["links"])))

if __name__ == "__main__":

    HOST='127.0.0.1'
    PORT=27020
    USERNAME='rootNinja'
    DBNAME='CrawlGossiping_formal'
    client=MongoClient()

    client=MongoClient(host=HOST,port=PORT,username=USERNAME,password="swordtight")
    db=client[DBNAME]
    visualCollection = db["Visualization"]
    link_node_relation(visualCollection)