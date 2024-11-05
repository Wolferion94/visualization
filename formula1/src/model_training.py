import pandas as pd
import numpy as np
from prophet import Prophet
import mysql.connector

def train_model(input_path, output_path):
    # Cargar los datos
    df = pd.read_csv(input_path)

    # Preprocesamiento de datos
    df['ds'] = pd.to_datetime(df['race_date']).dt.to_period('M').dt.to_timestamp()
    df['ds'] = pd.to_datetime(df['ds'])
    df['prob_ganar'] = np.where(df['final_position'] == 1, 1, 0)

    # Imputar valores faltantes con la mediana por columna
    df = df.fillna(df.median(numeric_only=True))

    # Agrupar por piloto y fecha
    df = df.groupby(['driverId', 'ds']).agg({
        'prob_ganar': 'mean',
        'fastest_lap': 'mean',
        'driver_points': 'mean',
        'completed_laps': 'mean',
        'fastest_lap_speed': 'mean',
        'qualifying_position': 'mean',
        'driver_standing_points': 'mean',
        'constructor_points': 'mean',
        'constructor_wins': 'mean'
    }).reset_index()

    # Diccionario para almacenar modelos y predicciones por piloto
    modelos = {}
    resultados_predicciones = []

    # Iterar sobre cada piloto
    for piloto in df['driverId'].unique():
        df_piloto = df[df['driverId'] == piloto][['ds', 'prob_ganar', 
                                                   'fastest_lap', 'driver_points', 'completed_laps',
                                                   'fastest_lap_speed', 'qualifying_position',
                                                   'driver_standing_points', 'constructor_points', 'constructor_wins']]
        df_piloto = df_piloto.rename(columns={'prob_ganar': 'y'})

        if df_piloto['y'].notnull().sum() < 2:
            continue
        
        modelo = Prophet()
        for regressor in ['fastest_lap', 'driver_points', 'completed_laps', 'fastest_lap_speed',
                          'qualifying_position', 'driver_standing_points', 'constructor_points', 'constructor_wins']:
            modelo.add_regressor(regressor)
        
        modelo.fit(df_piloto)
        modelos[piloto] = modelo
        
        future = modelo.make_future_dataframe(periods=12, freq='M')
        future = future[future['ds'] <= '2024-12-31']
        
        future = future.merge(df_piloto[['ds', 'fastest_lap', 'driver_points', 'completed_laps',
                                         'fastest_lap_speed', 'qualifying_position',
                                         'driver_standing_points', 'constructor_points', 'constructor_wins']],
                              on='ds', how='left')
        
        future = future.fillna(df_piloto.median(numeric_only=True))
        
        if future.isnull().values.any():
            continue
        
        forecast = modelo.predict(future)
        
        forecast_diciembre_2024 = forecast[(forecast['ds'].dt.year == 2024) & (forecast['ds'].dt.month == 12)]
        
        if forecast_diciembre_2024.empty:
            continue
        
        forecast_diciembre_2024['driverId'] = piloto
        resultados_predicciones.append(forecast_diciembre_2024[['ds', 'yhat', 'driverId']])

    predicciones_totales = pd.concat(resultados_predicciones, ignore_index=True)
    predicciones_totales = predicciones_totales.sort_values(by='yhat', ascending=False).reset_index(drop=True)
    
    predicciones_totales_min_max = predicciones_totales.copy(deep=True)
    predicciones_totales_min_max['yhat'] = predicciones_totales_min_max['yhat'].abs()
    yhat_min = predicciones_totales_min_max['yhat'].min()
    yhat_max = predicciones_totales_min_max['yhat'].max()
    predicciones_totales_min_max['probabilidad_ganar'] = ((predicciones_totales_min_max['yhat'] - yhat_min) / (yhat_max - yhat_min)).pow(0.5).round(3)

    # Obtener nombres y constructores para cada piloto desde la base de datos
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Ringochunin1302',
        database='ergast_f1'
    )
    cursor = conn.cursor()
    
    query = """
    SELECT 
        d.driverId,
        d.forename AS driver_first_name,
        d.surname AS driver_last_name,
        c.constructorId,
        c.name AS constructor_name
    FROM 
        drivers d
    JOIN 
        results r ON d.driverId = r.driverId
    JOIN 
        constructors c ON r.constructorId = c.constructorId
    JOIN 
        races ra ON r.raceId = ra.raceId
    WHERE 
        ra.year = (SELECT MAX(year) FROM races)
    GROUP BY 
        d.driverId, d.forename, d.surname, c.constructorId, c.name
    ORDER BY 
        d.driverId;
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [i[0] for i in cursor.description]
    df_names = pd.DataFrame(result, columns=columns)
    cursor.close()
    conn.close()

    df_names['name'] = df_names.driver_first_name + ' ' + df_names.driver_last_name + ' - ' + df_names.constructor_name
    df_prediction = pd.merge(predicciones_totales_min_max, df_names[['driverId', 'name']], how='left', on='driverId')[['name', 'probabilidad_ganar']]
    
    df_prediction = df_prediction.sort_values(by='probabilidad_ganar', ascending=False).reset_index(drop=True)
    df_prediction['posicion'] = range(1, len(df_prediction) + 1)

    # Guardar las predicciones en el archivo CSV
    df_prediction.to_csv(output_path, index=False)
