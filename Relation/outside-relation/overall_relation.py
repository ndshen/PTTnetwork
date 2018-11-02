import sys, os
import datetime, time
from datetime import timedelta
from pymongo import MongoClient
import subprocess
import json
import re

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
SLMinput_mapped=data_file_dir+'SLMinput_mapped'
visualinputF=data_file_dir+'visualinput'
SLMoutputF=data_file_dir+'SLMoutput'
visualoutputF=data_file_dir+'community'
mongoInputF=data_file_dir+"group"

# relation below gate will be ignored and will not be print in the output
GATE=0.01
INTER_GATE = 10

OFFICIAL = 0

HOST='127.0.0.1'
PORT=27020
USERNAME='rootNinja'
DBNAME='CrawlGossiping_formal'
client=MongoClient()

total_article = set()

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

def createFileNameTail(date, day_range):
    global SLMinputF, SLMinput_mapped, visualinputF,SLMoutputF,visualoutputF, mongoInputF

    name_tail="_"+date+"_"+str(day_range)+"_"+str(INTER_GATE)+".txt"
    name_tail_json="_"+date+"_"+str(day_range)+"_"+str(INTER_GATE)+".json"

    SLMinputF=SLMinputF+name_tail
    SLMinput_mapped=SLMinput_mapped+name_tail
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


def computeRelation(userA, userB, intersection,db, day_range, date):
    userCollection=db['User']
    # mongo_find_start = time.time()
    A = userCollection.find_one({"id":userA})
    B = userCollection.find_one({"id":userB})
    # print(time.time() - mongo_find_start)
    if A is None or B is None:
        return(-1)
    else:

        listA_len = validUserList(A, day_range, date)
        listB_len = validUserList(B, day_range, date)
        union= listA_len + listB_len - intersection
        if union == 0:
            union = 1
        return(intersection/union)


def iterateRelation(relationCollection, relationSkip, db, day_range, date):
    # relationCount = relationCollection.count()
    total_user = set()
    minimal_intersection = INTER_GATE
    # if day_range <= 4:
    #     minimal_intersection = 5
    # else:
    #     minimal_intersection = 10

    valid_date_range = []
    for i in range(day_range):
        d = datetime.datetime.strptime(date, "%Y-%m-%d")
        valid_date_range.append((d-datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
    
    global total_article
    doneCount = relationSkip
    cursor = relationCollection.find({"Articleid":{"$elemMatch":{"art_time":{"$in":valid_date_range}}}}, skip=relationSkip, no_cursor_timeout=True, batch_size=30)
    # print("Cursor Count: "+str(cursor.count()))
    print(valid_date_range)
    print("Processing the relations...")
    with open(SLMinputF, "a+") as f, open(visualinputF, "a+") as f2:
        
        for doc in cursor:
            intersectionList = validArticle(doc['Articleid'], date, day_range)
            if len(intersectionList) < minimal_intersection:
                doneCount += 1
                print("Done Relation: {}".format(doneCount), end="\r")
                continue
            # start_relation_time = time.time()
            total_article = total_article.union(set(intersectionList))
            userA=doc['user1id']
            userB=doc['user2id']
            relation=computeRelation(userA,userB, len(intersectionList), db, day_range, date)
            if relation > GATE:
                f.write('{}\t{}\t{}\n'.format(userA, userB, relation))
                visualinputLine="\"source\": {}, \"target\": {},\"weight\" : {}".format(userA,userB,relation)
                f2.write("{"+visualinputLine+"},\n")
                total_user.add(str(userA))
                total_user.add(str(userB))

            doneCount += 1
            # print("End of one Relation", time.time()- start_relation_time)
            print("Done Relation: {}".format(doneCount), end="\r")
            # update_progress(doneCount/cursor.count())
            # print("{}\t{}\t{}".format(userA,userB,relation))
    return(list(total_user))

def mapSLMinput(total_user_list):

    with open(SLMinputF, "r") as f, open(SLMinput_mapped, "w") as f2:
        lines = f.read().split('\n')
        for line in lines:
            if line == '':
                continue
            nodes = line.split('\t')
            f2.write("{}\t{}\t{}\n".format(total_user_list.index(nodes[0]), total_user_list.index(nodes[1]), nodes[2]))

def finalOutput(date, day_range, db, total_user_list):
    with open(SLMoutputF,"r") as f1, open(visualinputF,"r") as f2, open(mongoInputF,"a") as f4:
        SLMline=f1.read().split('\n')
        idCount=0
        nodeStr=''
        for line in SLMline:
            if line == '':
                break
            nodesLine='{\"id\" : '+total_user_list[idCount]+', \"group\": '+line+'},'
            nodeStr+=nodesLine
            idCount+=1
        nodeStr=nodeStr[:-1]

        finalStr="{\"date\":\""+date+"\",\"day_range\":"+str(day_range)+",\"inter_gate\":"+str(INTER_GATE)+",\"nodes\": [" +nodeStr+ "],\"links\": [" +f2.read()[:-2]+ "]}"
        nodeJson = "["+nodeStr+ "]"
        parsed = json.loads(finalStr)
        parsed_mongo = json.loads(nodeJson)
        visualCollection = db["Visualization"]
        visualCollection.insert_one(parsed)
        # open(visualoutputF,"a") as f3
        # f3.write(json.dumps(parsed, indent=2))
        f4.write(json.dumps(parsed_mongo, indent=2))

# get group from group.txt
def group_reconstruct(oldSLMoutputF, date, day_range,total_user_list):
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
                    if group['overall_group_id'] == info['group']:
                        group['overall_group_users'].append(info['id'])
                        break
        
        global total_article
        group_ids.sort()
        users = list(map(int, total_user_list))
        users.sort()
        group_document = {
            "date":date,
            "day_range":day_range,
            "relation_gate":GATE,
            "inter_gate":INTER_GATE,
            "official":OFFICIAL,
            "overall_groupArticle_list":list(total_article),
            "overall_groupUser_list": users,
            "overall_groupID_list":group_ids,
            "overall_group_list":groups
        }

    print('groups reconstruction finished')
    return group_document

def updateGroup(fileName, date, day_range, db, total_user_list):
    group_document = group_reconstruct(fileName, date, day_range, total_user_list)
    groupCollection = db['Group']
    groupCollection.insert_one(group_document)


def main(dbPassword, date, day_range = 7, append=False):

    s = datetime.datetime.now()

    createFileNameTail(date, day_range)
    
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
        if os.path.isfile(SLMoutputF):
            os.remove(SLMoutputF)
        if os.path.isfile(mongoInputF):
            os.remove(mongoInputF)
    
    total_user_list = iterateRelation(relationCollection, relationSkip, db, day_range, date)
    mapSLMinput(total_user_list)

    p =subprocess.Popen(['java','-jar', os.path.dirname(__file__)+'/../ModularityOptimizer.jar', SLMinput_mapped, SLMoutputF]+SLMargs)
    returnCode = p.wait()

    if returnCode != 0:
        print("SLM process error")
        exit(1)
    else:
        finalOutput(date, day_range,db, total_user_list)

    updateGroup(mongoInputF, date, day_range, db, total_user_list)

    e = datetime.datetime.now()
    print("Finished, spent: ", e-s)

if __name__ == "__main__":
    # print(os.path.dirname(__file__))
    if len(sys.argv) == 4:
        main(dbPassword=sys.argv[1], date=sys.argv[2], day_range= int(sys.argv[3]))
    elif len(sys.argv) ==5:
        main(dbPassword=sys.argv[1], date=sys.argv[2], day_range= int(sys.argv[3]) ,append=True)
    # python .\Relation\outside-relation\overall_relation.py swordtight 2018-09-20 1