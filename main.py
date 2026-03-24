from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Literal
import random
from database import JSONDatabase

app = FastAPI()
db = JSONDatabase()

class UpdateItemRequest(BaseModel):
    kind: Literal["emotions", "topics"]
    old_value: str
    new_value: str

class PotItem(BaseModel):
    emotions: Optional[str] = None
    topics: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Pot-Game API is reading from JSON!"}

@app.get("/pot")
def get_pot():
    emotions = db.get_emotions()
    topics = db.get_topics()

    if not emotions or not topics:
        raise HTTPException(status_code=404, detail="No emotions or topics available in the data.")

    return PotItem(
        emotions=random.choice(emotions),
        topics=random.choice(topics)
    )

@app.get("/items")
def list_all_items():
    try:
        data = db.get_all()
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-pot")
def add_pot(new_item: PotItem):
    if not new_item.emotions and not new_item.topics:
        raise HTTPException(status_code=400, detail="User must provide at least one field: emotions or topics.")

    added = {"emotions": None, "topics": None}

    if new_item.emotions:
        try:
            db.add_item("emotions", new_item.emotions)
            added["emotions"] = new_item.emotions.strip()
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))

    if new_item.topics:
        try:
            db.add_item("topics", new_item.topics)
            added["topics"] = new_item.topics.strip()
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))

    return {"message": "New item added successfully!", "added": added}

@app.put("/items")
def update_item(payload: UpdateItemRequest):
    try:
        result = db.update_item(payload.kind, payload.old_value, payload.new_value)
        return {
            "message": "Item updated successfully", 
            "kind": payload.kind, 
            "old_value": result["old"],
            "new_value": result["new"]
         }
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        elif "duplicate" in error_msg.lower():
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

@app.delete("/items")
def delete_item(
    kind: Literal["emotions", "topics"] = Query(..., description="Select a category to delete from: 'emotions' or 'topics'"),
    value: str = Query(..., min_length=1, description="Write the exact value to delete from the selected category.")
):
    try:
        removed = db.delete_item(kind, value)
        return {"message": "Item deleted successfully", "kind": kind, "removed": removed}
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)