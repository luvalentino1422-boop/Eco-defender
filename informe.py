import os
from datetime import datetime
from api_general import obtener_respuesta_poe

# Carpeta base donde están los archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "impactos_chispas.txt")
USUARIOS_FILE = os.path.join(BASE_DIR, "usuarios.txt")

# Puntos por tipo de impacto
PUNTOS_TIPO = {
    "Enemigo": 10,
    "Jugador": -5
}

def generar_matriz_informe():
    # Cabecera de la tabla
    matriz = [["ID", "Usuario", "Impactos", "Total Mes"]]

    # Leer usuarios registrados
    usuarios = []
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
            usuarios = [line.strip() for line in f if line.strip()]

    # Diccionario para acumular totales por usuario y mes
    totales = {}
    impactos = {}

    if not os.path.exists(LOG_FILE):
        print("No existe el archivo de impactos todavía.")
        return matriz

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for linea in f:
            try:
                # Extraer fecha y mes
                fecha_str = linea.split("]")[0].strip("[")
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                mes = fecha.strftime("%Y-%m")

                # Extraer usuario
                if "Usuario:" in linea:
                    usuario = linea.split("Usuario:")[1].split()[0].strip()
                else:
                    usuario = "Desconocido"

                # Tipo de impacto
                tipo = linea.split("Tipo:")[-1].strip()
                puntos = PUNTOS_TIPO.get(tipo, 1)

                # Clave única por usuario y mes
                clave = (usuario, mes)

                # Acumular totales
                totales[clave] = totales.get(clave, 0) + puntos

                # Si el usuario alcanza o supera los 100000 puntos, avisar a Poe
                if totales[clave] >= 100000 and totales[clave] - puntos < 100000:
                    mensaje = (
                        f"El jugador {usuario} acaba de alcanzar {totales[clave]} puntos este mes. "
                        "Felicítalo como si fueras un comentarista de videojuegos."
                    )
                    respuesta = obtener_respuesta_poe(mensaje)
                    print(f"🎉 Poe dice sobre {usuario}: {respuesta}")

                # Guardar detalle de impactos
                if clave not in impactos:
                    impactos[clave] = []
                impactos[clave].append(puntos)

            except Exception as e:
                print("Error procesando línea:", linea, e)

    # ---- Construir filas finales con IDs autoincrementales ----
    id_contador = 1
    for (usuario, mes), total in totales.items():
        matriz.append([id_contador, usuario, mes, len(impactos[(usuario, mes)]), total])
        id_contador += 1

    return matriz
