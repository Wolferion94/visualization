import requests
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

def generate_visualization(prediction_data_path, template_path, output_path):
    # Obtener datos de la API y crear DataFrame para la tabla F1 actual
    response = requests.get('https://ergast.com/api/f1/current/driverStandings.json')
    data_json = response.json()

    # Extraer información relevante
    standings = data_json['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    drivers_data = []
    for driver in standings:
        drivers_data.append({
            "position": driver['position'],
            "name": f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}",
            "points": int(driver['points']),
            "wins": int(driver['wins']),
            "constructor": driver['Constructors'][0]['name']
        })

    # Crear DataFrame de la tabla F1 actual
    df_f1 = pd.DataFrame(drivers_data)

    # Obtener el top 5
    f1_top5 = df_f1.head(5).to_dict(orient='records')

    # Calcular los valores máximos para puntos y victorias
    max_points = df_f1['points'].max()
    max_wins = df_f1['wins'].max()

    # Diccionario de colores para los constructores
    constructor_colors = {
        "Red Bull": "#1E90FF",
        "Ferrari": "#FF6347",
        "McLaren": "#FF8C00",
        "Mercedes": "#32CD32",
        "Aston Martin": "#228B22",
        "Alpine F1 Team": "#4682B4",
        "Williams": "#1E90FF",
        "Haas F1 Team": "#696969",
        "RB F1 Team": "#FFD700",
        "Sauber": "#C0C0C0"
    }

    # Cargar los datos de predicción
    df_prediction = pd.read_csv(prediction_data_path)
    df_prediction = df_prediction.head(10)
    df_prediction = df_prediction.rename(columns={'name': 'driverId', 'probabilidad_ganar': 'probability'})
    data_tabla = df_prediction.to_dict(orient='records')

    # Asumimos que df_concatenado también está en el archivo CSV
    df_concatenado = pd.concat([df_prediction.iloc[0::2].sort_index(ascending=False), df_prediction.iloc[1::2].sort_index(ascending=False)], ignore_index=True)
    data_pista = df_concatenado.to_dict(orient='records')

    # Configuración de Jinja2 para renderizar el HTML
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('template_f1_v3.html')

    # Renderizar la plantilla con los datos calculados
    output = template.render(
        data_tabla=data_tabla,
        data_pista=data_pista,
        f1_top5=f1_top5,
        max_points=max_points,
        max_wins=max_wins,
        constructor_colors=constructor_colors
    )

    # Guardar el HTML resultante
    with open(output_path, 'w') as f:
        f.write(output)
