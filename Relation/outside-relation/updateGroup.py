import subprocess, sys, json
import pymongo

def main(fileName, date, db, pwd):
    group_document = group_reconstruct(fileName, date)

    command = "mongoimport --host 127.0.0.1:27020 --db {} -u rootNinja -p {} --authenticationDatabase admin --collection Group --file {} --jsonArray". format(db, pwd, fileName)
    p = subprocess.Popen(command, shell = True)
    result = p.wait()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("python updateGroup.py [group json] [dbName] [pwd]")
        exit(1)
    # main(sys.argv[1], sys.argv[2], sys.argv[3])


# get group from group.txt
def group_reconstruct(oldSLMoutputF, date):
    group_document = dict()
    group_ids= []
    groups = []
    with open (oldSLMoutputF) as data:
        group_info = json.loads(data.read())
        for info in group_info:
            if info['group'] not in group_ids:
                group_ids.append(info['group'])
                groups.append({'overall_group_users':[info['id']], 'overall_group_id': info['group'] })
            else:
                for group in groups:
                    if group['id'] == info['group']:
                        group['overall_group_users'].append(info['id'])
        
        group_ids.sort()

        group_document = {
            "date":date,
            "overall_groupID_list":group_ids,
            "overall_group_list":groups
        }

    # print('groups reconstruction finished')

    return group_document