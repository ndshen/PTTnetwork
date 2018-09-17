from pymongo import MongoClient
client = MongoClient('localhost')
print(client)
db=client.Crawl
db.Crawl.count()
collection=db["User"]
Users={}
Users["name"]={}
Users["article"]={}
Users["messenge"]={}
collection.insert(Users)
print(Users)