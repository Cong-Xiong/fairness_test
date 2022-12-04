import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
import statistics as stat
import ReadvCPU

cpuMin = 1
cpuMax = 12

parser = ReadvCPU.Parser(cpuMin, cpuMax,"./resources/")
parser.read_vCPUs()


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


def analyseMigrations():
    server_vm = parser.server_vm
    for cpu in server_vm.values():
        for node in cpu:
            tmp = 0
            jumpNode = None
            for c in server_vm.values():
                tryNode = searchMigrationCPU(node, c)
                if(tryNode is None):
                    continue
                if (tmp < tryNode.migratePoint):
                    tmp = tryNode.migratePoint
                    jumpNode = tryNode
            node.jumpNode = jumpNode

analyseMigrations()
# parser.analyse(parser.server_vm,"redis")
i=0
for cpu in parser.server_vm.values():
    i+=1
    none_count = 0
    count = 0
    for node in cpu:
        count+=1
        if(node.jumpNode is None):
            none_count+=1
    print("CPU"+str(i)+" not find count: "+str(none_count)+"/"+str(count))