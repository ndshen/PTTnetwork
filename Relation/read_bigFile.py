import sys, os, math
data_file_dir = os.path.join(os.path.dirname(__file__), '../../tempData/outside-relation/')

def readBig():
    maxId = 0
    with open(data_file_dir+sys.argv[1], "r") as f:
        lines = f.read().split('\n')
        for i, line in enumerate(lines):
            if line == '':
                print(i)
                continue
            # print(line)
            node = line.split('\t')
            if math.ceil(float(node[2])) == 0:
                print(line)
            # if int(node[0]) == 17971 or int(node[1]) == 17971:
            #     print(line)
            # if int(node[0]) > maxId:
            #     maxId = int(node[0])
            # if int(node[1]) > maxId:
            #     maxId = int(node[1])   
            # if int(node[0]) < 0 or int(node[1]) < 0:
            #     print('!')
            # if i == int(sys.argv[2]):
            #     break
        print(len(lines), maxId)

# python read_bigFile.py [file name] [lines to print]

def deleteZeroRelation(data_file, new_data_file):
    with open(data_file, "r") as oldF, open(new_data_file, "w") as newF:
        lines = oldF.read().split('\n')
        for line in lines:
            if line == '':
                continue

            node = line.split('\t')
            if math.ceil(float(node[2])) != 0:
                newF.write(line + "\n")

if __name__ == "__main__":
    deleteZeroRelation(data_file_dir+sys.argv[1], data_file_dir+sys.argv[2])