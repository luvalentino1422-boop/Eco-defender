import mysql.connector
from mysql.connector import Error
from informe import generar_matriz_informe

try:
    # ---- Generar matriz ----
    matriz = generar_matriz_informe()
    print(f"Filas totales generadas: {len(matriz)}")

    for fila in matriz:
        print(fila)

    # Detectar cabecera (aunque tenga menos columnas)
    if matriz and isinstance(matriz[0][0], str) and matriz[0][0].lower() == "id":
        matriz = matriz[1:]

    if not matriz:
        print("No hay datos para procesar.")
        exit()

    # ---- Conectar a MySQL ----
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="guar_usuarios"
    )
    cursor = connection.cursor()

    # ---- Crear tabla si no existe ----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(255) UNIQUE,
            puntos INT DEFAULT 0
        )
    """)
    connection.commit()

    # ---- Insertar o actualizar ----
    sql = """
    INSERT INTO usuarios (usuario, puntos)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE puntos = VALUES(puntos)
    """

    contador = 0
    for fila in matriz:
        try:
            # Según tu estructura:
            # [ID, Usuario, Mes, Impactos, Total Mes]
            usuario = str(fila[1]).strip()
            puntos = int(fila[4])  # 'Total Mes'
            cursor.execute(sql, (usuario, puntos))
            contador += 1
        except (IndexError, ValueError) as e:
            print(f"Error en fila {fila}: {e}")
        except Error as e:
            print(f"Error de MySQL al procesar fila {fila}: {e}")

    connection.commit()
    print(f"{contador} registros insertados o actualizados correctamente.")

except Error as e:
    print(f"Error de conexión o ejecución MySQL: {e}")

finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection:
        connection.close()
