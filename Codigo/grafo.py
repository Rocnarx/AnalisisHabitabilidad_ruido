import networkx as nx
# bnb estuve entre tres opciones, arbol binario con multi lista, un arbol b+ (olvide tener en cuenta los indeces de los  materiales)
#Para organizar mejor los datos y estructurar esto, intente hacer un grafo jerárquico, donde cada piso es un subconjunto de nodos y cada ubicación (salón, biblioteca, cafetería) es un nodo con su nivel de ruido

class Nodo:
    def __init__(self, ubicacion, habitabilidad):
        self.ubicacion = ubicacion
        self.habitabilidad = habitabilidad

class Arista:
    def __init__(self, nodoA, nodoB, peso):
        self.nodoA = nodoA
        self.nodoB = nodoB
        self.peso = peso
class GrafoDeHabitabilidad:
    def __init__(self):
        self.grafo = nx.Graph()

    def agregar_nodo(self, ubicacion, habitabilidad):
        self.grafo.add_node(ubicacion, habitabilidad=habitabilidad)

    def generar_grafo(self, resultados):

        for ubicacion, estado in resultados.items():
            self.agregar_nodo(ubicacion, estado)
    
        ubicaciones = list(resultados.keys())
        n = len(ubicaciones)
        for i in range(n):
            for j in range(i+1, n):
                # Asignamos un peso alto si tienen el mismo estado y bajo si son distintos
                peso = 10 if resultados[ubicaciones[i]] == resultados[ubicaciones[j]] else 1
                self.grafo.add_edge(ubicaciones[i], ubicaciones[j], weight=peso)