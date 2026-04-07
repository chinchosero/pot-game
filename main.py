from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import random
from database import JSONDatabase
from data_repository import DataRepository

app = FastAPI()
db: DataRepository = JSONDatabase()

# --- Models ---

class CategoryRequest(BaseModel):
    name: str

class AddItemRequest(BaseModel):
    category: str
    value: str

class UpdateItemRequest(BaseModel):
    category: str
    old_value: str
    new_value: str

# --- Root ---

@app.get("/")
def read_root():
    return {"message": "Pot-Game API with dynamic categories!"}

# --- Categories Endpoints ---

@app.get("/categories")
def list_categories():
    """List all available categories."""
    try:
        categories = db.get_categories()
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/categories")
def create_category(request: CategoryRequest):
    """Create a new category."""
    try:
        db.add_category(request.name)
        return {"message": f"Category '{request.name}' created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/categories/{category_name}")
def remove_category(category_name: str):
    """Delete a category and all its items."""
    try:
        db.delete_category(category_name)
        return {"message": f"Category '{category_name}' deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Items Endpoints ---

@app.get("/items")
def list_items(category: Optional[str] = Query(None, description="Filter by specific category. If omitted, returns all items.")):
    """List all items, optionally filtered by category."""
    try:
        if category:
            items = db.get_items_by_category(category)
            return {category: items, "count": len(items)}
        else:
            data = db.get_all()
            counts = {cat: len(items) for cat, items in data.items()}
            return {"items": data, "summary": counts}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/items")
def create_item(request: AddItemRequest):
    """Add a new item to a category."""
    try:
        db.add_item(request.category, request.value)
        return {
            "message": "Item added successfully",
            "category": request.category,
            "value": request.value
        }
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        elif "duplicate" in error_msg:
            raise HTTPException(status_code=409, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/items")
def modify_item(payload: UpdateItemRequest):
    """Update an item in a category."""
    try:
        result = db.update_item(payload.category, payload.old_value, payload.new_value)
        return {
            "message": "Item updated successfully",
            "category": payload.category,
            "old_value": result["old"],
            "new_value": result["new"]
        }
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=str(e))
        elif "duplicate" in error_msg:
            raise HTTPException(status_code=409, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/items")
def remove_item(
    category: str = Query(..., min_length=1, description="Category name"),
    value: str = Query(..., min_length=1, description="Item value to delete")
):
    """Delete an item from a category."""
    try:
        removed = db.delete_item(category, value)
        return {"message": "Item deleted successfully", "category": category, "removed": removed}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Pot (Recipe) Endpoint ---

@app.get("/pot")
def get_pot(categories: list[str] = Query(..., min_length=1, description="Categories to mix in the pot")):
    """Generate a 'pot' (recipe) with one random item from each selected category."""
    result = {}
    for category in categories:
        try:
            items = db.get_items_by_category(category)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Category not found: {category}")
        if not items:
            raise HTTPException(status_code=404, detail=f"No items in category: {category}")
        result[category] = random.choice(items)
    return {"ingredients": result}