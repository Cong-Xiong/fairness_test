import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
import statistics as stat
from decimal import Decimal

others = {}
test_length = []
KVM_nginx_list = {}
KVM_clone1_list = {}

# nginx represents IO VM
KVM_open_nginx_list = []
# clone1 represents Background VM
KVM_open_clone1_list = []


def toNano(t):
    return round(t * 1000000000)


def is_inlist(lst, name):
    for l in lst:
        if str(l) in name:
            return True
    return False


def group(name):
    #     put pid ... in nginx list
    if (is_inlist([3313, 3314, 3315, 3316], name)):
        return KVM_nginx_list
    #     put pid ... in clone1 list
    if (is_inlist([3373, 3374, 3375, 3376], name)):
        return KVM_clone1_list
    return others


def analyse(lst, name):
    keys = lst.keys()
    print("------------------------------")
    print(name + " analyse:")
    tmp = []
    s = 0
    for k in keys:
        tmp = tmp + lst[k]
        print("------------------------------")
        print(k + ":")
        print("average wake up time:\t" + str(toNano(stat.mean(lst[k]))) + "ns")
        print("stdev wake up time:\t" + str(toNano(stat.stdev(lst[k]))) + "ns")
        print("max wake up time:\t" + str(toNano(max(lst[k]))) + "ns")
        print("min wake up time:\t" + str(toNano(min(lst[k]))) + "ns")
        print("total runtime:\t" + str(sum(lst[k])) + "s")
        s += sum(lst[k])
    print("------------------------------")
    print(name + " average wake up time:\t" + str(toNano(stat.mean(tmp))) + "ns")
    print(name + " stdev wake up time:\t" + str(toNano(stat.stdev(tmp))) + "ns")
    print(name + " total runtime:\t" + str(s) + "s")
    print("total runtime%:\t" + str(round(s / test_length * 100, 4)) + "%")


pCPU_min = 1
pCPU_max = 4
pcpu_numbers = pCPU_max - pCPU_min + 1
# cpu 1-4
for i in range(pCPU_min, pCPU_max + 1):
    interval_start_time = 0
    tasks_runtime = {}
    Last_time_stamp = 0
    now_time_stamp = 0
    jump1 = 0
    cpu = str(i)

    with open("./" + "cpu" + cpu) as f:
        for line in f:
            if (len(line) < 20):
                continue
            # decode
            line_list = line.split()
            if (line_list[0] == "CPU" or line_list[0] == "SPICE"):
                task = line_list[1]
                now_time_stamp = Decimal(line_list[3].strip(':'))
            else:
                task = line_list[0]
                now_time_stamp = Decimal(line_list[2].strip(':'))
            # first line
            if (jump1 == 0):
                interval_start_time = now_time_stamp
                jump1 = 1
                Last_time_stamp = now_time_stamp
                continue
            #
            curr_runtime = now_time_stamp - Last_time_stamp
            if (tasks_runtime.get(task) is None):
                # new task
                tasks_runtime[task] = curr_runtime
                if (group(task).get(task) is None):
                    group(task)[task] = [(curr_runtime, Last_time_stamp, now_time_stamp)]
                else:
                    group(task)[task].append(curr_runtime, Last_time_stamp, now_time_stamp)

            else:
                # old task
                tasks_runtime[task] += curr_runtime
                #                    每次记录(时间片长度,开始时间,结束时间)
                group(task)[task].append((curr_runtime, Last_time_stamp, now_time_stamp))
            #
            Last_time_stamp = now_time_stamp

KVM_open_nginx_list.append(KVM_nginx_list)
KVM_open_clone1_list.append(KVM_clone1_list)
KVM_nginx_list = {}
KVM_clone1_list = {}
others = {}
test_length.append((now_time_stamp - interval_start_time) * pcpu_numbers)

# print
test_length = test_length[0]
print(str(pcpu_numbers) + "CPUs total interval length:\t" + str(test_length) + "s")
# analyse(KVM_open_nginx_list[0],"redis")
# analyse(KVM_open_clone1_list[0],"clone1")
print([x for x, _, _ in KVM_open_clone1_list[0]['0/KVM-3373']])
