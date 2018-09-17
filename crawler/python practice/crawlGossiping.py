import http.client
import logging
import os
import re  # regular expression
import sched
import subprocess
import sys
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
import http.client
=======
import time
from datetime import datetime, timedelta
from threading import Timer
from urllib.request import urlretrieve  # import \
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py

import requests  # package for request something form website
import urllib3
from bs4 import BeautifulSoup  # parse tool
from pymongo import MongoClient

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

    

# upgrade condition
# main()->crawler()->(for each page)-> parse()->(select article to crawl)->download() and return

def crawler(pagetocrawl,url): # start to crawl
    stopcrawler = 0 # stop crawler due to over five days(auto update function) 
    pages = pagetocrawl
    if not os.path.isdir('download'): #create a folder to save crawled articles
        os.mkdir('download')
    next_url = url
    result = ""
    tempresult = ""
    for round in range(pages): #number of pages we want to crawl
        if stopcrawler == 1:
            print_log("crawler has been stopped")
            break
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
        url=next_url
        res=requests.get(url)
        soup=BeautifulSoup(res.text,'html.parser')   #use BeautifulSoup to parse
        
        if len(soup.select('div.over18-notice')) > 0: #if there is a prompt to ask age
            res=ageagree(res,url) # #auto confirm age
            try:
                (next_url,tempresult)=parse(res)  # tempresult be the articles in one pages
            except http.client.HTTPException as e:
                print("Error",e)
            result=result+tempresult
            
        else:
            (next_url,tempresult)=parse(res)
            result=result+tempresult
        #print(result)
        
    #with open("download/Gossiping.txt", "w",encoding="UTF-8") as text_file: #save the data into Gossiping.txt
      #      print(f"{result}", file=text_file)
      #      text_file.close() #close the file
=======
        url = next_url
        (next_url,tempresult) = parse(url)  # tempresult be the articles in one pages
        result = result+tempresult
        #print_log(result)
    with open("download/Gossiping.txt", "a",encoding="UTF-8") as text_file: #save the data into Gossiping.txt    
        #print(f"{result}", file=text_file)
        text_file.close() #close the file
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
    return(result,next_url)

def ageagree(res,url): # auto confirm 18+age
    rs = requests.session()
    res = rs.post('https://www.ptt.cc/ask/over18',verify=False,data={'yes':'yes'}) #post the confirm data to the website 
    res = rs.get(url,verify=False)
    return(res) #return the website that pass the 18-years old constraints

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
    
    
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
    paging = soup.select('div.btn-group-paging a') #preceding page
    next_url="https://www.ptt.cc"+paging[1]['href']  #preceding page
    url=next_url
    try:
        temp=download(articles,res)# choose what attr will be crawl
    except http.client.HTTPException as e:
        print("Error",e)
=======
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
        temp = download(articles,res)# choose what attr will be crawl
    except http.client.HTTPException as e:
        print_log("Error",e)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
    return (url,temp) #return the next page url, temp for the temporary data

def comparetime(artone,arttwo):
    timeone = artone["Time"]
    timetwo = arttwo["Time"]
    timeone = datetime.strptime(timeone, '%a %b %d %H:%M:%S %Y')
    
    timetwo = datetime.strptime(timetwo, '%a %b %d %H:%M:%S %Y')
    timeframe = timedelta(seconds=1)
    if timeone-timetwo>timeframe:
        return True
    else:
        return False

    

def download(articles,res): #download the content, choose what attr will be crawled
    #global latestArticleid  # to get the latest Article in Mongo DB
    collection = db["Article"]
    articlenumber = db.Article.find().count()
    global firsttimeruncode
    if firsttimeruncode == 0:
        collection = db["Article"]
        allart = db.Article.find()
        temp = ""
        latestartid = -1
        for oneart in allart:
            if temp == "":
                latestartid = oneart["id"]
                temp = oneart
            else:
                if comparetime(oneart,temp):
                    latestartid = oneart["id"]
                    temp = oneart
        latestart = db.Article.find_one({"id":latestartid})
        
        
        latesttime = latestart["Time"] # get the latest time of article in MOnog DB
        
        if len(latesttime)>30: #avoid wrong tiem format
            latestart = db.Article.find_one({"id":articlenumber-1})
            latesttime = latestart["Time"]  
        latesttime = datetime.strptime(latesttime, '%a %b %d %H:%M:%S %Y') 

    #print_log(latesttime)
        today=datetime.today()
        timeframe =timedelta(days=5)

    
    temp = ""
    for article in articles:
        
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
        url="https://www.ptt.cc"+article['href']
        try:
            res=requests.get(url)
            res2=ageagree(res,url) #auto confirm age
        except http.client.HTTPException as e:
            print("ERROR",e)
        
        soup=BeautifulSoup(res2.text,'html.parser')
  #     detailtagname= "div#main-content"  #crawl by id

        details= soup.findAll("meta", property="og:description") #main contents 
        titletagname="span.article-meta-value"
=======
        url = "https://www.ptt.cc"+article['href']
        try:
            res = requests.get(url)
            res2 = ageagree(res,url) #auto confirm age
        except http.client.HTTPException as e:
            print_log("ERROR",e)
        
        soup = BeautifulSoup(res2.text,'html.parser')

        details =  soup.findAll("meta", property="og:description") #main contents 
        titletagname = "span.article-meta-value"
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
        titles=soup.select(titletagname) #title,date and author
        
        pushtagname="div.push"
        pushes=soup.select(pushtagname) #push and messages
        if titles ==[]:
            print_log("skip for 八卦板板規 ")
            continue
        flagfortitle=0
        for title in titles:   # avoid 板規 公告
            #print_log(title) 
            if "公告" in title.text:     
                flagfortitle=1
                break
            if "協尋" in title.text:
                flagfortitle=1
                break    
        if flagfortitle ==1:
            print_log("skip for 公告 or 協尋")
            continue

        if firsttimeruncode==0 :
            pubdate_str = "span.article-meta-value" #Fri May  4 14:41:53 2018 # if the time exceed 5days, stop downloading
            pubdate_str= soup.select(pubdate_str)
             # publish day of the current article
            flagfortrycatch=0
            #print_log(pubdate_str[3].text)
            try:
                pubdate = datetime.strptime(pubdate_str[3].text, '%a %b %d %H:%M:%S %Y')
            except :
                flagfortrycatch=1
                print_log("error",pubdate)
            #print_log(latesttime,pubdate)
            if flagfortrycatch==0 :
                if  latesttime - pubdate > timeframe:
                    print_log(str(latesttime)+'\n'+str(pubdate))
                    print_log("exceed our timeframe 5 days")
                    stopcrawler = 1
                    break

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
        art_time = titles[3].text
        art_time = art_time[-4:] +"-"+ month[str(art_time.split(' ')[1])] +"-"+ art_time.split(' ')[2]#data.split(a,b)[0] split for b+1 times
        art_time = datetime.strptime(art_time,"%Y-%m-%d")
        if art_time > end_date  :
            continue
        if art_time < start_date:
            print_log("Successfully done")
            sys.exit(1)

        temp=temp+"\n"
        times=0
        for title in titles:   #title,date and author
            if times==0:
                temp=temp+"發文者(Author): "
                temp=temp+title.text+'\n'
                #print_log(title.text)  
            elif times==2:
                temp=temp+"主題(Title): "
                temp=temp+title.text+'\n'
                #print_log(title.text)  
            elif times==3:
                temp=temp+"時間(Time): "
                temp=temp+title.text+'\n'

                #print_log(title.text)  
            times+=1
            
            #print_log(title.text)
        for detail in details: #content
            temp=temp+detail['content']+'\n'
        for push in pushes:  # push messages
            temp=temp+push.text+'\n'

        temp=temp+"Ipaddress:"+ipaddress+'\n'
        
        
        temp=temp+"文章網址(url):"+url
        temp=temp+'\n'+'\n'
        global timesforsuccess
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
        print("success",timesforsuccess)
        timesforsuccess+=1
    #print(temp) 
=======
        print_log("success", timesforsuccess)
        timesforsuccess+=1
    #print_log(temp) 
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
    return(temp)  #return the temporary result


def main(args):
    
    if len(args) != 3 and len(args) != 5: 
        print_log("Please enter MongoDB password and pages (and start date and end date) to crawl")
        sys.exit(1)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',level=logging.DEBUG,filename="download/error_message.txt")
    global password
    #global pagetocrawl
    global idforUser
    global idforArticle
    
    global client
    global db
    global stopcrawler  # stop the crawler function to aviod crawl duplicate article
    global counttimes# count how many time the code has run
    global timesforsuccess
    timesforsuccess=0
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
    counttimes=2
    
        
    
=======
    counttimes=2 
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
    stopcrawler=0
    password=args[1]
    global pagetocrawl
    pagetocrawl=int(args[2])
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py

    
    looptocrawl=int(pagetocrawl/100)
    if pagetocrawl%100>0:
        looptocrawl+=1

    client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja",password=password)  #connect to database
    print(client)
    db=client.test_620
=======
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
            start_date = datetime.strptime(start_date,"%Y-%m-%d")
            end_date = datetime.strptime(end_date,"%Y-%m-%d")
        except:
            print_log("Wrong Time Format, please enter start&end time in Year-Month-day format")
            pass
    if pagetocrawl% 3 >0:
        looptocrawl+=1

    client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja",password=password)  #connect to database
    print_log(client)
    
    db=client.test_714
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py

      # if code runs first time
    
    global firsttimeruncode
    firsttimeruncode=1

    print_log("Start to crawl "+str(pagetocrawl) +" pages of ptt")
    url="https://www.ptt.cc/bbs/Gossiping/index.html" 
    nexturl=""
    temppage=pagetocrawl
    for i in range(looptocrawl):
        page=0
        if temppage>3:
            page=3
        else:
            page=temppage

        print_log(page,url)

        (alldata,nexturl)=crawler(page,url)
        url=nexturl
        alldata=alldata+"\n"+"發文者(Author): "
        temppage-=3

        lengthofdata=len(alldata.split('\n'))
        print_log("Parser started")
        Parsedata(alldata)
        print_log("Parser successed")

    
   
    
    #main()
    #start to crawl (first time)
    #print_log(alldata)


<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
    print("Parse due to:",nexturl)
=======
    print_log("Parse due to:",nexturl)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py

    #k.start()


    firsttimeparse()
    k=Timer(getdeltatime(),autoRunProgram)

def autoRunProgram(): #run every 3 days
    global counttimes
    print_log("Crawler started for "+str(counttimes)+" times")
    counttimes=counttimes+1
    
    global pagetocrawl
    looptocrawl=int(pagetocrawl/3)
    if pagetocrawl % 3 > 0:
        looptocrawl += 1
    url="https://www.ptt.cc/bbs/Gossiping/index.html" 
    for i in range(looptocrawl):
        temppage=pagetocrawl
        page = 0
        if temppage > 3:
            page=3
        else:
            page=temppage

        (alldata,url)=crawler(page,url)

        alldata=alldata+"\n"+"發文者(Author): "


        temppage -= 3

        lengthofdata=len(alldata.split('\n'))
        print_log("Parser started")
        Parsedata(alldata)
        print_log("Parser successed")
    
    k=Timer(getdeltatime(),autoRunProgram)
    k.start()
    print_log("Waiting for deltatime 3 days....")


def firsttimeparse():
    k=Timer(getdeltatime(),autoRunProgram)
    k.start()
    print_log("Waiting for deltatime 3 days....")

    

 

def getdeltatime(): #get delta time
    x=datetime.today()
    y=x+timedelta(days=3)
    delta_t=y-x
    return (delta_t.total_seconds())





def Parsedata(alldataincrawl):
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
    #print(password)
=======
    #print_log(password)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
    ####### add id to user and article class
    collection=db["Article"]
    if db.Article.find().count()!=0:
        idforArticle=db.Article.count()
    else:
        idforArticle=-1
    collection=db["User"]
    if db.User.find().count()!=0:
        idforUser=db.User.count()
    else:
        idforUser=-1 
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
    print(idforArticle,idforUser)

    
=======
    print_log("id_for_article:",idforArticle,"id_for_user:",idforUser)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py

    lengthofdata=len(alldataincrawl.split('\n'))
    ouputdata=""
    author="" #name of all author
    numbersOfArticle=0
    numbersOfAuthor=0 #people who wrote articles
    numbersOfmessage=0 # include messagers

    class myarticle : # class that contains name,author,number of push and boo(and context)
        def __init__(self):
            self.author=""
            self.push=0
            self.boo=0
            self.articlename=""
            self.pushcontext=[]
            self.boocontext=[]
            self.content=""
            self.time=""
            self.ip=""
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
=======
            self.url=""
        def seturl(self,myurl):
            self.url=myurl
        def geturl(self):
            return(self.url)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
        def setid(self,id):
            self.id=id
        def getid(self):
            return(self.id)
        def setip(self,ipadd):
            self.ip=ipadd
        def savePushmessage(self,data):    # save push message
            self.pushcontext.append(data.replace("推 ","",1))
        def saveBoomessage(self,data):         # save boo message
            self.boocontext.append(data.replace("噓 ","",1)) 
        def inputauthor(self,author):           #input author
            self.author=author
        def inputarticlename(self,name):        #input articlename
            self.articlename=name
        def pushplus(self):
            self.push=self.push+1
        def booplus(self):
            self.boo=self.boo+1
        def setcontent(self,contents):
            self.content=contents
        def settime(self,time):
            self.time=time
        def print_logall(self):
            print_log(self.author,self.articlename,self.push,self.boo)
            #print_log(self.pushcontext,self.boocontext)
        def print_logcalledfromuser(self):
            print_log(self.articlename,self.push,self.boo)
            #print_log(self.pushcontext,self.boocontext)
        def returnall(self):
            data=self.author+"\n"+self.time+"\n"+self.articlename+"\n"+"推："+str(self.push)+"   噓："+str(self.boo)+"\n"+self.content
            return(data)
        def returnformes(self):
            return(self.author+" "+self.articlename+"  推"+self.push+"  噓"+self.boo)
        def getarticlename(self):
            return(self.articlename)
        def getauthor(self):
            return(self.author)
        def getcontent(self):
            return(self.content)
        def getboo(self):
            return(self.boocontext)
        def getpush(self):
            return(self.pushcontext)
        def gettime(self):
            return(self.time)
        def getboonum(self):
            return(self.boo)
        def getpushnum(self):
            return(self.push)
        def getip(self):
            return(self.ip)
    class user : #username, article and message
        def __init__(self):
            self.name=""
            self.nickname=""
            self.id=-1
            self.message=[message() for _ in range(1)]
            self.article=[myarticle() for _ in range(1)]
        def setid(self,id):
            self.id=id
        def getid(self):
            return(self.id)
        def inputname(self,name):
            self.name=name
        def inputnickname(self,name):
            self.nickname=name
        def getname(self):   #get the username
            return(self.name)
        def getnickname(self):
            return(self.nickname)    
        def getarticle(self): #get the article name
            return(self.article)
        def getmessage(self):
            return(self.message)    
        def setarticle(self,article):
            self.article.append(article)
        def setmes(self,mes):   #set message
            self.message.append(mes)
        def countartnum(self):   #count how many articles a author has 
            i=0
            for art in self.article:
                i=i+1
            return(i-1)
        def countmesnum(self):   #count how many articles a author has 
            i=0
            for mes in self.message:
                i=i+1
            return(i-1)
        def print_logall(self):
            print_log(self.name)
            i=0
            print_log("Articles:")
            for art in self.article:
                if i<1:
                    i=i+1
                    continue
                art.print_logcalledfromuser()
            
            i=0
            print_log("message:")
            for mes in self.message:
                if i<1:
                    i=i+1
                    continue
                mes.print_logeverything()

            print_log("\n")
            print_log("\n")
    class message: # name,message,react,article
        def __int__(self):
            self.name=""
            self.articleid=-1
            self.article=myarticle() 
            self.message=""
            self.react=0   # 0 for boo ,1 for push
        def setarticleid(self,id):
            self.articleid=id
        def getarticleid(self):
            return(self.articleid)
        def setname(self,name):
            self.name=name
        def setarticle(self,art):
            self.article=art
        def setmessage(self,mes):
            self.message=mes
        def setPush(self):
            self.react=1
        def setBoo(self):
            self.react=0
        def print_logmes(self):
            print_log(self.name,self.message)
        def print_logarticle(self):
            self.article.print_logall()
        def print_logeverything(self):
            self.article.print_logall()
            if self.react==1 :
                print_log(self.name,"推 ",self.message)
            else:
                print_log(self.name,"噓 ",self.message)
        def getreact(self):
            if self.react==1 :
                return("推")
            else:
                return("噓")
        def getmes(self):
            return(self.message)
        def getname(self):
            return(self.name)
        def getarticle(self):
            return(self.article.getarticlename())
        def returnall(self):
            if self.react==1 :
                return(self.article.returnformes()+"\n"+"推："+self.message)
            else:
                return(self.article.returnformes()+"\n"+"噓："+self.message)
    
    print_log("Parsedata.py open")
    tempart=myarticle() #save for temporary article
    tempuser=user() #for temporary user(author)
    tempmessage=message()
    allarticle=[myarticle() for _ in range(1)]              #all articles
    alluser=[user() for _ in range(1)]                      # all users 
    allmessage=[message() for _ in range(1)]              #all message in all articles
    allmessageinonearticle=[message() for _ in range(1)]  #all message in one articles
    checkforarticlename=0                                   # condition to get the title 
    checkforexistauthor=-1                                  # condition to check if there is an exist author in DB
    flagforfirsttime=0                                      #pass the first time
    flagforArticleContent=0
    maincontent=""  # content
    flagtodevidetimefromart=0 # to devide the time from maincontent
    ipaddress=""
    articleaddress=""
    forautohr=1
    fortitleandtime=1
    check=None
    tempauthor=None
    
    for data in alldataincrawl.split('\n'):
        
        avoidduplicatetitle=0
        data=data.split('\n')[0]#data.split(a,b)[0] split for b+1 times
        #if "Gossiping" in data:
         #   continue
        if "imgur.com" in data:
            continue
        elif "→ " in data: 
            data=data.replace("→ ","答")     # deal with unfinished message 
            ouputdata=ouputdata+data+"\n"
            data=data.replace("答","",1)
            for i in range(numbersOfmessage+1):     
                if i==0:
                    continue
                else:
                    mesname=allmessageinonearticle[i].getname()     # if data = 推 asiasssh: 這隻好眼熟 是不是G什麼F什麼的作品 好像是空戰類型? 05/09 11:21
                    mescontent=allmessageinonearticle[i].getmes() #tempallmescon=這隻好眼熟 是不是G什麼F什麼的作品 好像是空戰類型? 05/09 11:21
                    tempname=data.split(':',1)[0]                  # tempname= asiasssh
                    #print_log(mesname,tempname)
                    #if i ==4:
                     #   sys.exit(1)
                    if mesname==tempname:
                        length=len(mescontent)
                        time =str( mescontent[length-11:])
                        tempmescon= mescontent[:length-11]                       #tempmescon=這隻好眼熟 是不是G什麼F什麼的作品 好像是空戰類型?
                        tempdata=data.split(':',1)[1].replace(" ","",1) 
                        lengthtwo=len(tempdata)
                        tempdata=tempdata[:lengthtwo-11]    # seperate the message and time
                        savecontent=tempmescon+tempdata+time
                        allmessageinonearticle[i].setmessage(savecontent)
                        allmessage[i].setmessage(savecontent)
                        for one in tempart.getboo():
                            name=one.split(':',1)[0]
                            if name==tempname:
                                one=name+":"+savecontent
                        for one in tempart.getpush():
                            name=one.split(':',1)[0]
                            if name==tempname:
                                one=name+":"+savecontent     
                        #print_log(mesname+"\n"+tempmescon+tempdata+time)
                        break
            continue 

        
        if flagforArticleContent==1 : 
            if "推 " not in data and "噓 " not in data: 
                maincontent=maincontent+data  # content for one article

        if "發文者(Author): " in data :
            flagforArticleContent=0  # content initialize
            
            
            if checkforexistauthor>=0:  # if there exists an author , append article to user's db
                tempart.setid(idforArticle)
                idforArticle+=1
                tempart.setcontent(maincontent) #set main content to tempart
                tempart.setip(ipaddress)
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
=======
                tempart.seturl(articleaddress)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
                allarticle.append(tempart)  #append temp article to all articles
                alluser[checkforexistauthor].setarticle(tempart) #save article in user class
                checkforexistauthor=-1
                #allmessageinonearticle[1].print_logmes()
                
                
                for i in range(numbersOfmessage+1): 
                    if i==0:
                        continue
                    else:
                        allmessageinonearticle[i].setarticle(tempart)   # save article into message class
            else:
                if flagforfirsttime>0:  # to avoid first loop
                    tempart.setid(idforArticle)
                    idforArticle+=1
                    tempart.setcontent(maincontent) #set main content to tempart
                    tempart.setip(ipaddress)
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
=======
                    tempart.seturl(articleaddress)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
                    allarticle.append(tempart)  #append temp article to all articles
                    tempuser.setid(idforUser)
                    idforUser+=1
                    tempuser.setarticle(tempart) #set article to  tempuser 
                    alluser.append(tempuser) #append temp user to user's db


                    for i in range(numbersOfmessage+1): 
                    
                        if i==0:
                            continue
                        else:
                            allmessageinonearticle[i].setarticle(tempart)

            #print_log(tempart.author)

            tempart=myarticle()             #initialize
            tempuser=user()                 #initialize
            allmessageinonearticle=[message() for _ in range(1)] 
            
            tempauthor=data.replace("發文者(Author): ","")
            nickname=""
            lengthforauthor=len(tempauthor.split(' ',1))
            if lengthforauthor>1:
                temp=tempauthor.replace("  "," ")
                tempauthor=temp.split(' ',1)[0]
                nickname=temp.split(' ',1)[1]
            tempart.inputauthor(tempauthor)   # save author into article class
            
                    
            numbersOfArticle=numbersOfArticle+1 # number of article
            if tempauthor not in author:  #if the author not in the exist list 
                author=author+tempauthor+"\n"
                numbersOfAuthor=numbersOfAuthor+1
                
                tempuser.inputname(tempauthor) #save name into user name
                tempuser.inputnickname(nickname)
            else:
                for i in range(numbersOfAuthor+2):  # check thers is already an extist user 
                    if tempauthor == alluser[i].getname():
                        checkforexistauthor=i
                        #print_log("aa") #not finished
                
            checkforarticlename=1  # condition to get the title
            numbersOfmessage=0 #initialize
            maincontent=""
            ipaddress=""
            articleaddress=""
            
        tempmessage=message()   #initialize

        if "主題(Title): " in data :
            tempartname=data.replace("主題(Title): ","")
            tempart.inputarticlename(tempartname)
        if "時間(Time): " in data : 
            arttime=data.replace("時間(Time): ","")
            tempart.settime(arttime)
            flagforArticleContent=1
            
        if "噓 " in data:
            if "答" in data[0]:
                continue
            flagforArticleContent=0 #avoid unnecessory messenge in article content
            tempart.booplus()
            ouputdata=ouputdata+data+"\n" #alldata is the data that already filtered noises
            tempart.saveBoomessage(data)
            
            data=data.replace("噓 ","",1)
            length=len(data.split(':',1))
            if length==2:
                data=data.split(':',1)
                tempmessage.setarticleid(idforArticle)
                tempmessage.setname(data[0])    # parse data
                tempmessage.setBoo()
                tempmessage.setmessage(data[1].replace(" ","",1))
                allmessageinonearticle.append(tempmessage)  # append temp message
                allmessage.append(tempmessage)
                numbersOfmessage=numbersOfmessage+1
            continue
            
        if "推 " in data :
            if "答" in data[0]:
                continue
            flagforArticleContent=0 #avoid unnecessory messenge in article content
            tempart.pushplus()
            ouputdata=ouputdata+data+"\n" #alldata is the data that already filtered noises
            tempart.savePushmessage(data)

   
            data=data.replace("推 ","",1)
            length=len(data.split(':',1))
            if length == 2:
                data=data.split(':',1)
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
            #print(data[0],data[1])
=======
            #print_log(data[0],data[1])
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
                tempmessage.setarticleid(idforArticle)
                tempmessage.setname(data[0])   #parse data
                tempmessage.setmessage(data[1].replace(" ","",1))
                tempmessage.setPush()
                allmessageinonearticle.append(tempmessage)
                allmessage.append(tempmessage)
                numbersOfmessage=numbersOfmessage+1
            
            continue
        if "Ipaddress:" in data:
            ipaddress= data[10:]
        if "文章網址(url):" in data:
            articleaddress=data[10:]
            

        ouputdata=ouputdata+data+"\n" #alldata is the data that already filtered noises
        flagforfirsttime=1
   #print_log(ouputdata)
    with open("download/alldata.txt", "a",encoding="UTF-8") as text_file: #save the data into Gossiping.txt
            text_file.write(ouputdata)
            text_file.close() #close the file
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
    print("Author:",idforUser)
=======
    print_log("id_for_user_include_Author:",idforUser)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
          
    flag=0

    otheruser=[user() for _ in range(1)]

    for mes in allmessage:  #add message to user class
        if flag<1:
            flag=flag+1
            continue
        else:
            flag2=0
            flagforexistuser=0
            for oneuser in alluser:
                if flag2<1:
                    flag2=flag2+1
                    continue
                userID=oneuser.getname()
            # print_log(userID,mes.getname())
                if userID == mes.getname():   # if user exists in user database, which means the user has at least one article
                    oneuser.setmes(mes)
                    #print_log(oneuser.getname(),mes.getname())
                    flagforexistuser=1
                    break
            
            if flagforexistuser==0: # check if user exist in otheruser
                flag3=0
                increaseuser=0

                for person in otheruser:   
                    if  flag3<1:
                        flag3=flag3+1
                        continue
                    userID=person.getname()   
                    if  mes.getname() == userID:# user not exist in DB, but he/she has at least one message
                        person.setmes(mes)
                        increaseuser=1
                        break
                if increaseuser==0:  
                    temp=user()
                    temp.inputname(mes.getname())
                    temp.setmes(mes)
                    temp.setid(idforUser)
                    idforUser+=1    
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
                    #print(temp.getname())
    #                   temp.printall()
=======
                    #print_log(temp.getname())
    #                   temp.print_logall()
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
                    otheruser.append(temp)

    writer=alluser # record for the people at least write one article
    tempflag=0
    for user in otheruser:
        if tempflag==0:
            tempflag=tempflag+1
            continue
        #print_log(user.getname())
        alluser.append(user)   


    print_log("Parsedata.py successfuly done")
    test=0
    print_log("start to insert to database")
    #client = MongoClient("localhost")

<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
    print("Author+Message:",idforUser)
=======
    print_log("id_for_user_Author_add_Commentor:",idforUser)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py



    ####### start to insert data into MongoDB
    for user in alluser:
        
        tempuser=None
        collection=db["User"]
        if collection.find_one({"Name":user.getname()})!=None:
            tempuser=collection.find_one({"Name":user.getname()}) # find if there is exist user in mongodb
        
        if tempuser!=None:
            #print_log(tempuser["Article"])
            artinuser=[myarticle() for _ in range(0)]
            mesinuser=[message() for _ in range(0)]
            artinuser=tempuser["Article"]# find the exist user's article
            mesinuser=tempuser["Message"]
        else:
            mesinuser=None
            artinuser=None
        #print_log(user.getname())     #insert the user data into MongoDB
        Articlelist=[]
        insertArticle={"Articlename":"",
                        "id":-1,
                        "Time":"",
                        "Author":"",
                        "IPaddress":"",
                        "URL":"",
                        "Content":"",
                        "Boo":[""],
                        "Push":[""]
                        
                    }
        Boolist=[]
        Pushlist=[]
        
        
        meslist=[]
        insertMessage={"ArticleName":"",
                    "React":"",
                    "Message":"" 
                    }

        insertUser={"Name":"",
                    "id":-1,
                    "Nickname":"",
                    "CorrelatedUser":[],
                    "Article":[""],
                    "Message":[""]
                    }     #initialize for user 
        #
        if test <=1:
            test=test+1
            continue

        insertUser["Name"]=user.getname()
        insertUser["Nickname"]=user.getnickname()
        insertUser["id"]=user.getid()
        tempart=user.getarticle()
        flag4=0
        artnum=user.countartnum()
        
        if artnum>0:  # if one user has at least one article
            for art in user.getarticle(): # insert user's article into user collection
                if flag4==0:
                    flag4=flag4+1
                    continue
                checkexistart=0
                if artinuser!=None:
                    if len(artinuser)>0:
                        for existart in artinuser: # if the article has been saved in mongodb, continue
                            if existart=="":
                                continue
                            if existart["Articlename"]==art.getarticlename():#check article name 
                                if existart["Author"]==art.getauthor():
                                    if len(existart["Boo"])==art.getboonum():
                                        if len(existart["Push"])==art.getpushnum(): # check Boo and Push number                             
                                            checkexistart=1
                                            break

                if checkexistart==1:
                    print_log("Article exists in User collection with no any change") #Due to Article with no changes. we skip it 
                    continue

                insertArticle={"Articlename":"",
                               "id":-1,
                               "Time":"",
                               "Author":"",
                               "IPaddress":"",
                               "URL":"",
                               "Content":"",
                               "Boo":[""],
                               "Push":[""]
                               
                             }
                insertArticle["Articlename"]=art.getarticlename() 
                insertArticle["Author"]=art.getauthor()
                insertArticle["Content"]=art.getcontent()
                insertArticle["Time"]=art.gettime()
                insertArticle["IPaddress"]=art.getip()
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
=======
                insertArticle["URL"]=art.geturl()
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
                insertArticle["id"]=art.getid()
                for mes in art.getboo():  # set boo message into article class
                    if mes.find(":")==-1:
                        continue
                    name = mes.split(':',1)[0]#data.split(a,b)[0] split for b+1 times  
                    message= mes.split(':',1)[1].replace("  "," ")    # devide mes into Name content Time
                    a=len(message)
                    time=message[a-11:]
                    message=message[:a-11]
                   
                    Boo={"Name":"",
                    "Content":"",
                    "Time":""}
                    Boo["Name"]=name
                    Boo["Content"]=message
                    Boo["Time"]=time
                    
                    Boolist.append(Boo)

                insertArticle["Boo"]=Boolist
                
                for mes in art.getpush():
                    #print_log(mes)
                    if mes.find(":")==-1:
                        continue
                    name = mes.split(':',1)[0]#data.split(a,b)[0] split for b+1 times  
                    message= mes.split(':',1)[1].replace("  "," ")    # devide mes into Name content Time
                    a=len(message)
                    time=message[a-11:]
                    message=message[:a-11]
                   
                    Push={"Name":"",
                    "Content":"",
                    "Time":""}
                    Push["Name"]=name
                    Push["Content"]=message
                    Push["Time"]=time
                    
                    Pushlist.append(Push)
                
                insertArticle["Push"]=Pushlist

                
                
                collection=db["Article"]
                tempart=collection.find_one({"id":art.getid() })
                if  tempart != None:   ###################  modify the article in Article colleciotn
                    collection=db["Article"] #choose Article collection

                    print_log("Article exists in Article collection but updates with message below","Articleid :",tempart["id"])
                    collection.update_one(    
                        {"Articlename":art.getarticlename(),"Author":user.getname() },
                        {
                        "$set":{
                           "Boo":insertArticle["Boo"],
                           "Push":insertArticle["Push"]
                        }
                        }

                        )
                    
                    collection=db["User"]###################  modify the article in User collection 
                    collection.update_one(
                        {"Name":user.getname(),"Article.Articlename":art.getarticlename()},
                        {
                            "$set":{
                                "Article.$.Boo":insertArticle["Boo"],
                                "Article.$.Push":insertArticle["Push"]
                            }
                        }
                        )

                    # for updating the relation in every one article
            
                    
                else :
                    collection=db["Article"]    #choose Article collection
                    collection.insert(insertArticle) # insert the article in article collection into mongoDB
                    Articlelist.append(insertArticle)
                    print_log("New Article enter:", insertArticle["id"])
                    collection=db["Relation"] 
                        
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
                getrelationfromarticle(Pushlist+Boolist,art.getid(),alluser)

=======
                getrelationfromarticle(Pushlist+Boolist,art.getid(),alluser,user.getid())
                print_log("Relation calculated","Article id:"+str(art.getid()))
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
                #articlelist=art.returnall()
                #print_log(articlelist)

            insertUser["Article"]=Articlelist   # record the article in user collection 



        flag5=0
        #print_log(user.countmesnum())
        if user.countmesnum()>0:        # recoed the mes the user has left
        # print_log(user.getname(),user.countmesnum())
            for mes in user.getmessage():
                if flag5==0:
                    flag5=flag5+1
                    continue
                insertMessage={"ArticleName":"",
                    "Articleid":-1,
                    "React":"",
                    "Message":"" 
                    }     
                insertMessage["ArticleName"]=mes.getarticle()
                insertMessage["React"]=mes.getreact()
                insertMessage["Message"]=mes.getmes()
                insertMessage["Articleid"]=mes.getarticleid()
                jump=0

                if mesinuser!=None:
                    if len(mesinuser)>0:    
                        for onemes in mesinuser:  # if mes has been save into MongoDB, continue to neglect it                         
                            if onemes=="":
                                continue
                            if onemes["ArticleName"]==mes.getarticle():
                                if onemes["Message"]==mes.getmes():
                                    
                                    jump=1
                                    break
                        if jump==1:
                            continue
                        else:
                            meslist.append(insertMessage)
                else:
                    meslist.append(insertMessage)

            insertUser["Message"]=meslist


        collection=db["User"] #choose User collection
        
        if  tempuser != None:    # if the user exist in MongoDb, update rather than insert a new article and message
            if insertArticle!=[""]:
                collection.update_one(
                    {"Name":user.getname()},
                    {
                    "$set":{
                        "Article":tempuser["Article"]+insertUser["Article"]  # update the article in User collection in MongoDB
                        
                    }
                    }
                )
            if insertMessage!=[""]:
                collection.update_one(
                    {"Name":user.getname()},
                    {
                    "$set":{
                          # update the article in User collection in MongoDB
                        "Message":tempuser["Message"]+insertUser["Message"]
                    }
                    }
                )
        else :    
            collection.insert(insertUser) # insert the user into mongoDB
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
=======
           # print_log("insert new User")
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
        
    print_log("Successfully insert User and Article to mongoDB")  


<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
    
    #print (alldata)
    #allmessage[1].printeverything()
    #for i in range(numbersOfmessage):
    #   if i ==0 :
    #       continue
    #   allmessage[i].printmes()
    #for i in range(numbersOfArticle+1):
    #    allarticle[i].printall()
    #for i in range(numbersOfAuthor+1):
    #  alluser[i].printall() 
    #alluser[16].printall()
    #alluser[16].printall()

def getrelationfromarticle(meslist,artid,alluser):   # update relation value when update article 
    print("Relation calculated")
=======

def getrelationfromarticle(meslist,artid,alluser,userid):   # update relation value when update article 
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
    lengthofmes=len(meslist)
    for i in range(lengthofmes):
        collection=db["User"]
        temp=collection.find_one({"Name":meslist[i]["Name"]})
        if temp!=None:
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
=======
            #update relation with author and commentor
            if temp["id"] > userid:
                updaterelation(temp["id"],userid,artid)
            else:
                updaterelation(userid,temp["id"],artid)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
            for j in range(i,lengthofmes):
                temptwo=collection.find_one({"Name":meslist[j]["Name"]})    # if two users exist in database
                if temptwo!=None:
                    if temp["Name"]==temptwo["Name"]:
                        continue
                    if temp["id"]<temptwo["id"]:
                        updaterelation(temp["id"],temptwo["id"],artid)
                    else:
                        updaterelation(temptwo["id"],temp["id"],artid)  
                else:                                   # if one of two user is not in database
                    tempid=-1
                    for tempuser in alluser:
                        if tempuser.getname()== meslist[j]["Name"]:
                            tempid=tempuser.getid()
                            break
                    updaterelation(temp["id"],tempid,artid)
        else:                                   # if two users are both not in database
            tempid=-1
            for tempuser in alluser:
                if tempuser.getname()== meslist[i]["Name"]:
                    tempid=tempuser.getid()
                    tempname=tempuser.getname()
                    break
<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
=======
            if tempid < userid:
                updaterelation(tempid,userid,artid)
            else:
                updaterelation(userid,tempid,artid)
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
            for j in range(i,lengthofmes):
                temptwo=collection.find_one({"Name":meslist[j]["Name"]})
                if temptwo!=None:
                    if tempname==temptwo["Name"]:
                        continue
                    updaterelation(temptwo["id"],tempid,artid)
                else:
                    temp2id=-1
                    for tempuser in alluser:
                        if tempuser.getname()== meslist[j]["Name"]:
                            temp2id=tempuser.getid()
                            break
                    if tempid==temp2id:
                        continue
                    if tempid<temp2id:
                        updaterelation(tempid,temp2id,artid)
                    else:
                        updaterelation(temp2id,tempid,artid)                                
                
        

def updaterelation(userAid,userBid,Articleid):  # update the relation collection
    collection=db["Relation"]
    relation=collection.find_one({"user1id":userAid,"user2id":userBid })
    duplicateid=0
    
    if relation!=None:
        #print_log(artidlist["user1id"])
        artidlist=relation["Articleid"]
        if artidlist != None:
            
            for existid in artidlist:
                if existid==Articleid:
                    duplicateid=1
                    break
            if duplicateid!=1:  # avoid duplicated count message in one article
                artidlist.append(Articleid)
               
                collection.update_one(
                {"user1id":userAid,"user2id":userBid },
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
        oneRelation["user1id"]=userAid
        oneRelation["user2id"]=userBid
                # record correlated user id in user with larger id in User collection 
        updateCorrelateduser(userAid,userBid)
            

        oneRelation["Intersection"]+=1
        intersectionarticlelist=[]
        intersectionarticlelist.append(Articleid)    
        oneRelation["Articleid"]=intersectionarticlelist

        collection=db["Relation"]
        collection.insert(oneRelation) 
           
        
    
        
    
def updateCorrelateduser(userAid,userBid):  # update correlated user id in user collection, userA's id is smaller than userB's
    collection=db["User"]
    tempuser=collection.find_one({"id":userBid})
    if tempuser!=None:
        if len(tempuser["CorrelatedUser"])>0:
            tempcorrelateduserid=tempuser["CorrelatedUser"]
            check=0
            for exist in tempcorrelateduserid:
                if exist==userAid:
                    check=1
                    break
            if check==0:
                tempcorrelateduserid.append(userAid)

        else:
            tempcorrelateduserid=[]
            tempcorrelateduserid.append(userAid)

        collection.update_one(
        {"id":userBid },
        {
        "$set":{
            "CorrelatedUser":tempcorrelateduserid
        }
        })


<<<<<<< HEAD:crawler/python practice/crawlGossiping.py
# def relations(userA, userB):
#     articleSetA=set()
#     articleSetB=set()

#     listA=userA['Message']
#     listB=userB['Message']

#     if listA[0] != '':
#         for message in listA:
#             if message=="":
#                 continue
#             articleSetA.add(message['ArticleName'])
#     if listB[0] != '':
#         for message in listB:
#             if message=="":
#                 continue
#             articleSetB.add(message['ArticleName'])
    
#     if len(articleSetA)==0 and len(articleSetB) == 0 :
#         articleIntersection=[]

#     else:
#         articleIntersection=articleSetA.intersection(articleSetB)
#         #articleUnion=articleSetA.union(articleSetB)
#         #relationValue=len(articleIntersection)/len(articleUnion)


#         oneRelation={       #insert to mongo DB
#                 "user1id":-1,
#                 "user2id":-1,
#                 "Intersection":0,
#                 "Articleid":[] # may have a lot of relation with otehr users
#         }
#         oneRelation["user1id"]=userA["id"]
#         oneRelation["user2id"]=userB["id"]

#         intersectionarticlelist=[]
#         oneRelation["Intersection"]=len(articleIntersection)

#         if len(articleIntersection)>0:      # record correlated user id in user with larger id in User collection 
#             updateCorrelateduser(userA["id"],userB["id"])
            

#         collection=db["Article"]
#         if len(articleIntersection)>0:
#             for one in articleIntersection:  # record the article id the relation happen
#                 oneid=collection.find_one({"Articlename":one})
#                 if oneid!=None:
#                     intersectionarticlelist.append(oneid["id"])
#             oneRelation["Articleid"]=intersectionarticlelist

#             collection=db["Relation"]
#             collection.insert(oneRelation)
#         print("Relation id:" ,userA["id"],userB["id"])
        
        



# def allPairs(db, userCollection): # count relation
#     userArray=userCollection.find()

#     for i in range(0,userArray.count()-1):
#         for j in range(i+1,userArray.count()):
#             userA=userArray[i]
#             userB=userArray[j]

#             relations(userA, userB) 
#             j=j+1

#         i=i+1
        
#     print("Successfully insert to database for all relation")    
    


# import logging 
# setting log config
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


# create a file handler
# handler = logging.FileHandler('./download/LogDebug.txt')
# handler.setLevel(logging.DEBUG)

# handler2 = logging.FileHandler('./download/LogInfo.txt')
# handler2.setLevel(logging.INFO)

# create a logging format
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# handler2.setFormatter(formatter)

# add the handlers to the logger
# logger.addHandler(handler)
# logger.addHandler(handler2)

# def setlogDEBUG(data):
#     logger.debug(data)
# def setlogINFO(data):
#     logger.info(data)

=======
>>>>>>> c46fc3c8e239d651af47a0ec1edac424675a19ca:crawler/crawlGossiping.py
if __name__ == '__main__' :
    main(sys.argv)


