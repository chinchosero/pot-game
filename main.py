from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
import json
import os

app = FastAPI()

class PotItem(BaseModel):
    emotions: Optional[str] = None
    topics: Optional[str] = None

def get_file_path():
    return os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    with open(get_file_path(), "r", encoding="utf-8") as file:
        return json.load(file)
    
def save_data(data):
    with open(get_file_path(), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.get("/")
def read_root():
    return {"message": "Pot-Game API is reading from JSON!"}

@app.get("/pot")
def get_pot():
    data = load_data()
    emotions = data.get("emotions", [])
    topics = data.get("topics", [])

    if not emotions or not topics:
        raise HTTPException(status_code=404, detail="No emotions or topics available in the data.")

    pot = PotItem(
        emotions=random.choice(data.get("emotions", [])),
        topics=random.choice(data.get("topics", []))
    )
    return pot

@app.post("/add-pot")
def add_pot(new_item: PotItem):
    if not new_item.emotions and not new_item.topics:
        raise HTTPException(status_code=400, detail="User must provide at least one field: emotions or topics.")
    
    data = load_data()
    data.setdefault("emotions", [])
    data.setdefault("topics", [])

    added = {"emotions": None, "topics": None}

    if new_item.emotions:
        data["emotions"].append(new_item.emotions)
        added["emotions"] = new_item.emotions

    if new_item.topics:
        data["topics"].append(new_item.topics)
        added["topics"] = new_item.topics

    save_data(data)
    return {"message": "New item added to the pot!", "added": added}
    