import heapq

def heuristic_cost_estimate(start, goal):
    # 启发式函数，估计从起点到目标的成本
    return abs(goal[0] - start[0]) + abs(goal[1] - start[1])

def astar_search(graph, start, goal):
    open_set = []  # 优先队列，用于存储待处理的节点
    closed_set = set()  # 存储已经处理过的节点
    came_from = {}  # 记录每个节点的前驱节点
    g_score = {start: 0}  # 记录从起点到每个节点的实际成本

    heapq.heappush(open_set, (0 + heuristic_cost_estimate(start, goal), start))

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = reconstruct_path(came_from, current)
            return path

        closed_set.add(current)

        for neighbor in neighbors(graph, current):
            if neighbor in closed_set or graph[neighbor[0]][neighbor[1]] == 1:
                continue

            tentative_g_score = g_score[current] + 1

            if neighbor not in [item[1] for item in open_set] or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic_cost_estimate(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return None  # 没有找到路径

def neighbors(graph, node):
    # 获取节点的相邻节点
    x, y = node
    potential_neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    return [(i, j) for i, j in potential_neighbors if 0 <= i < len(graph) and 0 <= j < len(graph[0])]

def reconstruct_path(came_from, current):
    # 重构路径
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.insert(0, current)
    return path

# 示例使用：
# 假设地图表示为二维矩阵，其中 0 表示可以通过的空地，1 表示墙壁，2 表示问号，3 表示当前位置，4 表示Boss房间
example_map = [
    [0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [2, 0, 1, 0, 1],
    [3, 2, 1, 0, 4]
]

start_position = (4, 0)
boss_position = (4, 4)

path = astar_search(example_map, start_position, boss_position)

if path:
    print("路径:", path)
else:
    print("无法找到路径")
