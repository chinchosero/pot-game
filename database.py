import json
import os
from data_repository import DataRepository


class JSONDatabase(DataRepository):

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
    
    # Categories
    
    def get_categories(self) -> list[str]:
        """Get a list of all categories."""
        return list(self._load().keys())
    
    def add_category(self, name: str):
        clean = name.strip()
        if not clean:
            raise ValueError("Category name cannot be empty.")
        data = self._load()
        if clean in data:
            raise ValueError(f"Category already exists: {clean}")
        data[clean] = []
        self._save(data)

    def delete_category(self, name: str):
        data = self._load()
        key = next((k for k in data if self.normalize(k) == self.normalize(name)), None)
        if key is None:
            raise ValueError(f"Category not found: {name}")
        del data[key]
        self._save(data)

    # Items

    def get_all(self) -> dict:
        return self._load()
    
    def get_items_by_category(self, category: str) -> list[str]:
        data = self._load()
        key = next((k for k in data if self.normalize(k) == self.normalize(category)), None)
        if key is None:
            raise ValueError(f"Category not found: {category}")
        return data[key]
    
    def add_item(self, category: str, value: str) -> None:
        clean_value = value.strip()
        if not clean_value:
            raise ValueError("Value cannot be empty.")
        data = self._load()
        key = next((k for k in data if self.normalize(k) == self.normalize(category)), None)
        if key is None:
            raise ValueError(f"Category not found: {category}")
        existing = {self.normalize(i) for i in data[key] if isinstance(i, str)}
        if self.normalize(clean_value) in existing:
            raise ValueError(f"Duplicate item in {category}: {clean_value} already exists.")
        data[key].append(clean_value)
        self._save(data)
    
    def delete_item(self, category: str, value: str) -> str:
        data = self._load()
        key = next((k for k in data if self.normalize(k) == self.normalize(category)), None)
        if key is None:
            raise ValueError(f"Category not found: {category}")
        items = data[key]
        idx = next(
            (i for i, item in enumerate(items) if self.normalize(item) == self.normalize(value)),
            None
        )
        if idx is None:
            raise ValueError(f"Item not found in {category}: {value}")
        removed = items.pop(idx)
        data[key] = items
        self._save(data)
        return removed

    
    def update_item(self, category: str, old_value: str, new_value: str) -> dict:
        clean_new = new_value.strip()
        if not clean_new:
            raise ValueError("New value cannot be empty.")
        data = self._load()
        key = next((k for k in data if self.normalize(k) == self.normalize(category)), None)
        if key is None:
            raise ValueError(f"Category not found: {category}")
        items = data[key]
        idx = next(
            (i for i, item in enumerate(items) if self.normalize(item) == self.normalize(old_value)),
            None
        )
        if idx is None:
            raise ValueError(f"Item not found in {category}: {old_value}")
        duplicate = any(
            i != idx and self.normalize(item) == self.normalize(clean_new)
            for i, item in enumerate(items)
        )
        if duplicate:
            raise ValueError(f"Duplicate item in {category}: {clean_new} already exists.")
        old_item = items[idx]
        items[idx] = clean_new
        data[key] = items
        self._save(data)
        return {"old": old_item, "new": clean_new}