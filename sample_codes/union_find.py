from typing import List


def validPath(n: int, edges: List[List[int]], start: int, end: int) -> bool:
    '''
    We cannot simply check if
    root of start == root of end
    because when we connect 2 different
    graphs (for example, each has 4 nodes),
    then we change the root of the connecting
    node, but others are left untouched.

    '''
    graph = UF(n)

    for e1, e2 in edges:
        graph.union(e1, e2)

    root1 = graph.find(start)
    root2 = graph.find(end)

    return root1 == root2


class UF:
    def __init__(self, size):
        self.root = [i for i in range(size)]
        self.rank = [1 for _ in range(size)]

    def find(self, vert):
        if self.root[vert] == vert:
            return vert
        self.root[vert] = self.find(self.root[vert])
        return self.root[vert]

    def union(self, v1, v2):
        r1 = self.find(v1)
        r2 = self.find(v2)
        if r1 != r2:
            if self.rank[r1] > self.rank[r2]:
                self.root[r2] = r1
            elif self.rank[r1] < self.rank[r2]:
                self.root[r1] = r2
            else:
                self.root[r2] = r1
                self.rank[r1] += 1