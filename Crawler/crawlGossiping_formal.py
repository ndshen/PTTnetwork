import http.client
import logging
import os
import re  # regular expression
import sched
import subprocess
import sys
import time
from datetime import datetime, timedelta
from threading import Timer
from urllib.request import urlretrieve  # import \

import requests  # package for request something form website
import urllib3
from bs4 import BeautifulSoup  # parse tool
from pymongo import MongoClient
import mes_black_list

urllib3.disable_warnings()
month = dict()
month ={'Jan':'1','Feb':'2','Mar':'3','Apr':'4','May':'5','Jun':'6','Jul':'7','Aug':'8','Sep':'9','Oct':'10','Nov':'11','Dec':'12'}


def print_log(*arg):
    string = ''
    length = len(arg)
    for i in range(length):
        if i != length-1:
            string += str(arg[i])+" "
        else:
            string += str(arg[i])
    print (string)
    logging.info(string)


def ageagree(res,url): # auto confirm 18+age
    rs = requests.session()
    res = rs.post('https://www.ptt.cc/ask/over18',verify=False,data={'yes':'yes'}) #post the confirm data to the website 
    res = rs.get(url,verify=False)
    return(res) #return the website that pass the 18-years old constraints


def comparetime(artone, arttwo):
    timeone = artone["Time"]
    timetwo = arttwo["Time"]
    try:
        timeone = datetime.strptime(timeone, '%a %b %d %H:%M:%S %Y')
        timetwo = datetime.strptime(timetwo, '%a %b %d %H:%M:%S %Y')
    except :
        print_log('wrong article time format')
        return False
    # avoid wrong time format
    if len(artone)>50:
        return False
    timeframe = timedelta(seconds = 1)
    if timeone - timetwo > timeframe:
        return True
    else:
        return False


#procedure
def main(args):
    global TIME_FRAME
    TIME_FRAME = None
    if len(args) == 4:
        TIME_FRAME = args[3]
    elif len(args) != 3 and len(args) != 5: 
        print_log("Please enter MongoDB password and pages (and start date and end date) to crawl")
        sys.exit(1)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.DEBUG,filename="../../tempData/crawler/download/formal_log.txt")#filename="../../tempData/crawler/download/formal_log.txt"
    global password
    #global pagetocrawl
    global idforUser
    global idforArticle
    
    global client
    global db
    global stop_crawler  # stop the crawler function to aviod crawl duplicate article
    global counttimes# count how many time the code has run
    global timesforsuccess
    timesforsuccess=0
    counttimes=2 
    stop_crawler = 0
    password = args[1]
    global pagetocrawl
    pagetocrawl=int(args[2])
    looptocrawl=int(pagetocrawl/3)
    # crawl data in special period 
    global start_date
    global end_date
    start_date = None
    end_date = None
    if len(args) == 5:
        start_date = args[3]
        end_date = args[4]
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except:
            print_log("Wrong Time Format, please enter start&end time in Year-Month-day format")
            pass
    if pagetocrawl% 3 >0:
        looptocrawl+=1
    client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja",password=password)  #connect to database
    print_log(client)
    
    db = client.CrawlGossiping_formal

      # if code runs first time
    
    global firsttimeruncode
    firsttimeruncode = 1

    print_log("Start to crawl "+str(pagetocrawl) + " pages of ptt")
    url = "https://www.ptt.cc/bbs/Gossiping/index.html" 
    nexturl = ""
    temppage = pagetocrawl
    for i in range(looptocrawl):
        page = 0
        if temppage > 3:
            page=3
        else:
            page = temppage

        print_log(page,url)

        (alldata, nexturl) = crawler(page, url)
        url = nexturl
        if stop_crawler: 
            break
    print_log("Parse due to:", nexturl)

    #k.start()
# upgrade condition
# main()->crawler()->(for each page)-> parse()->(select article to crawl)->download() and return

def crawler(pagetocrawl,url): # start to crawl
    global stop_crawler
    stop_crawler = 0 # stop crawler due to over five days(auto update function) 
    pages = pagetocrawl
    if not os.path.isdir('download'): #create a folder to save crawled articles
        os.mkdir('download')
    next_url = url
    result = ""
    tempresult = ""
    for round in range(pages): #number of pages we want to crawl
        url = next_url
        (next_url,tempresult) = parse(url)  # tempresult be the articles in one pages
        if tempresult != None:
            result = result + tempresult
        if stop_crawler == 1:
            print_log("crawler has been stopped")
            break
        #print_log(result)
    return(result, next_url)


def parse(url): # parse and get articles, res represent the age confirmed website, 

    try:
        res = requests.get(url)
    except http.client.HTTPException as e:
        print_log("Error",e)
        
    soup = BeautifulSoup(res.text,'html.parser')   #use BeautifulSoup to parse
    
    if len(soup.select('div.over18-notice')) > 0: #if there is a prompt to ask age
        res = ageagree(res,url) # #auto confirm age

    soup = BeautifulSoup(res.text,'html.parser')
    tagname = "div.title a"  #the div which class is title
    articles = soup.select(tagname)
    
    
    if url == "https://www.ptt.cc/bbs/Gossiping/index.html":
        paging = soup.select('div.btn-group-paging a') #preceding page
        next_url ="https://www.ptt.cc"+paging[1]['href']  #preceding page
    else:
        num = url[:-5]
        num = num[38:]
        webindex = int(num)-1
        next_url = "https://www.ptt.cc/bbs/Gossiping/index"+str(webindex)+".html"

    print_log("url:",url,"next_url:",next_url)
    
    url = next_url
    try:
        temp = download(articles, res)# choose what attr will be crawl
    except http.client.HTTPException as e:
        print_log("Error",e)
    return (url,temp) #return the next page url, temp for the temporary data
    

def find_lastest_art():
    collection = db["Article"]
    allart = db.Article.find()
    temp = ""
    latestartid = -1
    for oneart in allart:
        if temp == "":
            latestartid = oneart["id"]
            temp = oneart
        else:
            if comparetime(oneart, temp):
                latestartid = oneart["id"]
                temp = oneart
    return latestartid


def download(articles,res): #download the content, choose what attr will be crawled
    collection=db["Article"]
    if db.Article.find().count()!=0:
        idforArticle=db.Article.count()
    else:
        idforArticle = 0 
    collection=db["User"]
    if db.User.find().count()!=0:
        idforUser = db.User.count()
    else:
        idforUser = 0
    print_log("id_for_article:",idforArticle,"id_for_user:",idforUser)
    #global latestArticleid  # to get the latest Article in Mongo DB
    collection = db["Article"]
    articlenumber = db.Article.find().count()
    global firsttimeruncode

    # check if article in 3 days 
    if firsttimeruncode == 0:
        latestartid = find_lastest_art()
        latestart = db.Article.find_one({"id": latestartid })
        latesttime = latestart["Time"] # get the latest time of article in MOnog DB
        
        try:
            latesttime = datetime.strptime(latesttime, '%a %b %d %H:%M:%S %Y') 
        except :
            print_log('Still wrong time format ')
        
        today = datetime.today()
        timeframe = timedelta(days = 2)

    
    temp = ""
    for article in articles:
        
        url = "https://www.ptt.cc"+article['href']
        try:
            res = requests.get(url)
            res2 = ageagree(res,url) #auto confirm age
        except http.client.HTTPException as e:
            print_log("ERROR",e)
        
        soup = BeautifulSoup(res2.text,'html.parser')

        details =  soup.findAll("meta", property="og:description") #main contents 
        titletagname = "span.article-meta-value"
        titles=soup.select(titletagname) #title,date and author
        
        pushtagname="div.push"
        pushes=soup.select(pushtagname) #push and messages
        if titles ==[]:
            print_log("skip for 八卦板板規 ")
            continue
        flagfortitle = 0
        time_value = None
        author_value = None
        title_value = None
        flag = 0
        for title in titles:   # avoid 板規 公告
            #print(title) 
            if "公告" in title.text:     
                flagfortitle = 1
                break
            if "協尋" in title.text:
                flagfortitle = 1
                break
            if flag == 0:
                author_value = title.text
            elif flag == 2:
                title_value = title.text
            elif flag == 3:
                time_value = title.text.replace('  ',' ')
            flag += 1    
        if flagfortitle == 1 : 
            print_log("skip for 公告 or 協尋")
            continue
        if time_value is None or author_value is None or title_value is None:
            print_log('error value when crawling')
            continue
        # crawl within 7 seven days
        global TIME_FRAME
        if TIME_FRAME is not None:
            pubdate_str = "span.article-meta-value" #Fri May  4 14:41:53 2018 # if the time exceed 5days, stop downloading
            pubdate_str = soup.select(pubdate_str)
             # publish day of the current article
            #print_log(pubdate_str[3].text)
            global stop_crawler
            if firsttimeruncode == 0 :
                pubdate_str = "span.article-meta-value" #Fri May  4 14:41:53 2018 # if the time exceed 5days, stop downloading
                pubdate_str = soup.select(pubdate_str)
                # publish day of the current article
                #print_log(pubdate_str[3].text)
                try:
                    pubdate = datetime.strptime(pubdate_str[3].text, '%a %b %d %H:%M:%S %Y')
                    if  latesttime - pubdate > timeframe:
                        print_log(str(latesttime)+'\n'+str(pubdate))
                        print_log("exceed our timeframe 1 day")
                        stop_crawler = 1
                        return temp
                        break
                except :
                    print_log("error", pubdate)
                    continue
                #print_log(latesttime,pubdate)
            try:
                pubdate = datetime.strptime(pubdate_str[3].text, '%a %b %d %H:%M:%S %Y')
                print(datetime.now().replace(microsecond=0), pubdate)
                if  datetime.now().replace(microsecond=0) - pubdate > timedelta(days= int(TIME_FRAME)):
                    print_log(str(latesttime)+'\n'+str(pubdate))
                    print_log('exceed our timeframe %s day' % TIME_FRAME)
                    stop_crawler = 1
                    return temp
                    break
            except Exception as e:
                print(e)
                print_log("error", pubdate)
                continue
        
            
        ipaddressname="span.f2"
        f2tag=soup.select(ipaddressname)
        ipaddress=""
        for ip in f2tag:
            ip=ip.text
            if "來自:" in ip:
                ipaddress=ip[27:]
                ipaddress=ipaddress[:len(ipaddress)-1]
                break
        # pass the current article due to not in specified period
        flag_to_stop = 0
        art_time = None
        if start_date is not None:
            if len(titles)>3 and time_value is not None:
                try:
                    art_time = time_value
                    art_time = art_time[-4:] +"-"+ month[str(art_time.split(' ')[1])] +"-"+ art_time.split(' ')[2]#data.split(a,b)[0] split for b+1 times
                    art_time = datetime.strptime(art_time,"%Y-%m-%d")
                    if art_time > end_date :
                        continue
                    if art_time < start_date:
                        print_log("Successfully done")
                        flag_to_stop = 1
                except:
                    print_log("Can't find time in this article")
                    continue
            else:
                continue
        if flag_to_stop == 1:
            sys.exit(1)

        
        temp=temp+"\n"
        temp=temp+"發文者(Author): " + author_value
        temp=temp+'\n'
        temp=temp+"主題(Title): " + title_value
        temp=temp+'\n'
        temp=temp+"時間(Time): " + time_value
        temp=temp+'\n'

            
        #content
        content = ''
        for detail in details: 
            content = content + detail['content'] + '\n'
            temp = temp + detail['content'] + '\n'
        # push messages
        for push in pushes:
            temp = temp + push.text+'\n'
        # ip address    
        temp = temp + "Ipaddress:" + ipaddress + '\n'
        # url
        temp = temp + "文章網址(url):" + url
        temp = temp + '\n' + '\n'

        global timesforsuccesssuccess
        print_log("success")
        print_log("Article_name: ", title_value)

        #Get Author information
        Author = {
                "Name":"", "id":-1,
                "Nickname":"", "CorrelatedUser":[],
                "Article":[], "Message":[""]
        }
        lengthforauthor = len(author_value.split(' ',1))
        pri_name = None
        nickname = None
        if lengthforauthor > 1:
            temp = author_value.replace("  "," ")
            pri_name = temp.split(' ',1)[0]
            nickname = temp.split(' ',1)[1]
        else:
            pri_name = author_value
        Author['Name'] = pri_name
        Author['id'] = idforUser
        Author['Nickname'] = nickname
        author_id = idforUser
        # check author if in database
        check_new_author = 1
        check_id = check_duplicate('Author', Author)
        if check_id == -1:
            idforUser += 1
        else:
            author_id = check_id
            Author['id'] = author_id
            check_new_author = 0
        
        #Get article informatioㄙ
        insert_article = {
                        "ArticleName": title_value, "id": idforArticle,
                        "Time": time_value, "Author": author_value,
                        "IPaddress": ipaddress, "URL": url,
                        "Content": content, "Boo": [""], "Push":[""], "Neutral":[""]
        }
        article_id = idforArticle
        #check article if in database
        check_new_aritcle = 1
        check_id = check_duplicate('Article', insert_article)
        if check_id == -1:
            idforArticle += 1
        else:
            article_id = check_id
            insert_article['id'] = article_id
            check_new_aritcle =0
            # for first time crawl, to speed up first time
            if firsttimeruncode:
                print_log('skip duplicate article for first time')
                return None
        print_log("Article id: " + str(article_id) )
        Push_list = []
        Boo_list = []
        Neutral_list = []
        all_mes_user_id = []
        for push in pushes:
            try:
                data = push.text[:-1]
                mes_type = data[0]
                name = data.split(' ')[1][:-1]#data.split(a,b)[0] split for b+1 times
                mes_time = data.split(' ')[-2] + ' ' +data.split(' ')[-1]
                content = data.split(' ', 2)[2][:-1*len(mes_time)]
            except Exception as e:
                print_log(e)
                continue
            # commentor equal author 
            if name == author_value:
                continue
            # ignore the content which has no relation with article
            skip_mes = 0
            for black_list in mes_black_list.BLACK_LIST:
                if content.find(black_list) != -1:
                    skip_mes = 1
                    break
            if skip_mes:
                continue
            insert_user = {
                "Name": name, "id":idforUser,
                "Nickname":"", "CorrelatedUser":[],
                "Article":[], "Message":[""]
            }
            insert_message_to_user = {
                "ArticleName": title_value,
                'ArticleId': article_id,
                "React":"", #0 for boo ,1 for push, 2 for neutral
                "Message": content,
                'Time': mes_time
            }
            insert_message_to_art = {
                'Name' : name,
                'Content': content,
                'Time': mes_time
            }
            
            if mes_type == '推':
                Push_list.append(insert_message_to_art)
                insert_message_to_user['React'] = '推'
                insert_user['Message'] = [insert_message_to_user]

            elif mes_type == '噓':
                Boo_list.append(insert_message_to_art)
                insert_message_to_user['React'] = '噓'
                insert_user['Message'] = [insert_message_to_user]
            else:
                Neutral_list.append(insert_message_to_art)
                insert_message_to_user['React'] = '純回文'
                insert_user['Message'] = [insert_message_to_user]
                
            #check user data whetehr in database

            temp_user = check_duplicate('User', insert_user)
            collection = db["User"]
            if not temp_user:
                all_mes_user_id.append(idforUser)
                collection.insert(insert_user)
                if author_id > idforUser :
                    count_relation(idforUser, author_id, article_id, time_value)
                else:
                    count_relation(author_id, idforUser, article_id, time_value)
                idforUser += 1
            else:
                all_mes_user_id.append(temp_user['id'])
                if author_id > temp_user['id'] :
                    count_relation(temp_user['id'], author_id, article_id, time_value)
                else:
                    count_relation(author_id, temp_user['id'], article_id, time_value)
                if check_new_aritcle == 1 :
                    collection.find_one_and_update(
                        {'id': temp_user['id']
                    },{
                        '$push': {
                            'Message': insert_message_to_user
                        }
                    })
                else:
                    user = collection.find_one({'id': temp_user['id']})
                    duplicate = 0
                    for mes in user['Message']:
                        if mes == '':
                            continue
                        if mes['ArticleName'] == title_value and mes['ArticleId'] == article_id and mes['Message'] == content:
                            duplicate = 1
                            break
                    if duplicate != 1 :
                        collection.update_one(
                            {'id': temp_user['id'], "Article.Articlename":title_value
                        },{
                            '$push': {
                                'Message': insert_message_to_user
                            }
                        })

        update_relation_between_commentor(all_mes_user_id, article_id, time_value)

        insert_article['Boo'] = Boo_list
        insert_article['Push'] = Push_list
        insert_article['Neutral'] = Neutral_list
        
        # check article data whether in database, and insert to database
        collection = db['Article']
        if check_new_aritcle == 1:
            collection.insert(insert_article)
        else:
            collection.find_one_and_update(
            {'ArticleName': insert_article['ArticleName'], 'Author': insert_article['Author'], 'URL': insert_article['URL']},
            { '$set':{
                'Boo': insert_article['Boo'], 
                'Push': insert_article['Push'],
                'Neutral': insert_article['Neutral']
                }
            }
            )
        # check the author if exist in database, and insert to database
        collection = db['User']
        try:
            art_time = str(datetime.strptime(time_value, '%a %b %d %H:%M:%S %Y').date())
        except:
            print('error time format')
            continue
        if check_new_author == 1:
            save_data = {'art_id': article_id, 'art_time': art_time}
            Author['Article'].append(save_data)
            collection.insert(Author)
        else:
            collection.update_one({
                'id': author_id
                },{
                    "$addToSet": {
                        "Article": {'art_id': article_id, 'art_time': art_time}
                    }
                })
        print_log('Article id :' + str(article_id) + 'finished')

        
    return(temp)  #return the temporary result


def check_duplicate(category, data):
    if category == 'Article':
        collection = db[category]
        article = collection.find_one(
            {'ArticleName': data['ArticleName'], 'Author': data['Author'], 'URL': data['URL']}
        )
        if article is not None:
            return article['id']
        return -1

    elif category == 'Author':
        collection = db['User']
        user = collection.find_one(
            {'Name': data['Name']}
        )
        if user is not None:
            return user['id']
        return -1
    elif category == 'User':
        collection = db[category]
        user = collection.find_one(
            {'Name': data['Name']}
        )
        if user is not None:
            return user
        return False
    #else:


def update_relation_between_commentor(mes_list, art_id, art_time):
    length = len(mes_list)
    mes_list.sort()
    mes_list = list(set(mes_list))
    length = len(mes_list)
    for index, user_id in enumerate(mes_list):
        for i in range(index+1, length):
            if user_id < mes_list[i]:
                count_relation(user_id, mes_list[i], art_id, art_time)
            else:
                count_relation(mes_list[i], user_id, art_id, art_time)


def count_relation(userA_id, userB_id, Article_id, art_time):  # update the relation collection
    print_log("Update relation between " + str(userA_id)+ " and " + str(userB_id))
    collection = db["Relation"]
    relation = collection.find_one({"user1id":userA_id,"user2id":userB_id })
    duplicate_id = 0
    try:
        art_time = str(datetime.strptime(art_time, '%a %b %d %H:%M:%S %Y').date())
    except:
        print('error time format')
        return
    if userA_id != userB_id :
        if relation != None:
            #print_log(artidlist["user1id"])
            artidlist = relation["Articleid"]
            if artidlist != None:
                for exist_id in artidlist:
                    if exist_id['art_id'] == Article_id:
                        duplicate_id = 1
                        break
                if duplicate_id != 1:  # avoid duplicated count message in one article
                    save_data = {'art_id': Article_id, 'art_time': art_time}
                    artidlist.append(save_data)
                
                    collection.update_one(
                    {"user1id":userA_id,"user2id":userB_id },
                    {
                    "$inc":{
                            "Intersection":1
                            },
                    
                    "$set":{
                            "Articleid":artidlist
                        
                        }
                    }
                    )
        else:
            oneRelation={       #insert to mongo DB
                "user1id":-1,
                "user2id":-1,
                "Intersection":0,
                "Articleid":[] # may have a lot of relation with otehr users
            }
            oneRelation["user1id"]=userA_id
            oneRelation["user2id"]=userB_id
                    # record correlated user id in user with larger id in User collection 
            updateCorrelateduser(userA_id, userB_id)
                
            oneRelation["Intersection"]+=1
            intersectionarticlelist=[]
            save_data = {'art_id': Article_id, 'art_time': art_time}
            intersectionarticlelist.append(save_data)    
            oneRelation["Articleid"]=intersectionarticlelist

            collection=db["Relation"]
            collection.insert(oneRelation) 
    

def updateCorrelateduser(userA_id, userB_id):  # update correlated user id in user collection, userA's id is smaller than userB's
    collection=db["User"]
    tempuser=collection.find_one({"id":userB_id})
    if tempuser!=None:
        if len(tempuser["CorrelatedUser"]) > 0:
            tempcorrelateduserid=tempuser["CorrelatedUser"]
            check=0
            for exist in tempcorrelateduserid:
                if exist==userA_id:
                    check=1
                    break
            if check==0:
                tempcorrelateduserid.append(userA_id)
        else:
            tempcorrelateduserid=[]
            tempcorrelateduserid.append(userA_id)

        collection.update_one(
        {"id":userB_id },
        {
        "$set":{
            "CorrelatedUser":tempcorrelateduserid
        }
        })


def getdeltatime(): #get delta time
    x = datetime.today()
    y = x + timedelta(days = 1)
    delta_t = y-x
    return (delta_t.total_seconds())


if __name__ == '__main__' :
    main(sys.argv)
    print_log('Crawler successfully done, wating for next day schedule...')
    global stop_crawler, firsttimeruncode
    stop_crawler = 0
    firsttimeruncode = 0
    k = Timer(getdeltatime(), main, [sys.argv])
    k.start()



