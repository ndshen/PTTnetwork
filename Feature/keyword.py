#add terms to Term collection
#Term{
#	"date":date,
#	"day_range":day_range
#	"term":"",
#	"articles":[],
#	"group":{[
#		"id":0,
#		"df_group":0, word在這個group中top30article的出現次數
#	]},
#	"tf":0
#   "df":0
from pymongo import MongoClient
import jieba
import jieba.posseg as pseg
import sys
client = MongoClient(host="127.0.0.1",port=27020,username="rootNinja",password="swordtight")
db=client.CrawlGossiping_formal

date = sys.argv[1]
day_range = int(sys.argv[2])
official = int(sys.argv[3])
inter_gate = int(sys.argv[4])

def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]  
    return stopwords

jieba.load_userdict("userdict.txt")
stopwords = stopwordslist("stopword.txt")
group_count =  db.finalGroup.find({"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate}).count()
for group in db.finalGroup.find({"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate}): #for each group
	print("group:",group["group_id"])
	if group["group_id"] != 0:
		for article_id in group["top30"]: #for each article in each group
			print(article_id)
			article_exist = []
			for i in range(0,group_count+1):
				article_exist.append([])
			article = db.Article.find_one({"id":article_id})
			content = article["Content"].replace('\n','')
			words = pseg.cut(content)
			for word,tag in words: #for each word in that article
				if word not in stopwords and len(word) > 1:
				#if word is a noun
					if tag=="nz" or tag=="nt" or tag=="ns" or tag=="nrt" or tag=="nrfg" or tag=="nr" or tag=="n":

						if db.Term.find_one({"term":word,"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate}) != None: #if word in db
							print(word,"exists in db")
							#if it's the first time the word appears in this article 
							
							#if the word has appeared in this group already
							if db.Term.find_one({"term":word,"group.id":group["group_id"],"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate}) != None: 
								print(word,"appeared in",group["group_id"])
								if word in article_exist[group["group_id"]]:
									#tf+1
									db.Term.update(
										{"term": word,"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate},
										{"$inc":{"tf":1}})
									print("tf+1",article_id, word)
								else:
									#df_group+1, push article id 
									db.Term.update(
										{"term":word,"group.id":group["group_id"],"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate},
										{"$push":{"articles":article_id},"$inc":{"group.$.df_group":1,"tf":1,"df":1}})
									article_exist[group["group_id"]].append(word)
									print("df+1",group["group_id"],article_id, word,tag)
							else: #no group field
							#if word appeared in other groups
								
								db.Term.update({"term":word,"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate},
									{"$inc":{"tf": 1} ,"$push":{"group":{"id":group["group_id"],"df_group":1}}})
								article_exist[group["group_id"]].append(word)
								print("new group",group["group_id"],article_id, word,tag)
						else: #if word doesnt exist in db at all
							db.Term.insert({
								"date":date, 
								"day_range":day_range,
								"official":official,
								"inter_gate":inter_gate,
								"term":word,
								"articles":[article_id],
								"group":[{"id":group["group_id"],"df_group":1}],
								"tf":1,"df":1})
							article_exist[group["group_id"]].append(word)
							print("first",article_id, word, tag)

