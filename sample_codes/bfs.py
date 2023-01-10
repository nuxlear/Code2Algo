def validPath(self, n: int, edges: List[List[int]], start: int, end: int) -> bool:
    graph = defaultdict(list)
    visited = [False] * n

    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    queue = deque([start])

    while queue:
        for _ in range(len(queue)):
            u = queue.popleft()
            if u == end:
                return True
            visited[u] = True
            queue.extend([v for v in graph[u] if not visited[v]])

    return False