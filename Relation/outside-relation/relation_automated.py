import sys, os
import datetime
from pymongo import MongoClient
import subprocess
import json
import updateGroup

MODE='normal'
SLMargs=['1','1','3','10','10','0','1']
# modularity_function	Modularity function (1 = standard; 2 = alternative)
# resolution_parameter	Value of the resolution parameter
# optimization_algorithm	Algorithm for modularity optimization (1 = original Louvain algorithm; 2 = Louvain algorithm with multilevel refinement; 3 = SLM algorithm)
# n_random_starts	Number of random starts
# n_iterations	Number of iterations per random start
# random_seed	Seed of the random number generator
# print_output	Whether or not to print output to the console (0 = no; 1 = yes)

file_dir = os.path.join(os.path.dirname(__file__), '../../../tempData/outside-relation/')

SLMinputF=file_dir+'SLMinputA'
visualinputF=file_dir+'visualinputA'
SLMoutputF=file_dir+'SLMoutputA'
visualoutputF=file_dir+'community'
mongoInputF=file_dir+"group"

# relation below gate will be ignored and will not be print in the output
GATE=0

HOST='127.0.0.1'
PORT=27020
USERNAME='rootNinja'
DBNAME='test_714'
client=MongoClient()

def usage():
    print("Usage : relation_automated.py <db password> [optional: file_tail_name]")
    sys.exit(1)

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

def createFileNameTail(args):
    global SLMinputF,visualinputF,SLMoutputF,visualoutputF, mongoInputF

    if MODE == 'append':
        name_tail="_"+args[2]+".txt"
        name_tail_json="_"+args[2]+".json"
    elif MODE == 'normal':
        now=datetime.datetime.now()
        name_tail="_{}-{}-{}-{}.txt".format(now.month, now.day, now.hour, now.minute)
        name_tail_json="_{}-{}-{}-{}.json".format(now.month, now.day, now.hour, now.minute)

    SLMinputF=SLMinputF+name_tail
    visualinputF+=name_tail
    SLMoutputF+=name_tail
    visualoutputF+=name_tail_json
    mongoInputF+=name_tail_json

def computeRelation(userA, userB, intersection,db):
    userCollection=db['User']
    A = userCollection.find_one({"id":userA})
    B = userCollection.find_one({"id":userB})
    if A is None or B is None:
        return(-1)
    else:
        messageListA=A['Message']
        messageListB=B['Message']
        union= len(messageListA)+ len(messageListB) - intersection
        if union == 0:
            union = 1
        return(intersection/union)

def finalOutput():
    with open(SLMoutputF,"r") as f1, open(visualinputF,"r") as f2, open(visualoutputF,"a") as f3, open(mongoInputF,"a") as f4:
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
        finalStr="{\"nodes\": [" +nodeStr+ "],\"links\": [" +f2.read()[:-2]+ "]}"
        nodeJson = "["+nodeStr+ "]"
        parsed = json.loads(finalStr)
        parsed_mongo = json.loads(nodeJson)
        # print(json.dumps(parsed,indent=2))
        f3.write(json.dumps(parsed, indent=2))
        f4.write(json.dumps(parsed_mongo, indent=2))

def countRows():
    with open(SLMinputF, "r") as f, open(visualinputF, "r") as f2:
        fline=f.read().split('\n')
        f2line=f2.read().split('\n')
        if len(fline) != len(f2line):
            print("{} and {} do not have same rows length".format(SLMinputF,visualinputF))
            exit(1)
        nrows=len(fline)
        print("append mode : start from {}".format(str(nrows)))
        # exit(1)
        return(nrows)

def iterateRelation(relationCollection, relationSkip, db):
    relationCount = relationCollection.count()
    doneCount = relationSkip
    print("Processing the relations...")
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

def main(args):
    
    if len(args) == 3:
        global MODE
        MODE='append'
    elif len(args) != 2:
        usage()
    createFileNameTail(args)

    client=MongoClient(host=HOST,port=PORT,username=USERNAME,password=args[1])
    db=client[DBNAME]
    relationCollection=db['Relation']
    
    relationSkip=0
    if MODE == 'append':
        relationSkip=countRows()-1

    iterateRelation(relationCollection, relationSkip, db)

    p =subprocess.Popen(['java','-jar','../ModularityOptimizer.jar', SLMinputF, SLMoutputF]+SLMargs)
    returnCode=p.wait()

    if returnCode != 0:
        exit(1)
    else:
        finalOutput()
    
    updateGroup.main(mongoInputF, DBNAME, args[1])

if __name__ == "__main__":
    main(sys.argv)