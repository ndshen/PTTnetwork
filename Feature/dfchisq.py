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
    df = 0
    for df_group in word["group"]:
        df += df_group["df_group"] 

    for df_group in word["group"]:
        group = df_group["id"]
        exp_df = round(df*top30_len_dic[group]/N,3)
        df_chi = round(math.pow(df_group["df_group"]-exp_df,2)/exp_df,3)
        if exp_df > df_group["df_group"]:
            df_chi = df_chi*-1
        if df_group["df_group"] < 10:
            df_multi_chi = 0
        else:
            df_multi_chi = math.log2(df_group["df_group"])*df_chi
        if df_multi_chi > 0:
            print(word["term"],df_multi_chi)
            db.finalGroup.update(
		        {"group_id":group,"date":date,"day_range":day_range,"inter_gate":inter_gate},
		        {"$push":{"result":{"keyword":word["term"],"chisq":df_multi_chi}}})
            db.finalGroup.update(
                {"group_id":group,"date":date,"day_range":day_range,"inter_gate":inter_gate},
                {"$push":{"result":{"$each":[],"$sort":{"chisq":-1}}}})