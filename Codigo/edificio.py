# edificio.py
from mpl_toolkits.mplot3d import Axes3D  # Necesario para 3D
import matplotlib.pyplot as plt
import numpy as np
import csv

def leer_salones(nombre_archivo="salones.csv"):
    salones = {}
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            salones[row["Nombre"]] = row
    return salones

def leer_pasillos(nombre_archivo="pasillos.csv"):
    pasillos = {}
    with open(nombre_archivo, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pasillos[row["Nombre"]] = row
    return pasillos

def plot_edificio_3d(salones, pasillos, ax=None):
    # Mapeo de colores según la habitabilidad.
    color_map = {
        "Zona Tranquila": "green",
        "Zona Aceptable": "yellow",
        "Zona Ruidosa": "red"
    }
    
    # Si no se pasó un eje, crear uno.
    if ax is None:
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
    
    # Aumentar el factor de separación para los salones.
    spacing_factor = 10
    
    # Agrupar salones por piso (se asume que el nombre tiene formato "Piso X - Salón YYY").
    salones_por_piso = {}
    for nombre, datos in salones.items():
        try:
            partes = nombre.split(" ")
            piso = int(partes[1])
        except Exception:
            continue
        salones_por_piso.setdefault(piso, []).append((nombre, datos))
    
    # Dibujar salones: distribuirlos en el eje X.
    for piso in sorted(salones_por_piso.keys()):
        salon_list = salones_por_piso[piso]
        n = len(salon_list)
        xs = np.linspace(-n/2, n/2, n) * spacing_factor
        for i, (nombre, datos) in enumerate(salon_list):
            x = xs[i]
            y = 0    # Los salones se ubican en y=0
            z = piso
            color = color_map.get(datos.get("Habitabilidad", ""), "gray")
            ax.scatter(x, y, z, c=color, s=100)
            ax.text(x, y, z, nombre, size=8, color="k")
    
    # Dibujar pasillos: se asume un pasillo por piso, en posición fija (por ejemplo, x=0, y=3).
    for nombre, datos in pasillos.items():
        try:
            partes = nombre.split(" ")
            piso = int(partes[1])
        except Exception:
            continue
        x = 0
        y = 3
        z = piso
        color = color_map.get(datos.get("Habitabilidad", ""), "gray")
        ax.scatter(x, y, z, c=color, s=150, marker="^")
        ax.text(x, y, z, nombre, size=8, color="k")
    
    ax.set_xlabel("Eje X (Salones distribuidos)")
    ax.set_ylabel("Eje Y (Ubicación de pasillos)")
    ax.set_zlabel("Piso")
    ax.set_title("Plano 3D del Edificio Universitario")
    ax.set_xlim(-spacing_factor*5, spacing_factor*5)
    ax.set_ylim(-1, 10)
    ax.set_zlim(0, 10)
    
    # Nota: No se llama a plt.show() aquí, ya que la GUI de Tkinter controlará la figura.
    return ax
