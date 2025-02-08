
import csv
from datetime import datetime

def guardar_mejora_en_csv(nombre_salon, mejora, nombre_archivo="mejoras.csv"):
    
    with open(nombre_archivo, mode="a", newline="", encoding="utf-8") as csvfile:
        campos = ["Salon", "Mejora"]
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        
        
        if csvfile.tell() == 0:
            writer.writeheader()
        
        writer.writerow({
            "Salon": nombre_salon,
            "Mejora": mejora
        })
def menu_mejoras_salon(nombre, salon_data):

    habitabilidad = salon_data.get("Habitabilidad", "")
    
    # Si el salón no es ruidoso, se notifica y no se muestra el menú
    if habitabilidad != "Zona Ruidosa":
        return f"El salón '{nombre}' no presenta niveles críticos de ruido; no se requieren mejoras."
    
    print(f"\nEl salón '{nombre}' se encuentra en Zona Ruidosa.")
    print("Opciones de mejora:")
    print("1. Implementar materiales acústicos en paredes y techos.")
    print("2. Reubicar la actividad si es necesario .")
    print("3. Cancelar.")
    
    opcion = input("Seleccione una opción (1, 2 o 3): ").strip()
    
    if opcion == "1":
        mejora = "Instalar paneles acústicos y materiales absorbentes en paredes y techos"
        guardar_mejora_en_csv(nombre, mejora)
        return f"Recomendación: {mejora}."
    elif opcion == "2":
        mejora = "Reubicar el salón a una zona más habitable"
        guardar_mejora_en_csv(nombre, mejora)
        return f"Recomendación: {mejora}."
    else:
        return "No se realizaron cambios."

def asignar_actividad_csv(zona, habitabilidad, actividad, nombre_archivo="actividades.csv"):
  
   # Almacena la actividad asignada a una zona en un archivo CSV.
    
    with open(nombre_archivo, mode="a", newline="", encoding="utf-8") as csvfile:
        campos = ["Zona", "Habitabilidad", "Actividad"]
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        if csvfile.tell() == 0:
            writer.writeheader()
        
        writer.writerow({
            "Zona": zona,
            "Habitabilidad": habitabilidad,
            "Actividad": actividad
        })
def asignar_actividad_con_reubicacion(zona, habitabilidad, actividad, salones, pasillos, nombre_archivo="actividades.csv"):

    # Definir una lista de actividades restringidas para zonas ruidosas.
    actividades_restringidas = ['clase', 'clases', 'examen', 'estudio', 'conferencia']
    actividad_lower = actividad.lower()
    
    if habitabilidad == "Zona Ruidosa" and any(restringida in actividad_lower for restringida in actividades_restringidas):
        for diccionario in (salones, pasillos):
            for zona_nombre, datos in diccionario.items():
                # Se busca que la zona tenga habitabilidad aceptable y que esté libre.
                if datos.get("Habitabilidad") in ["Zona Tranquila", "Zona Aceptable"] and \
                   datos.get("Estado", "").lower() == "libre":
                    _guardar_actividad(zona_nombre, datos.get("Habitabilidad"), actividad, nombre_archivo)
                    return (f"La actividad '{actividad}' ha sido reubicada a la zona '{zona_nombre}' "
                            f"con habitabilidad '{datos.get('Habitabilidad')}'.")
        _guardar_actividad(zona, habitabilidad, actividad, nombre_archivo)
        return (f"No se encontró una zona más habitable y libre. La actividad '{actividad}' "
                f"se ha asignado en la zona original '{zona}'.")
    else:
        _guardar_actividad(zona, habitabilidad, actividad, nombre_archivo)
        return (f"La actividad '{actividad}' se ha asignado en la zona '{zona}' "
                f"con habitabilidad '{habitabilidad}'.")

def _guardar_actividad(zona, habitabilidad, actividad, nombre_archivo):
    with open(nombre_archivo, mode="a", newline="", encoding="utf-8") as csvfile:
        campos = ["Zona", "Habitabilidad", "Actividad"]
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({
            "Zona": zona,
            "Habitabilidad": habitabilidad,
            "Actividad": actividad
        })

def aplicar_instalacion_paneles(salon, salones, grafo_obj):

    if salon in salones:
        # Obtener el valor actual de Potencia_dB (asegurarse que sea entero)
        try:
            potencia_actual = int(salones[salon].get("Potencia_dB", 0))
        except ValueError:
            return f"No se pudo convertir el valor de Potencia_dB para {salon} a entero."
        
        # restar 10 db debido a la implementación del material 
        nueva_potencia = potencia_actual - 10
        salones[salon]["Potencia_dB"] = nueva_potencia
        
        # Determinar la nueva habitabilidad: si baja de 70 es aceptable si no sigue siendo ruidoso.
        if nueva_potencia < 70:
            nueva_habitabilidad = "Zona Aceptable"
        else:
            nueva_habitabilidad = "Zona Ruidosa"
        salones[salon]["Habitabilidad"] = nueva_habitabilidad
    else:
        return f"El salón '{salon}' no se encontró en el diccionario de salones."
    
    if salon in grafo_obj.grafo.nodes():
        grafo_obj.grafo.nodes[salon]["ruido"] = nueva_potencia
        grafo_obj.grafo.nodes[salon]["habitabilidad"] = nueva_habitabilidad
    
    return (f"La mejora se aplicó a '{salon}'. Nueva Potencia_dB: {nueva_potencia} dB, "
            f"nueva Habitabilidad: {nueva_habitabilidad}.")