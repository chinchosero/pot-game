from fastapi import FastAPI
import random
import json
import os

app = FastAPI()

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

@app.get("/")
def read_root():
    return {"message": "Pot-Game API is reading from JSON!"}

@app.get("/pot")
def get_pot():
    data = load_data()

    pot = {
        "emotions": random.choice(data.get("emotions", [])),
        "topics": random.choice(data.get("topics", []))
    }

    return pot