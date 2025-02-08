import matplotlib.pyplot as plt
plt.ion()  # Activar modo interactivo (no entiendo esto pero soluciona el problema de hilos "https://stackoverflow.com/questions/78805800/how-can-i-use-plt-ion")

from grafo import GrafoDeHabitabilidad
from visualizacion import visualizar_grafo_con_matching
from Listas import (
    generar_datos_salones,
    generar_datos_pasillos,
    guardar_csv,
    leer_csv,
    consultar_salon,
    consultar_pasillo
)
from conexiones import emparejar_por_estado
from habitabilidad import menu_mejoras_salon, asignar_actividad_con_reubicacion, aplicar_instalacion_paneles

def main():
    csv_salones = "salones.csv"
    csv_pasillos = "pasillos.csv"
    
    # 1. Generar datos simulados para los salones y guardarlos en CSV.
    datos_salones = generar_datos_salones()
    campos_salones = ["Nombre", "Estado", "Potencia_dB", "Habitabilidad"]
    guardar_csv(csv_salones, datos_salones, campos_salones)
    
    # 2. Generar datos de pasillos (con promedios de ruido) y guardarlos en otro CSV.
    datos_pasillos = generar_datos_pasillos(datos_salones)
    campos_pasillos = ["Piso", "Nombre", "Promedio_Ruido", "Habitabilidad"]
    guardar_csv(csv_pasillos, datos_pasillos, campos_pasillos)
    
    salones = leer_csv(csv_salones)
    pasillos = leer_csv(csv_pasillos)

    # 4. Crear un diccionario 'resultados' que asocie cada zona (salón o pasillo) a su Habitabilidad.
    resultados = {nombre: info["Habitabilidad"] for nombre, info in salones.items()}
    for pasillo in pasillos.values():
        resultados[pasillo["Nombre"]] = pasillo["Habitabilidad"]
    
    # 5. Generar el grafo con la info del csv
    grafo_obj = GrafoDeHabitabilidad()
    grafo_obj.generar_grafo(resultados)
    
    # Asignar un valor de "ruido" a cada nodo según su habitabilidad.
    for nodo, datos in grafo_obj.grafo.nodes(data=True):
        if datos.get("habitabilidad") == "Zona Tranquila":
            grafo_obj.grafo.nodes[nodo]["ruido"] = 45
        elif datos.get("habitabilidad") == "Zona Aceptable":
            grafo_obj.grafo.nodes[nodo]["ruido"] = 65
        elif datos.get("habitabilidad") == "Zona Ruidosa":
            grafo_obj.grafo.nodes[nodo]["ruido"] = 80
        else:
            grafo_obj.grafo.nodes[nodo]["ruido"] = 50

    # 6. Calcular el emparejamiento por estado.
    matching = emparejar_por_estado(grafo_obj.grafo)
    print("Emparejamientos por estado encontrados:")
    for par in matching:
        print(par)
    
    # 7. grafo actualizado
    visualizar_grafo_con_matching(grafo_obj, matching)
    
    # 8. Menú interactivo para consultas y asignación de actividades.
    while True:
        print("\nOpciones de consulta:")
        print("1. Consultar un salón (y ver mejoras si es ruidoso)")
        print("2. Consultar un pasillo por piso")
        print("3. Asignar una actividad a una zona")
        print("4. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            salon_a_consultar = input("Ingrese el nombre del salón a consultar: ").strip()
            info_salon = consultar_salon(salon_a_consultar, salones)
            print(info_salon)
            
            # para zonas ruidosas
            if salones.get(salon_a_consultar, {}).get("Habitabilidad") == "Zona Ruidosa":
                resultado_mejora = menu_mejoras_salon(salon_a_consultar, salones[salon_a_consultar])
                print(resultado_mejora)
                # En dado caso que la sol a la zona sea por material
                if "Instalar paneles acústicos" in resultado_mejora:
                    msg = aplicar_instalacion_paneles(salon_a_consultar, salones, grafo_obj)
                    print(msg)
                    matching = emparejar_por_estado(grafo_obj.grafo)
                    print("Nuevo matching tras aplicar la mejora:")
                    for par in matching:
                        print(par)
                    visualizar_grafo_con_matching(grafo_obj, matching)
            else:
                print("El salón no presenta niveles críticos de ruido; no se requieren mejoras especiales.")
        
        elif opcion == "2":
            piso_consulta = input("Ingrese el número de piso para consultar el pasillo: ").strip()
            print(consultar_pasillo(piso_consulta, pasillos))
        
        elif opcion == "3":
            zona = input("Ingrese el nombre de la zona (salón o pasillo): ").strip()
            if zona in salones:
                hab = salones[zona]["Habitabilidad"]
            elif zona in pasillos:
                hab = pasillos[zona]["Habitabilidad"]
            else:
                print("La zona no fue encontrada en salones ni pasillos.")
                continue
            actividad = input("Ingrese la actividad a asignar: ").strip()
            resultado_asignacion = asignar_actividad_con_reubicacion(zona, hab, actividad, salones, pasillos)
            print(resultado_asignacion)
        
        elif opcion == "4":
            print("Saliendo del programa...")
            break
        
        else:
            print("Opción no válida, intente de nuevo.")
        
        # Permitir que la GUI procese eventos (actualiza la figura sin bloquear )
        plt.pause(0.1)

if __name__ == "__main__":
    main()
