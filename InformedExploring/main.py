from queue import PriorityQueue

air_distance_bucharest = {
    "Arad": 366,
    "Bucharest": 0,
    "Craiova": 160,
    "Dobreta": 242,
    "Eforie": 161,
    "Fagaras": 178,
    "Giurgiu": 77,
    "Hirsova": 151,
    "Iasi": 226,
    "Lugoj": 244,
    "Mehadia": 241,
    "Neamt": 234,
    "Oradea": 380,
    "Pitesti": 98,
    "Rimnicu Vilcea": 193,
    "Sibiu": 253,
    "Timisoara": 329,
    "Urziceni": 80,
    "Vaslui": 199,
    "Zerind": 374
}

neighbours = {
    "Arad": {"Zerind": 75, "Sibiu": 140, "Timisoara": 118},
    "Bucharest": {"Pitesti": 101, "Giurgiu": 90, "Urziceni": 85, "Fagaras": 211},
    "Craiova": {"Pitesti": 138, "Rimnicu Vilcea": 146, "Dobreta": 120},
    "Dobreta": {"Mehadia": 75, "Craiova": 120},
    "Eforie": {"Hirsova": 86},
    "Fagaras": {"Sibiu": 99, "Bucharest": 211},
    "Giurgiu": {"Bucharest": 90},
    "Hirsova": {"Urziceni": 98, "Eforie": 86},
    "Iasi": {"Neamt": 87, "Vaslui": 92},
    "Lugoj": {"Timisoara": 111, "Mehadia": 70},
    "Mehadia": {"Dobreta": 75, "Lugoj": 70},
    "Neamt": {"Iasi": 87},
    "Oradea": {"Zerind": 71, "Sibiu": 151},
    "Pitesti": {"Rimnicu Vilcea": 97, "Craiova": 138, "Bucharest": 101},
    "Rimnicu Vilcea": {"Sibiu": 80, "Pitesti": 97, "Craiova": 146},
    "Sibiu": {"Fagaras": 99, "Rimnicu Vilcea": 80, "Arad": 140, "Oradea": 151},
    "Timisoara": {"Arad": 118, "Lugoj": 111},
    "Urziceni": {"Bucharest": 85, "Hirsova": 98, "Vaslui": 142},
    "Vaslui": {"Urziceni": 142, "Iasi": 92},
    "Zerind": {"Oradea": 71, "Arad": 75}
}


def backtrack(start, end, prev):
    path = []
    while end != start:
        path.insert(0, end)
        end = prev[end]
    path.insert(0, start)
    return path


def greedy_search(start, end):
    visited = set()
    q = PriorityQueue()
    q.put((0, start))
    prev = {start: ""}

    while not q.empty():
        current = q.get()[1]

        # end reached
        if current == end:
            break

        visited.add(current)

        for neighbor, _ in neighbours[current].items():
            if neighbor not in visited:
                prio = air_distance_bucharest[neighbor]
                q.put((prio, neighbor))
                prev[neighbor] = current

    return backtrack(start, end, prev)


def dijkstra(start, end):
    visited = set()
    q = PriorityQueue()
    q.put((0, start))
    dist = {start: 0}
    prev = {start: None}

    while not q.empty():
        dist_current, current = q.get()

        # end reached
        if current == end:
            break

        visited.add(current)

        for neighbor, cost in neighbours[current].items():
            dist_neighbor = dist_current + cost
            if neighbor not in dist or dist_neighbor < dist[neighbor]:
                dist[neighbor] = dist_neighbor
                prev[neighbor] = current
                q.put((dist_neighbor, neighbor))

    return backtrack(start, end, prev)


if __name__ == '__main__':
    # Greedy search
    print(" -> ".join(map(str, greedy_search("Mehadia", "Bucharest"))))

    # Dijkstra
    print(" -> ".join(map(str, dijkstra("Mehadia", "Bucharest"))))
