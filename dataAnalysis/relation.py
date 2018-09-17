import sys
from pymongo import MongoClient

HOST='140.112.107.203'
PORT=27020
USERNAME='rootNinja'
DBNAME='CrawlGossiping'
client=MongoClient()


def usage():
    print("Usage : relation.py <db password>")

def manualAddId(db, userCollection):
    count=0
    for user in userCollection.find():
        db.User.update({'Name':user['Name']},{'$set':{'ID':count}})
        print(user['Name']+'is assigned to ID-'+str(count))
        count+=1

def relations(userA, userB):
    articleSetA=set()
    articleSetB=set()

    listA=userA['Message']
    listB=userB['Message']

    if listA[0] != '':
        for message in listA:
            articleSetA.add(message['ArticleName'])
    if listB[0] != '':
        for message in listB:
            articleSetB.add(message['ArticleName'])
    
    if len(articleSetA)==0 and len(articleSetB) == 0 :
        relationValue=0

    else:

        articleIntersection=articleSetA.intersection(articleSetB)
        articleUnion=articleSetA.union(articleSetB)
        relationValue=len(articleIntersection)/len(articleUnion)

    return relationValue

def allPairs(db, userCollection, output):
    db.User.aggregate([{'$sort':{"id":1}}])
    userArray=userCollection.find()

    for i in range(0,userArray.count()-1):
        for j in range(i+1,userArray.count()):
            userA=userArray[i]
            userB=userArray[j]

            relation=relations(userA, userB)
            
            output.write("\n{}\t{}\t{}".format(userA["id"],userB["id"],relation))
            print("{}\t{}\t{}".format(userA["id"],userB["id"],relation))


            j=j+1

        i=i+1


    

def main(args):

    if len(args) != 2:
        usage()
        sys.exit(1)

    client=MongoClient(host=HOST,port=PORT,username=USERNAME,password=args[1])
    db=client[DBNAME]
    userCollection=db['User']

    with open('relationAnalysis.txt',"a") as output:
        # manualAddId(db, userCollection)

        allPairs(db, userCollection, output)


if __name__ == '__main__' :
    main(sys.argv)