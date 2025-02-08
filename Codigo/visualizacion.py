import matplotlib.pyplot as plt
import networkx as nx

def visualizar_grafo_con_matching(grafo_obj, matching):
    G = grafo_obj.grafo
    color_map = {"Zona Tranquila": "green", "Zona Aceptable": "yellow", "Zona Ruidosa": "red"}
    node_colors = [color_map.get(G.nodes[n].get("habitabilidad", "Desconocido"), "gray") for n in G.nodes()]

    pos = nx.spring_layout(G)
    plt.figure("Grafo de Habitabilidad")
    plt.clf()  
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edgelist=list(matching), edge_color="blue", width=3)
    plt.title("Grafo de Habitabilidad con Emparejamientos por Estado")
    plt.axis("off")
    plt.draw()
