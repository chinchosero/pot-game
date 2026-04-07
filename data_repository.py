from typing import Protocol


class DataRepository(Protocol):

    # Categories

    def get_categories(self) -> list[str]:
        """Returns a list of all categories (e.g., emotions, topics)."""
        ...

    def add_category(self, name: str) -> None:
        """Adds a new category. Raise ValueError if the category already exists."""
        ...
    def delete_category(self, name: str) -> None:
        """Deletes an existing category and all its items. Raise ValueError if the category does not exist."""

    # Items

    def get_all(self) -> dict:
        """Returns all categories and their items"""
        ...
    
    def get_items_by_category(self, category: str) -> list[str]:
        """Returns a list of items for the specified category. Raise ValueError if the category does not exist."""
        ...

    def add_item(self, category: str, value: str) -> None:
        """Adds a new item to the specified category. Raise ValueError if the category does not exist or if the item already exists."""
        ...

    def delete_item(self, category: str, value: str) -> str:
        """Deletes an item from the specified category. Raise ValueError if the category or item does not exist."""
        ...

    def update_item(self, category: str, old_value: str, new_value: str) -> dict:
        """Updates an item in the specified category. Raise ValueError if the category or item does not exist."""
        ...