from typing import Protocol


class DataRepository(Protocol):
    def get_all(self) -> dict:
        ...

    def get_emotions(self) -> list[str]:
        ...

    def get_topics(self) -> list[str]:
        ...

    def add_item(self, kind: str, value: str) -> None:
        ...

    def delete_item(self, kind: str, value: str) -> str:
        ...

    def update_item(self, kind: str, old_value: str, new_value: str) -> dict:
        ...