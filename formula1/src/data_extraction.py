import pandas as pd
import mysql.connector

def connect_to_database(host, user, password, database):
    """
    Conecta a la base de datos MySQL.
    """
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def execute_query(connection, query):
    """
    Ejecuta una consulta SQL y devuelve los resultados como una lista.
    """
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [i[0] for i in cursor.description]  # Obtener nombres de columnas
    cursor.close()
    return result, columns

def save_to_csv(df, file_path):
    """
    Guarda un DataFrame en un archivo CSV.
    """
    df.to_csv(file_path, index=False)

def extract_data(output_file):
    """
    Función principal de extracción de datos que se usará en el flujo principal.
    """
    # Configuración de conexión
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Ringochunin1302',
        'database': 'ergast_f1'
    }

    # Conectar a la base de datos
    conn = connect_to_database(**db_config)

    # Definir la consulta
    query = """
    SELECT 
        r.raceId, 
        r.driverId, 
        r.constructorId, 
        ra.year,
        ra.date AS race_date,
        r.positionOrder AS final_position, 
        r.points AS driver_points, 
        r.laps AS completed_laps, 
        r.fastestLap AS fastest_lap,
        r.fastestLapSpeed AS fastest_lap_speed, 
        r.milliseconds AS race_time_ms, 
        q.position AS qualifying_position, 
        ds.points AS driver_standing_points, 
        ds.wins AS driver_wins, 
        cs.points AS constructor_points, 
        cs.wins AS constructor_wins
    FROM 
        results r
    LEFT JOIN 
        qualifying q ON r.raceId = q.raceId AND r.driverId = q.driverId
    LEFT JOIN 
        driverStandings ds ON r.driverId = ds.driverId AND r.raceId = ds.raceId
    LEFT JOIN 
        constructorStandings cs ON r.constructorId = cs.constructorId AND r.raceId = cs.raceId
    JOIN
        races ra ON r.raceId = ra.raceId
    WHERE 
        r.positionOrder IS NOT NULL
        AND ra.year BETWEEN YEAR(CURDATE()) - 20 AND YEAR(CURDATE())
    ORDER BY 
        r.raceId, r.driverId;
    """

    # Ejecutar la consulta
    result, columns = execute_query(conn, query)

    # Convertir los resultados en un DataFrame
    df = pd.DataFrame(result, columns=columns)

    # Guardar el DataFrame en un CSV
    save_to_csv(df, output_file)

    # Cerrar la conexión
    conn.close()
    print(f"Datos guardados en {output_file}")
