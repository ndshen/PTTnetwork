from pymongo import MongoClient
client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja")
db=client.test_624
groups = db.Group.aggregate([{"$group":{"_id":{"group":"$group"},
	"count":{"$sum":1},#usercount
	"userId":{"$push":"$id"}}},
	{"$match":{"count":{"$gt":1}}},
	{"$sort":{"count":-1}}])
insertFeature={
	"group":0,
	"top30_len":0,
	"top30":[],
}
insertfinalGroup={
	"_id":-1,
	"count":0, #usercount
	"userId":-1,
	"articles":[{
		"_id":0,
		"count":0}]
}
for group in groups:
	if group["count"] >15:
		db.finalGroup.insert({
			"_id":group["_id"]["group"],
			"count":group["count"],
			"userId":group["userId"],
			"articles":[]
		})
		db.Feature.insert({
			"group":group["_id"]["group"],
			"top30_len":0,
			"top30":[],
			"feature":[{
				"keyword":"",
				"chisquare":0}]
		})
	for user_id in group["userId"]:
		user = db.User.find_one({"id":user_id})
		for article in user["Message"]:
			if article != "":
				count = db.finalGroup.find({"_id":group["_id"]["group"],"articles._id":article["Articleid"]}).count()
				#article not in list 
				if count == 0:
					db.finalGroup.update({"_id":group["_id"]["group"]},
						{"$push":{"articles":{"_id":article["Articleid"],"count":1}}})
				else: #article already in list
					db.finalGroup.update({"_id":group["_id"]["group"],"articles._id":article["Articleid"]},
						{"$inc":{"articles.$.count":1}})
	db.finalGroup.update(
		{"_id":group["_id"]["group"]},
		{"$push":{"articles":{"$each":[],"$sort":{"count":-1}}}})
	print("group done")

	temp = db.finalGroup.find_one({"_id":group["_id"]["group"]})
	thirtypercent = int(len(temp["articles"])*0.33333)
	if thirtypercent < 1:
		thirtypercent=1
	for i in range(0,thirtypercent):
		print("inprogress")
		article_id = temp["articles"][i]["_id"]
		print(article_id)
		db.Feature.update(
			{"group":group["_id"]["group"]},
			{"$set":{"top30_len":thirtypercent}})
		db.Feature.update(
			{"group":group["_id"]["group"]},
			{"$push":{"top30":article_id}})
			


