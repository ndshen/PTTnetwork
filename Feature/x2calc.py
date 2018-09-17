from pymongo import MongoClient
import jieba
import math
client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja")
db=client.test_624
pop_n=1935
N=578
for groups in db.finalGroup.find():
	group = groups["_id"]
	word_group = db.Keyword.aggregate([{"$match":{"group.id":group}}])
	for word in word_group:
		df_total = word["df"] 
		df_pop_total =0
		for dfs in word["group"]:
			df_pop_total+= dfs["df_pop"]
		db.Keyword.aggregate([{"$match":{"keyword":word["keyword"]}},
			{"$project":{"index":{"$indexOfArray":["$group.id",group]}}},
			{"$out":"index"}])
		index_db = db.index.find_one()
		pop_n11 = word["group"][index_db["index"]]["df_pop"]
		pop_n10 = df_pop_total-pop_n11
		pop_n01 = len(groups["articles"])-word["group"][index_db["index"]]["df_pop"]
		pop_n00 = pop_n - pop_n11 - pop_n10 - pop_n01
		print(pop_n11,pop_n10,pop_n00,pop_n01,df_pop_total)
		if pop_n10 == 0:
			pop_n10 = 1
		if pop_n01 ==0:
			pop_n01 = 1
		N11 = word["group"][index_db["index"]]["df_group"]
		N10 = word["df"]-N11
		top30 = db.Feature.find_one({"group":group})
		N01 = top30["top30_len"]-word["group"][index_db["index"]]["df_group"]
		N00 = N - N11 - N10 - N01
		E11 = pop_n11*N/pop_n
		E10 = pop_n10*N/pop_n
		E00 = pop_n00*N/pop_n
		E01 = pop_n01*N/pop_n
		chisq = ((N11-E11)**2)/E11 + ((N10-E10)**2)/E10 + ((N00-E00)**2)/E00 + ((N01-E01)**2)/E01
		EMI = (N11/N)*math.log((N*N11)/(df_total*(N01+N11)))
		EMI = EMI +(N01/N)*math.log((N*N01)/((N01+N00)*(N01+N11)))
		EMI = EMI +(N10/N)*math.log((N*N10)/((N11+N10)*(N00+N10)))
		EMI = EMI +(N00/N)*math.log((N*N00)/((N00+N01)*(N00+N10)))
		print(word["keyword"],chisq)

		if db.tempFeature2.find({"group":group}).count()==0:
			print("insertinggggggggggg")
			db.tempFeature2.insert({
				"group":group,
				"result":[]
				})
		#get chisq lt 6.63 and sort by EMI from hight to low 
		if chisq <= 6.63: 
			if db.tempFeature2.find({"keyword":word["keyword"],"group":group}).count()==0:
				db.tempFeature2.update(
					{"group":group},
					{"$push":{"result":{"keyword":word["keyword"],"chisq":chisq,"EMI":EMI,"df":df_pop_total}}})
				db.tempFeature2.update(
					{"group":group},
					{"$push":{"result":{"$each":[],"$sort":{"EMI":-1}}}})

for result in db.tempFeature2.find():
	for i in range(0,10):
		print(result["group"],result["result"][i]["keyword"],result["result"][i]["chisq"])

