import csv
import random


def calcular_habitabilidad(potencia):
    if potencia < 50:
        return "Zona Tranquila"
    elif 50 <= potencia <= 70:
        return "Zona Aceptable"
    else:
        return "Zona Ruidosa"

def generar_estado():
    
    #Simula el estado del salón: 60% probabilidad de "En Uso" y 30% de "Libre".
    
    return "En Uso" if random.random() < 0.6 else "Libre"

def generar_datos_salones():
   
    pisos = 8
    salones_por_piso = 7
    datos = []

    for piso in range(1, pisos + 1):
        for salon in range(1, salones_por_piso + 1):
            nombre = f"Piso {piso} - Salón {piso}{salon:02d}"
            estado = generar_estado()
            potencia = random.randint(40, 90)  # Simulación del nivel de ruido en dB
            habitabilidad = calcular_habitabilidad(potencia)
            datos.append({
                "Nombre": nombre,
                "Estado": estado,
                "Potencia_dB": potencia,
                "Habitabilidad": habitabilidad
            })
    return datos

def guardar_csv(nombre_archivo, datos, campos):
   
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        writer.writeheader()
        for fila in datos:
            writer.writerow(fila)
    print(f"CSV '{nombre_archivo}' creado con éxito.")

def leer_csv(nombre_archivo):
    datos_dict = {}
    try:
        with open(nombre_archivo, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for fila in reader:
                # pasar potencia a un valor entero para un calculo aproximado 
                if "Potencia_dB" in fila:
                    fila["Potencia_dB"] = int(fila["Potencia_dB"])
                # calcular promedio en valor flotante
                if "Promedio_Ruido" in fila:
                    fila["Promedio_Ruido"] = float(fila["Promedio_Ruido"])
                clave = fila.get("Nombre", fila.get("Piso"))
                datos_dict[clave] = fila
        return datos_dict
    except FileNotFoundError:
        print(f"El archivo '{nombre_archivo}' no se encontró.")
        return {}

def consultar_salon(nombre, salones):
    """
    Consulta la información de un salón específico a partir del diccionario 'salones'.
    """
    if nombre in salones:
        salon = salones[nombre]
        return (f"Nombre: {salon['Nombre']}\n"
                f"Estado: {salon['Estado']}\n"
                f"Potencia (dB): {salon['Potencia_dB']}\n"
                f"Habitabilidad: {salon['Habitabilidad']}")
    else:
        return "Salón no encontrado."

def generar_datos_pasillos(datos_salones):
    """
    Calcula el promedio de ruido por piso y genera los datos de pasillos.
    """
    pisos = {}
    for salon in datos_salones:
        nombre = salon["Nombre"]
        piso = nombre.split()[1]  # Extraer número de piso como string
        if f"Piso {piso}" not in pisos:
            pisos[f"Piso {piso}"] = []  # Guardar la clave con el formato correcto
        pisos[f"Piso {piso}"].append(salon["Potencia_dB"])

    datos_pasillos = []
    for clave, ruidos in pisos.items():
        promedio = sum(ruidos) / len(ruidos)
        habitabilidad = calcular_habitabilidad(promedio)
        datos_pasillos.append({
            "Piso": clave,  # Usar "Piso X" como clave
            "Nombre": f"{clave} - Pasillo",
            "Promedio_Ruido": round(promedio, 2),
            "Habitabilidad": habitabilidad
        })
    return datos_pasillos

def consultar_pasillo(piso, pasillos):

    clave = f"Piso {piso} - Pasillo"  # Asegurar el formato correcto

    if clave in pasillos:
        pasillo = pasillos[clave]
        return (f"Piso: {pasillo['Piso']}\n"
                f"Nombre: {pasillo['Nombre']}\n"
                f"Promedio de Ruido: {pasillo['Promedio_Ruido']} dB\n"
                f"Habitabilidad: {pasillo['Habitabilidad']}")
    else:
        return f"Piso {piso} no encontrado. unicamente ingresar el # piso a consultar."


