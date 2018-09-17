import subprocess, sys

def main(fileName, db, pwd):
    command = "mongoimport --host 127.0.0.1:27020 --db {} -u rootNinja -p {} --authenticationDatabase admin --collection Group --file {} --jsonArray". format(db, pwd, fileName)
    p = subprocess.Popen(command, shell = True)
    result = p.wait()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python updateGroup.py [group json] [dbName] [pwd]")
        exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])