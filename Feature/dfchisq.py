#calculate df chisq and EMI
from pymongo import MongoClient
import jieba
import math
import sys

N=0
date = "2018-10-07"
day_range = 7
top30_len_dic = []
for groups in db.finalGroup.find({"date":date,"day_range":day_range}):
	N+=groups["top30_len"]
	top30_len_dic.append((groups["group_id"],groups["top30_len"]))
top30_len_dic = dict(top30_len_dic)
print(N)
for word in  db.Term.find({"date":date,"day_range":day_range}):
	df_total = word["df"]
	for df_group in word["group"]:
		weight = 1
		group = df_group["id"]
		print("group",group)
		top30_len = top30_len_dic[group]
		N11 = df_group["df_group"]
		if N11/df_total > 0.04:
			print("group",group,word["term"])
			top30_len = top30_len_dic[group]
			E11 = word["df"]*top30_len/N
			E01 = top30_len-E11
			E10 = word["df"]*(N-top30_len)/N
			E00 = N-E11-E01-E10
			N10 = df_total-N11
			N01 = top30_len-N11
			N00 = N - N11 - N10 - N01
			if N11 == 0:
				N11 = 0.5
			if N10 == 0:
				N10 = 0.5
			chisq = ((N11-E11)**2)/E11 + ((N10-E10)**2)/E10 + ((N00-E00)**2)/E00 + ((N01-E01)**2)/E01
			if N10/df_total < 0.5 and N11/df_total > 0.9:
				weight = 1.8
			EMI = (N11/N)*math.log2((N*N11)/((N11+N10)*(N01+N11)))*weight
			EMI = EMI +(N01/N)*math.log2((N*N01)/((N01+N00)*(N01+N11)))
			EMI = EMI +(N10/N)*math.log2((N*N10)/((N11+N10)*(N00+N10)))
			EMI = EMI +(N00/N)*math.log2((N*N00)/((N00+N01)*(N00+N10)))
			print(word["term"],chisq,EMI)
			print(N,top30_len,N11,N10,N01,N00)
	
			if chisq >= 6.63 and EMI > 0.00009: 
				print("EMI > 0.00009")
				print("insertinggggggggggg",group,word["term"])
				db.finalGroup.update(
					{"group_id":group,"date":date,"day_range":day_range},
					{"$push":{"result":{"keyword":word["term"],"chisq":chisq,"EMI":EMI}}})
				db.finalGroup.update(
					{"group_id":group,"date":date,"day_range":day_range},
					{"$push":{"result":{"$each":[],"$sort":{"EMI":-1}}}})

		
