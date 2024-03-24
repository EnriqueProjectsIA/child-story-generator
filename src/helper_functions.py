from datetime import datetime as dt
import datetime
import requests
import Levenshtein as lev
from typing import List
from pathlib import Path
import base64
import pickle

def calculate_number_of_years(brith_date:str) -> int:
    """
    Calculate the number of years between birth_date and current_date
    """
    # Convert the string date to a datetime object
    birth_date = dt.strptime(brith_date, "%Y-%m-%d")
    current_date = datetime.date.today()
    number_of_years = current_date.year - birth_date.year
    # Check if the current date has passed the birth date
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        number_of_years -= 1
    return number_of_years

def calculate_levenshtein_distance(reference_words:List[str], target_word:str):
    """
    Calculate the Levenshtein distance between a list of reference words and a target word
    """
    distances = [lev.distance(target_word, word) for word in reference_words]
    min_distance = min(distances)
    index_min_distance = distances.index(min_distance)
    return reference_words[index_min_distance]

def download_image(image_url, save_path)->None:
    """
    Download an image from a URL and save it to a path
    """
    response = requests.get(image_url)
    response.raise_for_status()  # Asegura que la descarga fue exitosa
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
def convert_base64_to_jpg(b64_string, output_path):
    """
    Convierte un string codificado en base64 a un archivo JPG.

    Parámetros:
    - b64_string (str): La cadena codificada en base64 de la imagen.
    - output_path (str): La ruta del archivo de salida donde se guardará la imagen JPG.
    """
    # Decodifica la cadena base64 a datos binarios
    img_data = base64.b64decode(b64_string)
    
    # Escribe los datos binarios decodificados en un archivo
    with open(output_path, 'wb') as file:
        file.write(img_data)
def delete_image(image_path)->None:
    """
    Delete an image from a path
    """
    if Path(image_path).exists():
        Path(image_path).unlink()
if __name__ == "__main__":
    path = Path(__file__).parent.parent /"images" / "temp_64.jpg"
    path_data = r'C:\proyectos_personales\Cuentos\data\2024-03-24_11-58-45_histories_images.pkl'
    with open(path_data, 'rb') as f:
        data = pickle.load(f)
    image_url = data['history_0']['image_0']
    convert_base64_to_jpg(image_url, path)
    