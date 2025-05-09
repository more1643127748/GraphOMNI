from collections import defaultdict, deque
import os
import json

def build_graph(edges):

    adjacency = defaultdict(list)
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    return adjacency

def build_graph_from_csv(file_path):
    """
    Load a CSV file and create a graph from it.
    
    :param file_path: The path to the CSV file.
    :return: A graph represented as an adjacency list.
    """
    vertices = []
    edges = []

    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                parts = line.split()
                if len(parts) == 1:
                    vertices.append(int(parts[0]))
                elif len(parts) == 2:
                    edges.append((int(parts[0]), int(parts[1])))

    graph = build_graph(edges)
    return graph

def validate_bfs(graph, start, order):

    n = len(order)
    if n == 0 or order[0] != start:
        return False

    pos = {}
    for i, v in enumerate(order):
        if v in pos:
            return False
        pos[v] = i

    visited = set([start])
    queue = deque([start])
    idx = 0  

    while queue:
        u = queue.popleft()
        try: 
            if u != order[idx]:
                return False
        except IndexError as e:
            return False
 
        idx += 1

        unvisited_neighbors = [w for w in graph[u] if w not in visited]

        unvisited_neighbors.sort(key=lambda x: pos[x] if x in pos else float("inf"))

        for w in unvisited_neighbors:
            visited.add(w)
            queue.append(w)

    return idx == n

def bfs_shortest_distance(graph, start):

    dist = {}
    dist[start] = 0
    queue = deque([start])

    while queue:
        u = queue.popleft()
        for w in graph[u]:
            if w not in dist:  
                dist[w] = dist[u] + 1
                queue.append(w)

    return dist

def validate_shortest_path(graph, s, t, path):


    if not path:
        return False
    if path[0] != s or path[-1] != t:
        return False

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        if v not in graph[u]:
            return False

    dist = bfs_shortest_distance(graph, s)
    if t not in dist:
        return False

    shortest_dist = dist[t] 
    candidate_dist = len(path) - 1  

    return candidate_dist == shortest_dist

def load_json(file_path, property_name):
    """
    Load a JSON file and extract BFS traversal orders.
    
    :param file_path: The path to the JSON file.
    :return: A list of BFS traversal orders.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    property_value = data.get(property_name, [])
    return property_value

def visit_and_validate_bfs(directory):
    """
    Traverse the given directory and visit all CSV files under every child folder.
    
    :param directory: The root directory to start the traversal.
    """
    for root, dirs, files in os.walk(directory):        
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)                
                graph = build_graph_from_csv(file_path)
                bfs_order = load_json(file_path.replace(".csv", ".json"), "bfs_traversal_order")
                for order in bfs_order:
                    source = order.get("start", None)                    
                    seq = order.get("order", None)                    
                    if isinstance(seq, str):
                        seq = seq.strip("()").split(",")
                        seq = [int(x) for x in seq]
                        
                    result = validate_bfs(graph, source, seq)
                    if not result:
                        print(f"Validation failed for {file_path}")
                        print(f"Start: {source}")
                        print(f"Order: {seq}")
                        print("----")                    

def visit_and_validate_shortest_path(directory):
    """
    Traverse the given directory and visit all CSV files under every child folder.
    
    :param directory: The root directory to start the traversal.
    """
    for root, dirs, files in os.walk(directory):        
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)                
                graph = build_graph_from_csv(file_path)
                shortest_paths = load_json(file_path.replace(".csv", ".json"), "shortest_path")                
                for sp in shortest_paths:                    
                    for k, v in sp.items():
                        s, t = k.strip("()").split(",")
                        s = int(s)
                        t = int(t)
                        path = v
                        result = validate_shortest_path(graph, s, t, path)
                        if not result:
                            print(f"Validation failed for {file_path}")
                            print(f"Start: {s}")
                            print(f"End: {t}")
                            print(f"Path: {path}")
                            print("----")                                    


def check_is_connected(graph, s, t):

    from collections import deque

    if s == t:
        return True

    visited = set()
    queue = deque([s])
    visited.add(s)

    while queue:
        current = queue.popleft()
        for neighbor in graph.get(current, []):
            if neighbor == t:
                return True
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False

if __name__ == "__main__":
    print("Hello, BFS order verification!")
    visit_and_validate_bfs("/home/c223zhan/gai/graph-llm-dataset/bfsorder")
    
    print("Hello, Shortest path verification!")
    visit_and_validate_shortest_path("/home/c223zhan/gai/graph-llm-dataset/shortest_path")