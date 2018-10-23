from pymongo import MongoClient
import jieba
import math
import sys
client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja",password="swordtight")
db=client.CrawlGossiping_formal
N=0
date = "2018-10-07"
day_range = 7
for groups in db.finalGroup.find({"date":date,"day_range":day_range}):
	N+=groups["top30_len"]
print(N)
for groups in db.finalGroup.find({"date":date,"day_range":day_range}):
	group = groups["group_id"]
	print("group",group)
	word_group = db.Term.aggregate([{"$match":{"group.id":group,"date":date,"day_range":day_range}}]).batch_size(30)
	for word in word_group:
		df_total=0
		weight = 1 
		for df_group in word["group"]:
			df_total += df_group["df_group"]
		
		db.Term.aggregate([{"$match":{"term":word["term"],"date":date,"day_range":day_range}},
			{"$project":{"index":{"$indexOfArray":["$group.id",group]}}},
			{"$out":"index"}])
		index_db = db.index.find_one()
		N11 = word["group"][index_db["index"]]["df_group"]
		if N11/df_total > 0.04:
			E11 = word["df"]*groups["top30_len"]/N
			E01 = groups["top30_len"]-E11
			E10 = word["df"]*(N-groups["top30_len"])/N
			E00 = N-E11-E01-E10
			N10 = df_total-N11
			N01 = groups["top30_len"]-N11
			N00 = N - N11 - N10 - N01
			chisq = ((N11-E11)**2)/E11 + ((N10-E10)**2)/E10 + ((N00-E00)**2)/E00 + ((N01-E01)**2)/E01
			
			if N10 == 0:
				N10=0.5
			if N01 ==0:
				N01=0.5
			if N10/df_total < 0.5 and N11/df_total > 0.15:
				weight = 1.8
			EMI = (N11/N)*math.log2((N*N11)/(df_total*(N01+N11)))*weight
			EMI = EMI +(N01/N)*math.log2((N*N01)/((N01+N00)*(N01+N11)))
			EMI = EMI +(N10/N)*math.log2((N*N10)/((N11+N10)*(N00+N10)))
			EMI = EMI +(N00/N)*math.log2((N*N00)/((N00+N01)*(N00+N10)))
			print(word["term"],chisq,EMI)
			print(N,groups["top30_len"],N11,N10,N01,N00)
		
			if chisq >= 6.63 and EMI > 0.00009: 
				if db.finalGroup.find({"keyword":word["term"],"_id":group,"date":date,"day_range":day_range}).count()==0:
					print("insertinggggggggggg",group,word["term"])
					db.finalGroup.update(
						{"group_id":group,"date":date,"day_range":day_range},
						{"$push":{"result":{"keyword":word["term"],"chisq":chisq,"EMI":EMI}}})
					
	db.finalGroup.update(
		{"group_id":group,"date":date,"day_range":day_range},
		{"$push":{"result":{"$each":[],"$sort":{"EMI":-1}}}})
	print("group",group,"done")