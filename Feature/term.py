#add terms to Term collection
# Term{
# 	"date":date,
# 	"day_range":day_range
# 	"term":"",
# 	"articles":[],
# 	"group":{[
# 		"id":0,
# 		"df_group":0, word在這個group中top30article的出現次數
# 	]},
# 	"tf":0
#   "df":0
from pymongo import MongoClient
import jieba
import jieba.posseg as pseg
import sys

date = "2018-09-18"
day_range = 1
def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]  
    return stopwords

jieba.load_userdict("userdict.txt")
stopwords = stopwordslist("stopword.txt")
for group in db.finalGroup.find({"date":date,"day_range":day_range}): #for each group
	print("group:",group["group_id"])
	for article_id in group["top30"]: #for each article in each group
		print(article_id)
		article = db.Article.find_one({"id":article_id})
		content = article["Content"].replace('\n','')
		words = pseg.cut(content)
		for word,tag in words: #for each word in that article
			if word not in stopwords and len(word) > 1:
			#if word is a noun
				if tag=="nz" or tag=="nt" or tag=="ns" or tag=="nrt" or tag=="nrfg" or tag=="nr" or tag=="ng" or tag=="n":
					
					if db.Term.find_one({"term":word,"date":date,"day_range":day_range}) != None: #if word in db
						print(word,"exists in db")
						#if the word has appeared in this group already
						if db.Term.find_one({"term":word,"group.id":group["group_id"],"date":date,"day_range":day_range}) != None: 
							print(word,"appeared in",group["group_id"])
							if db.Term.find_one({"term":word,"date":date,"day_range":day_range,"group.id":group["group_id"],"articles":article_id}) != None:
								#tf+1
								db.Term.update(
						 		 	{"term": word,"date":date,"day_range":day_range},
						 		 	{"$inc":{"tf":1}})
								print("tf+1",word)
							else:
								#df_group+1, push article id 
								db.Term.update(
									{"term":word,"group.id":group["group_id"],"date":date,"day_range":day_range},
									{"$push":{"articles":article_id},"$inc":{"group.$.df_group":1,"tf":1,"df":1}})
								print("df+1",group["group_id"],word,tag)
						else: #no group field
						#if the word has appeared in other groups
							db.Term.update({"term":word,"date":date,"day_range":day_range},
								{"$inc":{"tf": 1, "df":1} ,"$push":{"group":{"id":group["group_id"],"df_group":1}}})
							print("new group",group["group_id"],word,tag)
					else: #if word doesnt exist in db at all
						db.Term.insert({
							"date":date, 
							"day_range":day_range,
							"term":word,
							"articles":[article_id],
							"group":[{"id":group["group_id"],"df_group":1}],
							"tf":1,"df":1})
						print("first", word, tag)

