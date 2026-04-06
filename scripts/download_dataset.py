import requests
import zipfile
import os
from pathlib import Path

DATASET_URL = "https://github.com/Igorbraziel/desafio-tecnico-ceia-ufg/releases/download/dataset/downloads.zip"
ZIP_PATH = "downloads.zip"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def download_zip():
    print("Downloading zip dataset...")
    
    try:
        response = requests.get(DATASET_URL, stream=True)
        response.raise_for_status()
        
        with open(ZIP_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print("Download completo!")
    except Exception as e:
        print(f"Erro no download do arquivo zip: {e}")

def extract_zip():
    print("Extraindo arquivo zip...")
    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(PROJECT_ROOT)

        print("Extração completa")
    except Exception as e:
        print(f"Erro ao extrair zip dataset: {e}")

def main():
    download_zip()
    extract_zip()
    
    os.remove(ZIP_PATH)
    
if __name__ == "__main__":
    main()
        
