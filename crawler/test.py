#data= "推 jokc7839: 反串？ 04/15 12:16"
#data=data.replace("推 ","",1)
#data=data.split(':',1)#data.split(a,b)[0] split for b+1 times
#print(data[0],"\n",data[1].replace(" ","",1))

dd="sas"
#print(dd[0])
print(dd)

x=" "
with open("download/test.txt", "r") as text_file:
    x=text_file.read()
with open("download/test2.txt", "r") as text_file:
    y=text_file.read()   
z=x+y
with open("download/test2.txt", "w") as text_file:
    text_file.write(z)
   
 #   text_file.write("saaa")
 #  text_file.close()


    #close the file
#month = dict (Jan=1,Feb=2,Mar=3,Apr=4,May=5,Jun=6,Jul=7,Aug=8,Sep=9,Oct=10,Nov=11,Dec=12)
        
#monthlist= list(month.items())

#print(monthlist[0][0])



