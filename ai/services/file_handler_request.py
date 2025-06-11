import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def select_json_file():
    Tk().withdraw()
    file_path = askopenfilename(
        filetypes=[("JSON Files", "*.json")],
        title="Выберите JSON-файл запроса"
    )
    return file_path

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)