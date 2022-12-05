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

def createParser(min,max):
    cpuMin = min
    cpuMax = max
    parser = ReadvCPU.Parser(cpuMin, cpuMax, "./resources/30s/")
    parser.read_vCPUs()
    return parser

def showRunTimes(runtimes):
    for i in runtimes:
        print(str(i)+"\t", end = "")
    print("")
def showDiffCPUs():
    parser12 = createParser(1,4)
    analyseMigrations(parser12)
    cpuResult(parser12)

    simulator1 = Simulation.Simulate(1)
    simulator4 = Simulation.Simulate(4)
    # simulator8 = Simulation.Simulate(8)
    # simulator12 = Simulation.Simulate(12)

    simulator1.run(parser12)
    simulator4.run(parser12)
    # simulator8.run(parser12)
    # simulator12.run(parser12)

    showRunTimes(simulator1.runtimes)
    showRunTimes(simulator4.runtimes)
    # showRunTimes(simulator8.runtimes)
    # showRunTimes(simulator12.runtimes)

showDiffCPUs()

# pd.Series(extension_time).quantile(np.arange(0, 1, 0.1, dtype=float))
