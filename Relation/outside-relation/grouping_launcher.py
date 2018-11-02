import sys
import subprocess

def launch(inter_gate, official, dbPWD, date, day_range):
    p = subprocess.Popen("python overall_relation.py {} {} {} {} {}".format(inter_gate, official, dbPWD, date, day_range))
    return_code = p.wait()
    if return_code != 0:
        print("[ERROR] date: {}, day_range: {}, inter_gate: {}".format(date, str(day_range), str(inter_gate)))
        exit(1)


launch(10, 0, "swordtight", "2018-09-23", 7)
launch(10, 0, "swordtight", "2018-09-16", 7)
launch(10, 0, "swordtight", "2018-10-28", 7)

