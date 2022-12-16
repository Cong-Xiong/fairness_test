class Simulate:
    def __init__(self, threadNo):
        self.threadNo = threadNo
        self.runtimes = []
        self.paths = {}


    def run(self, parser):
        for t in range(0, self.threadNo):
            self.findOneThreadPath(parser, list(parser.server_vm.values())[t][0])
        for t in range(0, self.threadNo):
            self.runtimes.append(self.collectTime(list(parser.server_vm.values())[t][0]))
        self.clear(parser)

    def findOneThreadPath(self, parser, node):
        currNode = node
        tmpList = []
        while (True):
            currNode.currTask += 1
            nextNode = currNode.getJumpNode()
            if (nextNode is None):
                if (len(list(parser.server_vm.values())[currNode.id - 1]) <= currNode.No + 1):
                    break
                currNode = list(parser.server_vm.values())[currNode.id - 1][currNode.No + 1]
                tmpList.append((currNode, (currNode.end - currNode.start)))
            else:
                tmpList.append((nextNode[0], nextNode[1]))
                currNode = nextNode[0]
        self.paths.update({node.id: tmpList})

    def collectTime(self, node):
        path = self.paths.get(node.id)
        time = node.migratePoint - node.start
        for p in path:
            time += p[1]/p[0].currTask
            # time += p[1]
        return time

    def clear(self, parser):
        for cpu in parser.server_vm.values():
            for n in cpu:
                n.currTask = 0
