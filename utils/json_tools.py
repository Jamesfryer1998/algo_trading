import json
import pandas as pd
 
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    return data

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_csv(file_path):
    data = pd.read_csv(file_path)
    return data