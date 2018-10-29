from aggregate_feature import findKeywordArticles
date = "2018-10-14"
day_range = 7
inter_gate = 15
group_id = 1

a = findKeywordArticles("老婆", date, day_range, inter_gate)
b = findKeywordArticles("女人", date, day_range, inter_gate)

print(len(a))
print(len(b))
print(len(a.intersection(b)))