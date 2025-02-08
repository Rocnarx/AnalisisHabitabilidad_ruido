import networkx as nx

def emparejar_por_estado(grafo):
    # Agrupar nodos por estado
    grupos = {}
    for nodo, data in grafo.nodes(data=True):
        estado = data.get("habitabilidad", "Desconocido")
        grupos.setdefault(estado, []).append(nodo)
    #ordenar los nodos por zonas
    matching = set()
    for estado, nodos in grupos.items():
        nodos = sorted(nodos)
        for i in range(0, len(nodos) - 1, 2):
            matching.add((nodos[i], nodos[i+1]))
    return matching