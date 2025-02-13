
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx

# Importar funciones y módulos de tu proyecto
from grafo import GrafoDeHabitabilidad
from visualizacion import visualizar_grafo_con_matching
from Listas import (
    generar_datos_salones,
    generar_datos_pasillos,
    guardar_csv,
)
from conexiones import emparejar_por_estado
from habitabilidad import (
    aplicar_instalacion_paneles,
    guardar_mejora_en_csv
)
from edificio import plot_edificio_3d, leer_salones as leer_salones_edificio, leer_pasillos as leer_pasillos_edificio

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto de Habitabilidad - Interfaz 3D")
        self.geometry("1200x800")
        
        # Panel para la visualización principal (edificio 3D)
        self.fig = plt.Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Panel de controles a la derecha
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        btn_edificio = ttk.Button(control_frame, text="Ver Edificio Completo", command=self.ver_edificio)
        btn_edificio.pack(pady=10)
        
        lbl_piso = ttk.Label(control_frame, text="Ver por Piso:")
        lbl_piso.pack(pady=5)
        self.entry_piso = ttk.Entry(control_frame)
        self.entry_piso.pack(pady=5)
        btn_piso = ttk.Button(control_frame, text="Ver Piso", command=self.ver_piso)
        btn_piso.pack(pady=10)
        
        btn_grafo = ttk.Button(control_frame, text="Ver Grafo Matching", command=self.ver_grafo_matching)
        btn_grafo.pack(pady=10)
        
        btn_consultar = ttk.Button(control_frame, text="Consultar Salón", command=self.consultar_salon_gui)
        btn_consultar.pack(pady=10)
        
        btn_consultar_pasillo = ttk.Button(control_frame, text="Consultar Pasillo por Piso", command=self.consultar_pasillo_por_piso)
        btn_consultar_pasillo.pack(pady=10)
        
        btn_actividad = ttk.Button(control_frame, text="Asignar Actividad", command=self.asignar_actividad)
        btn_actividad.pack(pady=10)
        
        btn_salir = ttk.Button(control_frame, text="Salir", command=self.quit)
        btn_salir.pack(pady=10)
        
        # Al iniciar, se crean (si no existen) y se leen los CSV y se genera el grafo.
        self.cargar_datos_y_grafo()
        self.ver_edificio()  # Mostrar por defecto el edificio completo.
    
    def cargar_datos_y_grafo(self):
        # Si no existen los CSV, generarlos.
        if not os.path.exists("salones.csv"):
            datos_salones = generar_datos_salones()
            campos_salones = ["Nombre", "Estado", "Potencia_dB", "Habitabilidad"]
            guardar_csv("salones.csv", datos_salones, campos_salones)
        if not os.path.exists("pasillos.csv"):
            datos_salones = generar_datos_salones()  # Para generar pasillos se usa la info de salones.
            datos_pasillos = generar_datos_pasillos(datos_salones)
            campos_pasillos = ["Piso", "Nombre", "Promedio_Ruido", "Habitabilidad"]
            guardar_csv("pasillos.csv", datos_pasillos, campos_pasillos)
        
        # Leer datos utilizando funciones de edificio.py
        self.salones = leer_salones_edificio("salones.csv")
        self.pasillos = leer_pasillos_edificio("pasillos.csv")
        
        # Crear diccionario de resultados: zona -> Habitabilidad.
        self.resultados = {nombre: info["Habitabilidad"] for nombre, info in self.salones.items()}
        for pasillo in self.pasillos.values():
            self.resultados[pasillo["Nombre"]] = pasillo["Habitabilidad"]
        
        # Generar el grafo.
        self.grafo_obj = GrafoDeHabitabilidad()
        self.grafo_obj.generar_grafo(self.resultados)
        # Asignar un valor de "ruido" a cada nodo según su Habitabilidad.
        for nodo, datos in self.grafo_obj.grafo.nodes(data=True):
            hab = datos.get("habitabilidad")
            if hab == "Zona Tranquila":
                self.grafo_obj.grafo.nodes[nodo]["ruido"] = 45
            elif hab == "Zona Aceptable":
                self.grafo_obj.grafo.nodes[nodo]["ruido"] = 65
            elif hab == "Zona Ruidosa":
                self.grafo_obj.grafo.nodes[nodo]["ruido"] = 80
            else:
                self.grafo_obj.grafo.nodes[nodo]["ruido"] = 50
        
        self.matching = emparejar_por_estado(self.grafo_obj.grafo)
    
    def ver_edificio(self):
        self.cargar_datos_y_grafo()  
        self.ax.clear()
        plot_edificio_3d(self.salones, self.pasillos, ax=self.ax)
        self.canvas.draw()
    
    def ver_piso(self):
        piso = self.entry_piso.get().strip()
        try:
            piso = int(piso)
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número de piso válido")
            return
        salones_piso = {k: v for k, v in self.salones.items() if k.split(" ")[1] == str(piso)}
        pasillos_piso = {k: v for k, v in self.pasillos.items() if k.split(" ")[1] == str(piso)}
        if not salones_piso and not pasillos_piso:
            messagebox.showinfo("Info", f"No se encontraron datos para el piso {piso}.")
            return
        self.ax.clear()
        plot_edificio_3d(salones_piso, pasillos_piso, ax=self.ax)
        self.canvas.draw()
    
    def ver_grafo_matching(self):
        top = tk.Toplevel(self)
        top.title("Grafo con Matching")
        fig = plt.Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        G = self.grafo_obj.grafo
        color_map = {"Zona Tranquila": "green", "Zona Aceptable": "yellow", "Zona Ruidosa": "red"}
        node_colors = [color_map.get(G.nodes[n].get("habitabilidad", "gray"), "gray") for n in G.nodes()]
        pos = nx.spring_layout(G)
        ax.clear()
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=100, ax=ax)
        nx.draw_networkx_labels(G, pos, ax=ax)
        nx.draw_networkx_edges(G, pos, edgelist=list(self.matching), edge_color="blue", width=3, ax=ax)
        ax.set_title("Grafo de Habitabilidad con Matching")
        canvas_top = FigureCanvasTkAgg(fig, master=top)
        canvas_top.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas_top.draw()
    
    def consultar_salon_gui(self):
        salon = simpledialog.askstring("Consultar Salón", "Ingrese el nombre del salón:")
        if salon:
            info = self.salones.get(salon)
            if info:
                messagebox.showinfo("Información del Salón", f"{salon}\n{info}")
                if info.get("Habitabilidad") == "Zona Ruidosa":
                    opcion = self.menu_mejoras_salon_gui(salon, info)
                    if opcion == "1":
                        msg = aplicar_instalacion_paneles(salon, self.salones, self.grafo_obj)
                        # Guardar la mejora en el CSV de mejoras.
                        guardar_mejora_en_csv(salon, "Instalar paneles acústicos y materiales absorbentes en paredes y techos")
                        messagebox.showinfo("Mejora Aplicada", msg)
                        self.matching = emparejar_por_estado(self.grafo_obj.grafo)
                        visualizar_grafo_con_matching(self.grafo_obj, self.matching)
                    elif opcion == "2":
                        actividad = simpledialog.askstring("Reubicar Actividad", "Ingrese la actividad a reubicar:")
                        if actividad:
                            from habitabilidad import asignar_actividad_con_reubicacion
                            resultado = asignar_actividad_con_reubicacion(salon, info.get("Habitabilidad"), actividad, self.salones, self.pasillos)
                            messagebox.showinfo("Resultado de Asignación", resultado)
            else:
                messagebox.showinfo("Información", "Salón no encontrado.")
    
    def menu_mejoras_salon_gui(self, salon_name, salon_data):
        top = tk.Toplevel(self)
        top.title(f"Mejoras para {salon_name}")
        lbl = tk.Label(top, text=f"El salón {salon_name} está en Zona Ruidosa.\nSeleccione una opción:")
        lbl.pack(pady=10)
        opcion_var = tk.StringVar(value="1")
        rb1 = tk.Radiobutton(top, text="1. Implementar materiales acústicos en paredes y techos", variable=opcion_var, value="1")
        rb1.pack(anchor="w", padx=20)
        rb2 = tk.Radiobutton(top, text="2. Reubicar la actividad si es necesario", variable=opcion_var, value="2")
        rb2.pack(anchor="w", padx=20)
        btn_ok = ttk.Button(top, text="OK", command=top.destroy)
        btn_ok.pack(pady=10)
        self.wait_window(top)
        return opcion_var.get()
    
    def consultar_pasillo_por_piso(self):
        piso_str = simpledialog.askstring("Consultar Pasillo por Piso", "Ingrese el número de piso:")
        if not piso_str:
            return
        try:
            piso = int(piso_str)
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número de piso válido.")
            return
        pasillo_info = None
        for key, info in self.pasillos.items():
            if key.startswith(f"Piso {piso} - Pasillo"):
                pasillo_info = info
                break
        if pasillo_info:
            messagebox.showinfo("Información del Pasillo", f"Piso {piso} - Pasillo\n{pasillo_info}")
        else:
            messagebox.showinfo("Información", f"No se encontró pasillo para el piso {piso}.")
    
    def asignar_actividad(self):
        zona = simpledialog.askstring("Asignar Actividad", "Ingrese el nombre de la zona (salón o pasillo):")
        if not zona:
            return
        actividad = simpledialog.askstring("Asignar Actividad", "Ingrese la actividad a asignar:")
        if not actividad:
            return
        if zona in self.salones:
            hab = self.salones[zona]["Habitabilidad"]
        elif zona in self.pasillos:
            hab = self.pasillos[zona]["Habitabilidad"]
        else:
            messagebox.showerror("Error", "Zona no encontrada.")
            return
        from habitabilidad import asignar_actividad_con_reubicacion
        resultado = asignar_actividad_con_reubicacion(zona, hab, actividad, self.salones, self.pasillos)
        messagebox.showinfo("Resultado de Asignación", resultado)

if __name__ == "__main__":
    app = App()
    app.mainloop()
