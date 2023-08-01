from graphviz import Graph, Digraph


class Node:
    nodes = {}

    def __init__(self, name):
        self.name = name
        self.neighbors = []
        Node.nodes[self.name] = self

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def __str__(self):
        out = f'{self.name} '
        for neighbor in self.neighbors:
            out += f'{neighbor},'
        return out

    def print_all(self):
        for node in Node.nodes:
            print(Node.nodes[node])

    def __eq__(self, other):
        return self.name == other.name

    def get_node(name):
        return Node.nodes[name]


class Edge:
    def __init__(self, node1, node2, distance):
        self.node1 = Node.get_node(node1)
        self.node2 = Node.get_node(node2)
        neighbor = Neighbor(self.node2, distance)
        self.node1.add_neighbor(neighbor)


class Neighbor:
    def __init__(self, node, dist):
        self.node = node
        self.dist = dist

    def __str__(self):
        return f'{self.node.name}:{self.dist}'


# nodeA = Node("a")
# nodeB = Node("b")
# edgeAB = Edge("a", "b", 10)
# nodeA.print_all()


class UndirGraph:
    def __init__(self):
        self.nodes = []

    def make_undirected(self, node):
        for neighbor in node.neighbors:
            temp = Neighbor(node, neighbor.dist)
            neighbor.node.add_neighbor(temp)

    def add_node(self, node):
        self.make_undirected(node)
        self.nodes.append(node)

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    def print(self):
        for node in self.nodes:
            node.print_info()

    def visualize_graph(self):
        dot = Graph(strict=True)
        dot.attr(rankdir='LR')
        # for node in self.nodes:
        # 	dot.node(node.name)
        # edges =[]
        for node in self.nodes:
            for neighbor in node.neighbors:
                edge = dot.edge(node.name, neighbor.node.name, label=f'{neighbor.dist}')
            # if edge in edges:
            # 	edge.remove()
            # edges.append(edge)
        dot.view()
        return dot


class MinHeap:
    def __init__(self):
        self.heap = []

    def __len__(self):
        return len(self.heap)

    def insert(self, node):
        self.heap.append(node)
        self.heapify()
        # self.makeMaxHeap()

    def is_empty(self):
        return len(self) == 0

    def heapify(self):
        i = len(self.heap) - 1
        self.heapify2(i)

    def heapify2(self, i):  # heapifying after insertion
        if i == 0:
            return
        parent = (i - 1) // 2
        if self.heap[parent] > self.heap[i]:
            self.heap[parent], self.heap[i] = self.heap[i], self.heap[parent]
        self.heapify2(parent)

    def remove_top(self):
        if len(self.heap) == 0:
            return None
        top = self.heap[0]
        self.heap[0] = self.heap[-1]
        self.heapify3(0)
        new_heap = self.heap[:-1]
        self.heap = new_heap
        return top

    def heapify3(self, i):  # heapifying after deletion
        largest = i
        l = len(self.heap)
        if i >= l - 1:
            return
        left = i * 2 + 1
        right = 2 * i + 2
        if left < l and self.heap[largest] > self.heap[left]:
            largest = left
        if right < l and self.heap[largest] > self.heap[right]:
            largest = right

        if i != largest:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self.heapify3(largest)

    def print(self):
        for val_obj in self.heap:
            print(val_obj)


class Entry:
    def __init__(self, node):
        self.node = node
        self.total_dist = float("inf")
        self.discovered = False
        self.prev = None
        self.in_heap = False

    def make_discovered(self):
        self.discovered = True

    def get_neigbors(self):
        return self.node.neighbors

    def equal_to(self, node: Node):
        return self.node.name == node.name

    def equal(self, other):
        return self.node.name == other.node.name

    def __lt__(self, other):
        return self.total_dist < other.total_dist

    def __eq__(self, other):
        return self.total_dist == other.total_dist

    def __gt__(self, other):
        return self.total_dist > other.total_dist

    def __str__(self):
        if self.prev is None:
            return f'{self.node.name}, {self.total_dist} {self.discovered} {self.prev}'
        return f'{self.node.name}, {self.total_dist} {self.discovered} {self.prev.node.name}'


class Dijkstra:
    def __init__(self, graph, source, dest):
        self.graph = graph
        self.node_name_entries_dict = {}
        for node in graph.nodes:
            entry = Entry(node)
            if entry.equal(Entry(Node.get_node(source))):
                entry.make_discovered()
                entry.total_dist = 0
                self.source = entry
            elif entry.equal(Entry(Node.get_node(dest))):
                self.dest = entry
            self.node_name_entries_dict[node.name] = entry
        # self.find_path(self.source, self.dest)

    def find_path(self, source, dest):
        heap = MinHeap()
        heap.insert(source)
        cur_entry = source
        while not heap.is_empty():
            cur_entry = heap.remove_top()
            cur_entry.make_discovered()
            if cur_entry.equal(dest):
                break
            for neighbor in cur_entry.get_neigbors():
                temp_entry = self.get_entry(neighbor.node.name)
                if temp_entry.discovered:
                    continue
                if cur_entry.total_dist + neighbor.dist < temp_entry.total_dist:
                    temp_entry.total_dist = cur_entry.total_dist + neighbor.dist
                    temp_entry.prev = cur_entry
                if not temp_entry.in_heap:
                    temp_entry.in_heap = True
                    heap.insert(temp_entry)

        return self.trace_back(dest)

    def trace_back(self, dest):
        path = []
        cur_entry = dest
        while not cur_entry.equal(self.source):
            path.append(cur_entry)
            if cur_entry.prev is None:
                print("No path")
                return False
            cur_entry = cur_entry.prev
        path.append(self.source)
        path.reverse()
        self.path = path
        return True
        # return path

    def get_entry(self, node_name):
        return self.node_name_entries_dict[node_name]
    def get_cost(self):
        return self.dest.total_dist

    def print(self):
        for entry in self.path:
            print(entry)

    def visualize_graph(self):
        dot = self.graph.visualize_graph()
        dot.node(self.source.node.name, color="GREEN", style="filled")
        dot.node(self.dest.node.name, color="ORANGE", style="filled")
        for entry1, entry2 in zip(self.path, self.path[1:]):
            label = entry2.total_dist - entry1.total_dist
            if entry1 != self.source and entry1 != self.dest:
                dot.node(entry1.node.name, color="BLUE", style="filled")
            dot.edge(entry1.node.name, entry2.node.name, penwidth="3")
        dot.view()

    def visualize_path(self):
        dot = Digraph()
        dot.format = "png"
        output_filename = "path"
        for entry1, entry2 in zip(self.path, self.path[1:]):
            if entry1 == self.source:
                dot.node(entry1.node.name.replace("_", " "), color="GREEN", style="filled")
            elif entry2 == self.dest:
                dot.node(entry2.node.name.replace("_", " "), color="ORANGE", style="filled")
            label = entry2.total_dist - entry1.total_dist
            dot.edge(entry1.node.name.replace("_", " "), entry2.node.name.replace("_", " "), label=str(label))
        dot.render(output_filename)
        return output_filename + ".png"

# nodeA = Node("A")
# nodeB = Node("B")
# nodeC = Node("C")
# nodeD = Node("D")
# nodeE = Node("E")

# edgeAB = Edge("A", "B", 10)
# edgeAC = Edge("A", "C", 20)
# edgeBD = Edge("B", "D", 15)
# edgeBC = Edge("B", "C", 1)
# edgeCD = Edge("C", "D", 4)
# edgeDE = Edge("D", "E", 5)
# edgeCE = Edge("C", "E", 10)

# my_graph = UndirGraph()
# my_graph.add_nodes(Node.nodes.values())

# djk = Dijkstra(my_graph, "E", "B")
# djk.visualize_graph()


# nodeA = Node("A")
# nodeB = Node("B")
# nodeC = Node("C")
# nodeA.add_neighbor(Neighbor(nodeB, 10))
# nodeA.add_neighbor(Neighbor(nodeC, 20))
# nodeD = Node("D")
# nodeE = Node("E")
# nodeF = Node("F")
# nodeG = Node("G")
# neigbor1 = Neighbor(nodeD, 30)
# neigbor2 = Neighbor(nodeE, 10)
# neigbor3 = Neighbor(nodeF, 20)
# neigbor4 = Neighbor(nodeG, 10)
# neigbor5 = Neighbor(nodeG, 20)
# nodeC.add_neighbor(neigbor1)
# nodeC.add_neighbor(neigbor2)
# nodeE.add_neighbor(neigbor4)
# nodeE.add_neighbor(neigbor3)
# nodeD.add_neighbor(neigbor3)
# nodeD.add_neighbor(neigbor5)
# nodeH = Node("H")
# nodeF.add_neighbor(Neighbor(nodeH, 15))
# nodeI = Node("I")
# nodeG.add_neighbor(Neighbor(nodeH, 10))
# nodeG.add_neighbor(Neighbor(nodeI, 30))
# nodeH.add_neighbor(Neighbor(nodeI, 15))
# nodeBB = Node("BB")
# nodeA.add_neighbor(Neighbor(nodeBB, 15))
#
#
#
#
# # adding nodes to graph object
# my_graph = UndirGraph()
# my_graph.add_nodes([nodeA, nodeB, nodeC, nodeD, nodeE, nodeF, nodeG, nodeH, nodeI, nodeBB])
#
# dijkstra = Dijkstra(my_graph, nodeD, nodeC)
# # dijkstra.print()
# dijkstra.visualize_graph()