# main.py

from src.data_extraction import extract_data
from src.model_training import train_model
from src.data_visualization import generate_visualization

def main():
    # Definir rutas de archivos
    raw_data_path = "D:\\visualization\\formula1\\data\\processed\\df_train_v3.csv"
    prediction_data_path = "D:\\visualization\\formula1\\data\\processed\\df_prediction.csv"
    template_path = "D:\\visualization\\formula1\\visualizacion\\templates"
    output_path = "D:\\visualization\\docs\\f1_probabilidades_v3.html"
    
    # 1. Extracción de datos
    print("Extrayendo datos...")
    extract_data(raw_data_path)
    
    # 2. Entrenamiento y predicción del modelo
    print("Entrenando modelo...")
    train_model(raw_data_path, prediction_data_path)
    
    # 3. Generación de visualización
    print("Generando visualización...")
    generate_visualization(prediction_data_path, template_path, output_path)
    
    print("Pipeline completada con éxito.")

if __name__ == "__main__":
    main()
