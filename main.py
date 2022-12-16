import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
import statistics as stat
from scipy import stats
import ReadvCPU
import Simulation


def searchMigrationCPU(node, list):
    time = node.migratePoint
    for n in list:
        if n.id == node.id:
            return None
        if n.start >= time:
            return None
        else:
            if n.migratePoint > time:
                return n


def analyseMigrations(parser):
    server_vm = parser.server_vm
    for cpu in server_vm.values():
        searched_Nodes = [0 for _ in range(parser.pCPU_max - parser.pCPU_min + 1)]
        for node in cpu:
            tmp = 0
            index = 0
            for c in server_vm.values():
                tryNode = searchMigrationCPU(node, c[searched_Nodes[index]:])
                if (tryNode is None):
                    index += 1
                    continue
                node.jumpNodes.append((tryNode, tryNode.migratePoint - node.migratePoint))
                searched_Nodes[tryNode.id - parser.pCPU_min] = tryNode.No
                index += 1


def cpuResult(parser):
    i = 0
    for cpu in parser.server_vm.values():
        i += 1
        none_count = 0
        count = 0
        for node in cpu:
            count += 1
            if (node.getJumpNode() is None):
                none_count += 1
        print("CPU" + str(i) + " not find count: " + str(none_count) + "/" + str(count))


def searchJump(node):
    time = 0
    count = 0
    n = node
    while (True):
        if n.jumpNode is None:
            break
        n = n.jumpNode
        count += 1
        time += n.jumpDuration
    return time, count
    # print("Extension Time: "+ str(time))
    # print("Migrate count: " + str(count))


extension_time = []
migrate_count = []


def serchOneCPU(parser):
    for cpu in parser.server_vm.values():
        for node in cpu:
            (t, c) = searchJump(node)
            extension_time.append(t)
            migrate_count.append(c)
        break


def createParser(addr):
    cpuMin = 1
    cpuMax = 12
    parser = ReadvCPU.Parser(cpuMin, cpuMax, addr)
    parser.read_vCPUs()
    return parser


def showRunTimes(runtimes):
    for i in runtimes:
        print(str(i) + "\t", end="")
    print("")


# //////////////////////////////////////////////////////
# def temp2(parser):
#     if(parser.server_vm!=0):
#         parser.analyse2(parser.server_vm)
#     if (len(parser.b1) != 0):
#         parser.analyse2(parser.b1)
#     if (len(parser.b2) != 0):
#         parser.analyse2(parser.b2)
#     if (len(parser.b3) != 0):
#         parser.analyse2(parser.b3)
# def temp():
#     p2 = createParser("./rate2/")
#     p3 = createParser("./rate3/")
#     p4 = createParser("./rate4/")
#     temp2(p2)
#     temp2(p3)
#     temp2(p4)
s12 = Simulation.Simulate(12)
s8 = Simulation.Simulate(8)
s4 = Simulation.Simulate(4)
s2 = Simulation.Simulate(2)


def temp_print(parser, file_name):
    s12.run(parser)
    with open(file_name+"t12", "w") as f:
        f.write(file_name+"t12")
        [f.write(str(x)+"\t") for x in s12.runtimes]
        f.write("\n")
    s8.run(parser)
    with open(file_name+"t8", "w") as f:
        [f.write(str(x)+"\t") for x in s8.runtimes]
        f.write("\n")
    s4.run(parser)
    with open(file_name + "t4", "w") as f:
        [f.write(str(x) + "\t") for x in s4.runtimes]
        f.write("\n")
    s2.run(parser)
    with open(file_name + "t2", "w") as f:
        [f.write(str(x) + "\t") for x in s2.runtimes]
        f.write("\n")


def temp_fairness():
    p22 = createParser("./rate2/2/")
    analyseMigrations(p22)
    temp_print(p22,"rate22")
    p23 = createParser("./rate2/3/")
    analyseMigrations(p23)
    temp_print(p23, "rate23")
    p24 = createParser("./rate2/4/")
    analyseMigrations(p24)
    temp_print(p24, "rate24")


    p32 = createParser("./rate3/2/")
    analyseMigrations(p32)
    temp_print(p32, "rate32")
    p33 = createParser("./rate3/3/")
    analyseMigrations(p33)
    temp_print(p33, "rate33")
    p34 = createParser("./rate3/4/")
    analyseMigrations(p34)
    temp_print(p34, "rate34")

    p42 = createParser("./rate4/2/")
    analyseMigrations(p42)
    temp_print(p42, "rate42")
    p43 = createParser("./rate4/3/")
    analyseMigrations(p43)
    temp_print(p43, "rate43")
    p44 = createParser("./rate4/4/")
    analyseMigrations(p44)
    temp_print(p44, "rate44")


# pd.Series(extension_time).quantile(np.arange(0, 1, 0.1, dtype=float))
