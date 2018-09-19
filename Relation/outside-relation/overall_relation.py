import sys, os
import datetime
from datetime import timedelta
from pymongo import MongoClient
import subprocess
import json

SLMargs=['1','1','3','10','10','0','1']
# modularity_function	Modularity function (1 = standard; 2 = alternative)
# resolution_parameter	Value of the resolution parameter
# optimization_algorithm	Algorithm for modularity optimization (1 = original Louvain algorithm; 2 = Louvain algorithm with multilevel refinement; 3 = SLM algorithm)
# n_random_starts	Number of random starts
# n_iterations	Number of iterations per random start
# random_seed	Seed of the random number generator
# print_output	Whether or not to print output to the console (0 = no; 1 = yes)

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


def update_progress(progress):
    barLength = 30 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

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

def validArticle(articleList, date, day_range):
    validList = []
    end_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=day_range)
    for item in articleList:
        item_date = datetime.datetime.strptime(item[1], "%Y-%m-%d")
        if (item_date < end_date) and (item_date > start_date):
            validList.append(item)
    
    return validList

def validUserList(user, day_range, date):
    end_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=day_range)
    messageList = user["Message"]
    validMessageList = []
    for message in messageList:
        message_date = datetime.datetime.strptime(message["Time"], "%m/%d %H:%M")
        if (message_date < end_date) and (message > start_date):
            validMessageList.append(message)
    
    articleList = user["Article"]
    validArticleList = validArticle(articleList, date, day_range)

    return validMessageList + validArticleList


def computeRelation(userA, userB, intersection,db, day_range, date):
    userCollection=db['User']
    A = userCollection.find_one({"id":userA})
    B = userCollection.find_one({"id":userB})
    if A is None or B is None:
        return(-1)
    else:
        listA = validUserList(A, day_range, date)
        listB = validUserList(B, day_range, date)
        union= len(listA)+ len(listB) - intersection
        if union == 0:
            union = 1
        return(intersection/union)


def iterateRelation(relationCollection, relationSkip, db, day_range, date):
    relationCount = relationCollection.count()
    doneCount = relationSkip
    print("Processing the relations...")

    with open(SLMinputF, "a+") as f, open(visualinputF, "a+") as f2:
        
        for doc in relationCollection.find(skip=relationSkip, no_cursor_timeout=True, batch_size=30):
            userA=doc['user1id']
            userB=doc['user2id']
            intersectionList = validArticle(doc['ArticleId'], date, day_range)
            relation=computeRelation(userA,userB, len(intersectionList), db, day_range, date)
            if relation >= GATE:
                f.write('{}\t{}\t{}\n'.format(userA, userB, relation))
                visualinputLine="\"source\": {}, \"target\": {},\"weight\" : {}".format(userA,userB,relation)
                f2.write("{"+visualinputLine+"},\n")
            doneCount += 1
            update_progress(doneCount/relationCount)
            # print("{}\t{}\t{}".format(userA,userB,relation))

def finalOutput(date, db):
    with open(SLMoutputF,"r") as f1, open(visualinputF,"r") as f2, open(mongoInputF,"a") as f4:
        SLMline=f1.read().split('\n')
        idCount=0
        nodeStr=''
        for line in SLMline:
            if line == '':
                break
            nodesLine='{\"id\" : '+str(idCount)+', \"group\": '+line+'},'
            nodeStr+=nodesLine
            idCount+=1
        nodeStr=nodeStr[:-1]
        finalStr="{\"date\":"+date+",\"nodes\": [" +nodeStr+ "],\"links\": [" +f2.read()[:-2]+ "]}"
        nodeJson = "["+nodeStr+ "]"
        parsed = json.loads(finalStr)
        parsed_mongo = json.loads(nodeJson)
        visualCollection = db["Visualization"]
        visualCollection.insert_one(parsed)
        # open(visualoutputF,"a") as f3
        # f3.write(json.dumps(parsed, indent=2))
        f4.write(json.dumps(parsed_mongo, indent=2))

# get group from group.txt
def group_reconstruct(oldSLMoutputF, date):
    group_document = dict()
    group_ids= []
    groups = []
    with open (oldSLMoutputF) as data:
        group_info = json.loads(data.read())
        for info in group_info:
            if info['group'] not in group_ids:
                group_ids.append(info['group'])
                groups.append({'overall_group_users':[info['id']], 'overall_group_id': info['group'] })
            else:
                for group in groups:
                    if group['id'] == info['group']:
                        group['overall_group_users'].append(info['id'])
        
        group_ids.sort()

        group_document = {
            "date":date,
            "overall_groupID_list":group_ids,
            "overall_group_list":groups
        }

    print('groups reconstruction finished')
    return group_document

def updateGroup(fileName, date, db):
    group_document = group_reconstruct(fileName, date)
    groupCollection = db['Group']
    groupCollection.insert_one(group_document)


def main(dbPassword, date, day_range = 7, append=False):
    createFileNameTail(date, append)
    
    client=MongoClient(host=HOST,port=PORT,username=USERNAME,password=dbPassword)
    db=client[DBNAME]
    relationCollection=db['Relation']
    relationSkip=0
    
    if append is True:
        if countRows() is not False:
            relationSkip = countRows() - 1
    # if there is already a file for that day, delete it
    else:
        if os.path.isfile(SLMinputF):
            os.remove(SLMinputF)
        if os.path.isfile(visualinputF):
            os.remove(visualinputF)
    
    iterateRelation(relationCollection, relationSkip, db, day_range, date)
    # client.close()

    p =subprocess.Popen(['java','-jar', os.path.dirname(__file__)+'../ModularityOptimizer.jar', SLMinputF, SLMoutputF]+SLMargs)
    returnCode = p.wait()

    if returnCode != 0:
        print("SLM process error")
        exit(1)
    else:
        finalOutput(date, db)

    updateGroup(mongoInputF, date, db)

if __name__ == "__main__":
    main(dbPassword=sys.argv[1], date=sys.argv[2], append=sys.argv[3])