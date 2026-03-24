from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Literal
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

def normalize(value: str) -> str:
    return value.strip().lower()

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

@app.get("/items")
def list_all_items():
    data = load_data()
    emotions = data.get("emotions", [])
    topics = data.get("topics", [])
    return {
        "emotions": emotions,
        "topics": topics,
        "counts": {
            "emotions": len(emotions),
            "topics": len(topics)
        }
    }

@app.post("/add-pot")
def add_pot(new_item: PotItem):
    if not new_item.emotions and not new_item.topics:
        raise HTTPException(status_code=400, detail="User must provide at least one field: emotions or topics.")
    
    data = load_data()
    data.setdefault("emotions", [])
    data.setdefault("topics", [])

    existing_emotions = {normalize(e) for e in data["emotions"] if isinstance(e, str)}
    existing_topics = {normalize(t) for t in data["topics"] if isinstance(t, str)}

    added = {"emotions": None, "topics": None}

    if new_item.emotions:
        clean_emotion = new_item.emotions.strip()
        if normalize(clean_emotion) in existing_emotions:
            raise HTTPException(status_code=409, detail=f'Duplicate emotion: "{clean_emotion}" already exists.')
        data["emotions"].append(clean_emotion)
        added["emotions"] = clean_emotion

    if new_item.topics:
        clean_topic = new_item.topics.strip()
        if normalize(clean_topic) in existing_topics:
            raise HTTPException(status_code=409, detail=f'Duplicate topic: "{clean_topic}" already exists.')
        data["topics"].append(clean_topic)
        added["topics"] = clean_topic

    save_data(data)
    return {"message": "New item added successfully!", "added": added}

@app.delete("/items")
def delete_item(
    kind: Literal["emotions", "topics"] = Query(..., description="Select a category to delete from: 'emotions' or 'topics'"),
    value: str = Query(..., min_length=1, description="Write the exact value to delete from the selected category.")
):
    data = load_data()
    items = data.get(kind, [])
    target = normalize(value)
    index_to_delete = next(
         (i for i, item in enumerate(items) if isinstance(item, str) and normalize(item) == target),
        None
    )

    if index_to_delete is None:
        raise HTTPException(status_code=404, detail=f'Item not found in "{kind}": "{value}"')

    removed = items.pop(index_to_delete)
    data[kind] = items
    save_data(data)

    return {"message": "Item deleted successfully", "kind": kind, "removed": removed}
    