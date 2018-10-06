import sys
from pymongo import MongoClient

HOST='140.112.107.203'
PORT=27020
USERNAME='rootNinja'
DBNAME='CrawlGossiping_formal'
client=MongoClient()

DATE = "2018-09-18"
DAY_RANGE = 7

client=MongoClient(host=HOST,port=PORT,username=USERNAME,password="swordtight")
db=client[DBNAME]
userCollection= db["User"]
visualCollection = db["Visualization"]

def findIdbyName(name):
    user = userCollection.find_one({"Name":name})
    if user == None:
        print("this user not in database")
        exit(1)
    return(user["id"])

if __name__ == "__main__":
    userName = sys.argv[1]
    pipeline = [
        {
            "$match":{
                "date":DATE,
                "day_range":DAY_RANGE
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
                "nodes.id":findIdbyName(userName)
            }
        }
    ]
    
    for result in visualCollection.aggregate(pipeline):
        print(result["nodes"])