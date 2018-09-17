
from pymongo import MongoClient
import math
import jieba
client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja")
db=client.test_624
#Keyword{
#	"keyword":"",
#	"articles":[],
#	"group":{[
#		"id":0,
#		"df_group":0, word在這個group中top30article的出現次數
#		"df_other":0, 在所有其他group中top30article出現次數
#		"df_pop":0 在這個group中所有文章的出現次數
#	]},
#	"tf":0
#}
N = 0
for group in db.Feature.find(): #for each group
	print("group:",group["group"])
	N += group["top30_len"]
	for article_id in group["top30"]: #for each article in each group
		print(article_id)
		article = db.Article.find_one({"id":article_id})
		words = jieba.cut(article["Content"], cut_all=False)
		for word in words: #for each word in that article
			df_other = 0
			if db.Keyword.find({"keyword":word}).count() != 0: #if word in db
				key = db.Keyword.find_one({"keyword":word})
				#if the word has appeared in this group already
				if db.Keyword.find({"keyword":word,"group.id":group["group"]}).count()!=0: 
					if db.Keyword.find({"keyword":word,"group.id":group["group"],"articles":article_id}).count()!=0:
						#tf+1
						db.Keyword.update(
				 		 	{"keyword": word},
				 		 	{"$inc":{"tf":1}})
					else:
						#df+1, push article id 
						db.Keyword.update(
							{"keyword":word,"group.id":group["group"]},
							{"$inc":{"group.$.df_group":1,"tf":1,"df":1}}
						)
						db.Keyword.update(
							{"keyword":word,"group.id":group["group"]},
							{"$push":{"articles":article_id}}
							)
						print("same g diff a",word,key["df"])
						print(key["group"])
				else: #no group field
				#if word appeared in other groups
					if db.Keyword.find({"keyword":word,"articles":article_id}).count()==0:
						db.Keyword.update({"keyword":word},{"$push":{"articles":article_id}})
					db.Keyword.update({"keyword":word},{"$inc":{"df":1}})
					db.Keyword.update({"keyword":word},{"$push":{"group":{"id":group["group"],"df_other":0,"df_group":1}}})
					print("new group",word,key["df"])
					print(key["group"])

				for groups_in_keyword in key["group"]:
					db.Keyword.aggregate([{"$match":{"keyword":word}},
						{"$project":{"index":{"$indexOfArray":["$group.id",groups_in_keyword["id"]]}}},
						{"$out":"index"}])
					index_db = db.index.find_one()
					df_other = key["df"]-key["group"][index_db["index"]]["df_group"]
					db.Keyword.update(
						{"keyword":word,"group.id":groups_in_keyword["id"]},
						{"$set":{"group.$.df_other":df_other}}
					)
			else: #if word doesnt exist in db at all
				if len(word)>1:
					db.Keyword.insert({"keyword":word,"articles":[],"group":[],"tf":1,"df":1})
					db.Keyword.update({"keyword":word},{"$push":
						{"articles":article_id,
						"group":{"id":group["group"],
						"df_group":1,
						"df_other":0}}})
					key = db.Keyword.find_one({"keyword":word})
					print("first",word,key["df"])
db.Keyword.remove({"df":{"$lt":5}})




	
