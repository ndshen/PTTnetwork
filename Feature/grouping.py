#aggregate group and store the result in finalGroup collection
#insert Feature collection that stores the top 30% of a group
# insertfinalGroup={
# 	"group_id":-1,
# 	"usercount":0, #usercount
# 	"userId":-1,
# 	"articles":[{
# 		"_id":0,
# 		"count":0}],
#	"top30_len":0,
#	"top30":[],
#	“result”:[{
# 		"keyword":"",
# 		“EMI”:0,
# 		“chisq”:0}]
# }
import sys
from pymongo import MongoClient
client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja",password="swordtight")
db=client.CrawlGossiping_formal

date = "2018-10-07"
day_range = 7
Group = db.Group.find_one({"date":date,"day_range":day_range})
for group in Group["overall_group_list"]:
	if db.finalGroup.find_one({"group_id":group["overall_group_id"],"date":date,"day_range":day_range}) == None:
		print("group",group["overall_group_id"])
		if len(group["overall_group_users"]) >20: #if the usercount of group > 15
			db.finalGroup.insert({
				"group_id":group["overall_group_id"],
				"date":date,
				"day_range":day_range,
				"usercount":len(group["overall_group_users"]),
				"articles":[],
				"top30_len":0,
				"top30":[]
			})
		for user_id in group["overall_group_users"]: #for all users in that group
			user = db.User.find_one({"id":user_id})
			art_list = set()
			for article in user["Message"]:
				if article != "" and article["ArticleId"] not in art_list:
					art_list.add(article["ArticleId"])
					if db.Group.find({"date":date,"day_range":day_range, "overall_groupArticle_list":article["ArticleId"]}) != None:
						print(user_id, article["ArticleId"])
						count = db.finalGroup.find({"date":date,"day_range":day_range, "group_id":group["overall_group_id"],"articles._id":article["ArticleId"]}).count()
						#article not in list 
						if count == 0:
							db.finalGroup.update({"group_id":group["overall_group_id"], "date":date,"day_range":day_range},
								{"$push":{"articles":{"_id":article["ArticleId"],"count":1}}})
						else: #article already in list
							db.finalGroup.update({"group_id":group["overall_group_id"],"articles._id":article["ArticleId"],"date":date,"day_range":day_range},
								{"$inc":{"articles.$.count":1}})
				else:
					continue
		db.finalGroup.update(#sort by article count
			{"group_id":group["overall_group_id"],"date":date,"day_range":day_range},
			{"$push":{"articles":{"$each":[],"$sort":{"count":-1}}}})
		print("group done",group["overall_group_id"])

		temp = db.finalGroup.find_one({"group_id":group["overall_group_id"],"date":date,"day_range":day_range})

		if temp != None:		
			thirtypercent = int(len(temp["articles"])*0.33333)
			if thirtypercent < 1:
				thirtypercent=1
			for i in range(0,thirtypercent):
				print("30 percent inprogress")
				article_id = temp["articles"][i]["_id"]
				print(article_id)
				db.finalGroup.update(
					{"group_id":group["overall_group_id"],"date":date,"day_range":day_range},
					{
						"$set":{
								"top30_len":thirtypercent
								},
					 	"$push":{
					 			"top30":article_id
					 			}
					 })
				