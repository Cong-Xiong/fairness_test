import os
import sys
import statistics as stat


class Node:
    def __init__(self, start, end, vCPUId):
        self.start = start
        self.end = end
        self.interval = end - start

        self.No = 0
        self.id = vCPUId
        self.migratePoint = end - 0.0006

        self.currTask = 0

        self.jumpNodes = []
        self.jumpDuration = 0

    def getJumpNode(self):
        if len(self.jumpNodes) == 0:
            return None
        self.jumpNodes.sort(key=lambda x: x[0].migratePoint, reverse=True)
        self.jumpNodes.sort(key=lambda x: x[0].currTask)
        return self.jumpNodes[0]


class Parser:
    def __init__(self, pCPU_min, pCPU_max, addr, v):
        self.pCPU_min = pCPU_min
        self.pCPU_max = pCPU_max

        self.others = {}
        self.tests_length = []
        self.server_vm = {}
        self.b1 = {}
        self.b2 = {}
        self.b3 = {}
        self.addr = addr + "/"
        self.possibleJumpCount = 0
        self.v1 = v[0]
        self.v2 = v[1]
        self.v3 = v[2]
        self.v4 = v[3]

    def toNano(self, t):
        return round(t * 1000000000)

    def is_inlist(self, lst, name):
        for l in lst:
            if str(l) in name:
                return True
        return False

    def analyse(self, lst, name):
        keys = lst.keys()
        print("------------------------------")
        print(name + " analyse:")
        tmp = []
        s = 0
        for k in keys:
            intervals = [x.interval for x in lst[k]]
            tmp = tmp + intervals
            print("------------------------------")
            print(k + ":")
            print("average wake up time:\t" + str(self.toNano(stat.mean(intervals))) + "ns")
            print("stdev wake up time:\t" + str(self.toNano(stat.stdev(intervals))) + "ns")
            print("max wake up time:\t" + str(self.toNano(max(intervals))) + "ns")
            print("min wake up time:\t" + str(self.toNano(min(intervals))) + "ns")
            print("total runtime:\t" + str(sum(intervals)) + "s")
            s += sum(intervals)
        print("------------------------------")
        print(name + " average wake up time:\t" + str(self.toNano(stat.mean(tmp))) + "ns")
        print(name + " stdev wake up time:\t" + str(self.toNano(stat.stdev(tmp))) + "ns")
        print(name + " runtime:\t" + str(s) + "s")
        print(name + " runtime%:\t" + str(round(s / sum(self.tests_length) * 100, 4)) + "%")
        print("------------------------------")
        print("runtime:\t" + str(sum(self.tests_length)))

    def analyseCPUs(self, lst):
        keys = lst.keys()
        tmp = []
        cpus = []
        s = 0
        for k in keys:
            intervals = [x.interval for x in lst[k]]
            tmp = tmp + intervals
            cpus.append(str(round(sum(intervals) / sum(self.tests_length) * 400, 4)) + "%")
            s += sum(intervals)
        cpus.append(str(round(s / sum(self.tests_length) * 100, 4)) + "%")
        return cpus

    def group(self, name):
        #     put pid ... in nginx list
        io = self.v1
        b1 = self.v2
        b2 = self.v3
        b3 = self.v4
        interval = self.pCPU_max - self.pCPU_min + 1
        if (io!=-1 and self.is_inlist(range(io, io + interval), name)):
            return self.server_vm
        #     put pid ... in clone1 list
        # clone1
        if (b1 !=-1 and self.is_inlist(range(b1, b1 + interval), name)):
            return self.b1
        # clone2
        if (b2 !=-1 and self.is_inlist(range(b2, b2 + interval), name)):
            return self.b2
        # clone
        if (b3 !=-1 and self.is_inlist(range(b3, b3 + interval), name)):
            return self.b3
        return self.others

    def addNo(self):
        for cpu in self.server_vm.values():
            No = 0
            for n in cpu:
                n.No = No
                No += 1

    def read_vCPUs(self):
        pcpu_numbers = self.pCPU_max - self.pCPU_min + 1
        # cpu 1-4
        for i in range(self.pCPU_min, self.pCPU_max + 1):
            start_time = 0
            tasks_runtime = {}
            Last_time_stamp = 0
            now_time_stamp = 0
            jump1 = 0
            cpu = str(i)

            with open(self.addr + "cpu" + cpu) as f:
                for line in f:
                    if (len(line) < 20):
                        continue
                    # decode
                    line_list = line.split()
                    if (line_list[0] == "CPU" or line_list[0] == "SPICE"):
                        task = line_list[1]
                        now_time_stamp = float(line_list[3].strip(':'))
                    else:
                        task = line_list[0]
                        now_time_stamp = float(line_list[2].strip(':'))
                    # first line
                    if (jump1 == 0):
                        start_time = now_time_stamp
                        jump1 = 1
                        Last_time_stamp = now_time_stamp
                        continue
                    #
                    curr_runtime = now_time_stamp - Last_time_stamp
                    node = Node((Last_time_stamp), (now_time_stamp), i)
                    if (tasks_runtime.get(task) is None):
                        # new task
                        tasks_runtime[task] = curr_runtime
                        if (self.group(task).get(task) is None):
                            self.group(task)[task] = [node]
                        else:
                            self.group(task)[task].append(node)
                    else:
                        # old task
                        tasks_runtime[task] += curr_runtime
                        self.group(task)[task].append(node)
                    #
                    Last_time_stamp = now_time_stamp

            self.tests_length.append((now_time_stamp - start_time))
        self.addNo()


# get arguments
args = sys.argv
vcpu_min = int(args[1])
vcpu_max = int(args[2])
vcpu_len = vcpu_max - vcpu_min + 1
p = os.popen("pwd")
pwd = str(p.readline().rstrip())
p.close()
# get vcpus
vcpulist = []
f = os.popen("cat /proc/vcpu_list_show")
for line in f:
    vcpulist.append(int(line.split()[3]))
f.close()
vcpulist.sort()
temp = vcpulist + [-1 for x in range(0, 100)]
vms = [temp[0], temp[0 + vcpu_len], temp[0 + 2 * vcpu_len], temp[0 + 2 * vcpu_len]]
# analyse trace
result = []
parser = Parser(vcpu_min, vcpu_max, pwd, vms)
parser.read_vCPUs()
if len(parser.server_vm) != 0:
    result.append(parser.analyseCPUs(parser.server_vm))
if len(parser.b1) != 0:
    result.append(parser.analyseCPUs(parser.b1))
if len(parser.b2) != 0:
    result.append(parser.analyseCPUs(parser.b2))
if len(parser.b3) != 0:
    result.append(parser.analyseCPUs(parser.b3))
import pandas as pd

cols = ["CPU " + str(x) for x in range(vcpu_len)]
cols.append("sum")
df = pd.DataFrame(result, columns = cols)
print(df)
