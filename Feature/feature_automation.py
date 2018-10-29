import subprocess
import sys

def launch(date,day_range, official, inter_gate):

    p_grouping = subprocess.Popen("python grouping.py {} {} {} {}".format(date, day_range, official, inter_gate), shell=True)
    return_code = p_grouping.wait()
    if return_code != 0:
        print("grouping error")
        exit(1)

    p_keyword = subprocess.Popen("python keyword.py {} {} {} {}".format(date, day_range, official, inter_gate), shell=True)
    return_code = p_keyword.wait()
    if return_code != 0:
        print("keyword error")
        exit(1)

    p_emi = subprocess.Popen("python df_chisqmi.py {} {} {} {}".format(date, day_range, official, inter_gate), shell=True)
    return_code = p_emi.wait()
    if return_code != 0:
        print("emi error")
        exit(1)

if __name__ == "__main__":
    launch("2018-09-30", 7, 0, 15)
