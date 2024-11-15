import tkinter as tk
from tkinter import simpledialog, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from heapq import heappush, heappop

# Grafo y posiciones
G = nx.Graph()
pos = {}
node_colors = {}

# Funciones para manipular el grafo
def add_node(node, position):
    G.add_node(node)
    pos[node] = position
    node_colors[node] = 'lightblue' 

def add_edge(node1, node2, weight, color):
    G.add_edge(node1, node2, weight=weight)
    node_colors[node1] = color
    node_colors[node2] = color

# Algoritmos
def dijkstra(source, target):
    try:
        return nx.dijkstra_path(G, source, target)
    except nx.NetworkXNoPath:
        messagebox.showerror("Error", "No existe un camino entre los nodos seleccionados.")
        return []

def yen_k_camino_corto(source, target, k):
    k_paths = []
    candidatos = []
    shortest_path = nx.dijkstra_path(G, source, target)
    k_paths.append(shortest_path)

    for i in range(1, k):
        for j in range(len(k_paths[i - 1]) - 1):
            spur_node = k_paths[i - 1][j]
            root_path = k_paths[i - 1][:j + 1]
            temp_graph = G.copy()
            for path in k_paths:
                if path[:j + 1] == root_path:
                    temp_graph.remove_edge(path[j], path[j + 1])

            try:
                spur_path = nx.dijkstra_path(temp_graph, spur_node, target)
                total_path = root_path[:-1] + spur_path
                total_cost = sum(G[u][v]['weight'] for u, v in zip(total_path, total_path[1:]))
                heappush(candidatos, (total_cost, total_path))
            except nx.NetworkXNoPath:
                continue
        if candidatos:
            _, new_path = heappop(candidatos)
            k_paths.append(new_path)
        else:
            break
    return k_paths

def kruskal():
    return list(nx.minimum_spanning_edges(G, algorithm='kruskal'))

def bellman_ford(source, target):
    try:
        return nx.bellman_ford_path(G, source, target)
    except nx.NetworkXNoPath:
        messagebox.showerror("Error", "No existe un camino entre los nodos seleccionados.")
        return []

# Interfaz gráfica
class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grafos y algoritmos")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.node_count = 0
        self.selected_node = None
        self.node1 = None
        self.node2 = None
        self.create_buttons()
        self.figure, self.ax = plt.subplots()
        self.canvas.mpl_connect = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.mpl_connect.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.draw_graph()

    def create_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(frame, text="Agregar Nodo", command=self.add_node_button).pack(pady=5)
        tk.Button(frame, text="Agregar Arista", command=self.add_arista_button).pack(pady=5)
        tk.Button(frame, text="Kruskal", command=self.run_kruskal).pack(pady=5)
        tk.Button(frame, text="Dijkstra", command=self.run_dijkstra).pack(pady=5)
        tk.Button(frame, text="Yen", command=self.run_yen).pack(pady=5)
        tk.Button(frame, text="Bellman-Ford", command=self.run_bellman_ford).pack(pady=5)
        tk.Button(frame, text="Salir", command=self.root.quit).pack(pady=5)

        self.node_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE)
        self.node_listbox.pack(pady=5)

    def add_node_button(self):
        self.canvas.bind("<Button-1>", self.add_node)

    def add_node(self, event):
        for node, (x, y) in pos.items():
            if (event.x - x) ** 2 + (event.y - y) ** 2 < 20 ** 2:
                messagebox.showerror("Error", "Haz clic lejos de un nodo existente.")
                return
        self.node_count += 1
        add_node(self.node_count, (event.x, event.y))
        self.node_listbox.insert(tk.END, f"Nodo {self.node_count}")
        self.canvas.unbind("<Button-1>")
        self.draw_graph()

    def add_arista_button(self):
        selected_nodes = self.node_listbox.curselection()
        if len(selected_nodes) != 2:
            messagebox.showerror("Error", "Debe seleccionar exactamente dos nodos para agregar una arista.")
            return
        node1 = int(self.node_listbox.get(selected_nodes[0]).split()[1])
        node2 = int(self.node_listbox.get(selected_nodes[1]).split()[1])
        weight = simpledialog.askfloat("Peso", f"Peso de la arista entre {node1} y {node2}:")
        if weight is not None:
            color = simpledialog.askstring("Color", "Ingrese el color de la arista (por ejemplo, 'red', 'blue'):")
            if not color:
                color = 'gray'  
            add_edge(node1, node2, weight, color)
        self.draw_graph()

    def draw_graph(self):
        self.ax.clear()
        node_color_list = [node_colors.get(node, 'lightblue') for node in G.nodes()]
        nx.draw(G, pos, ax=self.ax, with_labels=True, node_color=node_color_list, edge_color='gray', node_size=500, font_size=10)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=self.ax)
        self.canvas.mpl_connect.draw()

    def run_kruskal(self):
        mst = kruskal()
        messagebox.showinfo("Kruskal", f"Árbol de expansión mínima: {list(mst)}")

    def run_dijkstra(self):
        source = simpledialog.askinteger("Nodo Fuente", "Ingrese el nodo fuente:")
        target = simpledialog.askinteger("Nodo Destino", "Ingrese el nodo destino:")
        if source and target:
            path = dijkstra(source, target)
            messagebox.showinfo("Dijkstra", f"Camino más corto: {path}")

    def run_yen(self):
        source = simpledialog.askinteger("Nodo Fuente", "Ingrese el nodo fuente:")
        target = simpledialog.askinteger("Nodo Destino", "Ingrese el nodo destino:")
        k = simpledialog.askinteger("K", "¿Cuántos caminos desea calcular?")
        if source and target and k:
            paths = yen_k_camino_corto(source, target, k)
            messagebox.showinfo("Yen", f"Los {k} caminos más cortos son: {paths}")

    def run_bellman_ford(self):
        source = simpledialog.askinteger("Nodo Fuente", "Ingrese el nodo fuente:")
        target = simpledialog.askinteger("Nodo Destino", "Ingrese el nodo destino:")
        if source and target:
            path = bellman_ford(source, target)
            messagebox.showinfo("Bellman-Ford", f"Camino más corto: {path}")

# Inicia la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()