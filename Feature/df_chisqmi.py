#calculate df chisq and EMI
from pymongo import MongoClient
import jieba
import math
import sys
client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja",password="swordtight")
db=client.CrawlGossiping_formal

date = sys.argv[1]
day_range = int(sys.argv[2])
official = int(sys.argv[3])
inter_gate = int(sys.argv[4])
N=0
top30_len_dic = []
for groups in db.finalGroup.find({"date":date,"day_range":day_range,"inter_gate":inter_gate}):
	if groups["group_id"] != 0:
		N+=groups["top30_len"]
		top30_len_dic.append((groups["group_id"],groups["top30_len"]))
top30_len_dic = dict(top30_len_dic)
print(N)
for word in db.Term.find({"date":date,"day_range":day_range,"inter_gate":inter_gate}):
	df_total=0
	df_list=[]
	for df_group in word["group"]:
		df_total += df_group["df_group"]

	for df_group in word["group"]:
		weight = 1
		group = df_group["id"]
		top30_len = top30_len_dic[group]
		N11 = df_group["df_group"]
		if N11/df_total > 0.035:
			top30_len = top30_len_dic[group]
			print("group",group,top30_len,word["term"])
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

			if N10/df_total < 0.1 and N11/df_total > 0.8:
				weight += N11/df_total
			if N11/df_total < 0.1:
				weight = 1.34-N11/df_total
			

			EMI = (N11/N)*math.log2((N*N11)/((N11+N10)*(N01+N11)))*weight
			EMI = EMI +(N01/N)*math.log2((N*N01)/((N01+N00)*(N01+N11)))
			EMI = EMI +(N10/N)*math.log2((N*N10)/((N11+N10)*(N00+N10)))
			EMI = EMI +(N00/N)*math.log2((N*N00)/((N00+N01)*(N00+N10)))
			
			print(df_group["id"],word["term"],chisq,EMI)	
			if chisq >= 6.63 and EMI > 0.00009: 
				#print("EMI > 0.00009")
				print("insertinggggggggggg",group,word["term"])
				db.finalGroup.update(
					{"group_id":group,"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate},
					{"$push":{"result":{"keyword":word["term"],"chisq":chisq,"EMI":EMI}}})
				db.finalGroup.update(
					{"group_id":group,"date":date,"day_range":day_range,"official":official,"inter_gate":inter_gate},
					{"$push":{"result":{"$each":[],"$sort":{"EMI":-1}}}})
