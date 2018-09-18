import sys, os
import datetime
from pymongo import MongoClient
import subprocess
import json
import updateGroup

data_file_dir = os.path.join(os.path.dirname(__file__), '../../../tempData/outside-relation/')

SLMinputF=data_file_dir+'SLMinput'
visualinputF=data_file_dir+'visualinput'
SLMoutputF=data_file_dir+'SLMoutput'
visualoutputF=data_file_dir+'community'
mongoInputF=data_file_dir+"group"

# relation below gate will be ignored and will not be print in the output
GATE=0

HOST='127.0.0.1'
PORT=27020
USERNAME='rootNinja'
DBNAME='test_714'
client=MongoClient()


def createFileNameTail(date, append):
    global SLMinputF,visualinputF,SLMoutputF,visualoutputF, mongoInputF

    if append is True:
        name_tail="_"+date+".txt"
        name_tail_json="_"+date+".json"
    else:
        now=datetime.datetime.now()
        name_tail="_{}-{}-{}.txt".format(now.year, now.month, now.day)
        name_tail_json="_{}-{}-{}.json".format(now.year, now.month, now.day)

    SLMinputF=SLMinputF+name_tail
    visualinputF+=name_tail
    SLMoutputF+=name_tail
    visualoutputF+=name_tail_json
    mongoInputF+=name_tail_json

def countRows():
    with open(SLMinputF, "r") as f, open(visualinputF, "r") as f2:
        fline=f.read().split('\n')
        f2line=f2.read().split('\n')
        if len(fline) != len(f2line):
            print("{} and {} do not have same rows length".format(SLMinputF,visualinputF))
            return(False)
        nrows=len(fline)
        print("append mode : start from {}".format(str(nrows)))
        # exit(1)
        return(nrows)

def iterateRelation(relationCollection, relationSkip, db):
    relationCount = relationCollection.count()
    doneCount = relationSkip
    print("Processing the relations...")

    if relationSkip

    with open(SLMinputF, "a+") as f, open(visualinputF, "a+") as f2:
        
        for doc in relationCollection.find(skip=relationSkip, no_cursor_timeout=True):
            userA=doc['user1id']
            userB=doc['user2id']
            intersection=doc['Intersection']
            relation=computeRelation(userA,userB,intersection,db)
            if relation >= GATE:
                f.write('{}\t{}\t{}\n'.format(userA, userB, relation))
                visualinputLine="\"source\": {}, \"target\": {},\"weight\" : {}".format(userA,userB,relation)
                f2.write("{"+visualinputLine+"},\n")
            doneCount += 1
            update_progress(doneCount/relationCount)
            # print("{}\t{}\t{}".format(userA,userB,relation))

def main(dbPassword, date, day_range = 7, append=False):
    createFileNameTail(date, append)
    
    client=MongoClient(host=HOST,port=PORT,username=USERNAME,password=args[1])
    db=client[DBNAME]
    relationCollection=db['Relation']

    relationSkip=0
    if append is True:
        if countRows() is not False:
            relationSkip = countRows() - 1
    else:
        if os.existsssss
    
    


if __name__ == "__main__":
    main(dbPassword=sys.argv[1], date=sys.argv[2], append=sys.argv[3])