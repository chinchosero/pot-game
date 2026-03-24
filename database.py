import json
import os

class JSONDatabase:
    def __init__(self, file_name="data.json"):
        self.file_path = os.path.join(os.path.dirname(__file__), file_name)

    def _load(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    
    def _save(self, data):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @staticmethod
    def normalize(value: str) -> str:
        """Normalize string for case-insensitive comparison."""
        return value.strip().lower()
    
    def get_all(self):
        """Get all emotions and topics."""
        return self._load()
    
    def get_emotions(self):
        """Get all emotions."""
        return self._load().get("emotions", [])
    
    def get_topics(self):
        """Get all topics."""
        return self._load().get("topics", [])
    
    def add_item(self, kind, value):
        """Add an item. Raises ValueError if invalid or duplicate."""
        if kind not in ("emotions", "topics"):
            raise ValueError(f"Invalid kind: {kind}")

        clean_value = value.strip()
        if not clean_value:
            raise ValueError("Value cannot be empty.")
        
        data = self._load()
        data.setdefault(kind, [])

        # Check for duplicates using normalized comparison
        existing_normalized = {self.normalize(item) for item in data[kind] if isinstance(item, str)}
        if self.normalize(clean_value) in existing_normalized:
            raise ValueError(f"Duplicate {kind[:-1]}: {clean_value} already exists.")
        
        data[kind].append(clean_value)
        self._save(data)
    
    def delete_item(self, kind, value):
        """Delete an item. Raises ValueError if not found."""
        if kind not in ("emotions", "topics"):
            raise ValueError(f"Invalid kind: {kind}")
        
        data = self._load()
        items = data.get(kind, [])
        
        target_normalized = self.normalize(value)
        index_to_delete = next(
            (i for i, item in enumerate(items) if isinstance(item, str) and self.normalize(item) == target_normalized),
            None
        )
        
        if index_to_delete is None:
            raise ValueError(f"{kind[:-1].capitalize()} not found: {value}")
        
        removed = items.pop(index_to_delete)
        data[kind] = items
        self._save(data)
        return removed
    
    def update_item(self, kind, old_value, new_value):
        """Update an item. Raises ValueError if not found or duplicate."""
        if kind not in ("emotions", "topics"):
            raise ValueError(f"Invalid kind: {kind}")

        clean_new = new_value.strip()
        if not clean_new:
            raise ValueError("New value cannot be empty.")
        
        data = self._load()
        items = data.get(kind, [])
        
        old_normalized = self.normalize(old_value)
        index_to_update = next(
            (i for i, item in enumerate(items) if isinstance(item, str) and self.normalize(item) == old_normalized),
            None
        )
        
        if index_to_update is None:
            raise ValueError(f"{kind[:-1].capitalize()} not found: {old_value}")
        
        # Check for duplicates using normalized comparison
        new_normalized = self.normalize(clean_new)
        duplicate_exists = any(
            i != index_to_update and isinstance(item, str) and self.normalize(item) == new_normalized
            for i, item in enumerate(items)
        )

        if duplicate_exists:
            raise ValueError(f"Duplicate {kind[:-1]}: {clean_new} already exists.")
        
        old_item = items[index_to_update]
        items[index_to_update] = clean_new
        data[kind] = items
        self._save(data)

        return {"old": old_item, "new": clean_new}