import sys
import subprocess
host = '127.0.0.1:27020'
dbUser='rootNinja'
dbName='test_624'
collectionName='Group'
fileName='group.json'
def main(args):
    with open(args[1], "r") as f:
        section=f.read().split('"links": [')
        group=section[0][:-8]
        group=group.split('\n',2)[2]
        group='[\n'+group+'\n]'
        with open(fileName, "w") as j:
            j.write(group)
    subprocess.Popen(['mongoimport', 
                    '--host', host,
                    '-u', dbUser,
                    '-p', args[2],
                    '--authenticationDatabase','admin',
                    '--db', dbName, 
                    '--collection', collectionName, 
                    '--file' ,fileName ,
                    '--jsonArray'])



if __name__ == "__main__":
    main(sys.argv)