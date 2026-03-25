import pytest
import os
import json
from database import JSONDatabase

@pytest.fixture
def temp_db():
    test_file = "test_data.json"
    with open(test_file, 'w') as f:
        json.dump({"emotions": ["Alegria", "Tristeza"], "topics": ["Fiestas"]}, f)
    
    db = JSONDatabase(test_file)
    yield db  # ← aquí es donde el test se ejecuta
    
    if os.path.exists(test_file):
        os.remove(test_file)


# --- add_item ---
def test_add_emotion_success(temp_db):
    temp_db.add_item("emotions", "Esperanza")
    assert "Esperanza" in temp_db.get_emotions()

def test_add_duplicate_raises_error(temp_db):
    with pytest.raises(ValueError, match="Duplicate"):
        temp_db.add_item("emotions", "alegria")  # ya existe, case-insensitive

def test_add_empty_value_raises_error(temp_db):
    with pytest.raises(ValueError, match="cannot be empty"):
        temp_db.add_item("emotions", "   ")

def test_add_invalid_kind_raises_error(temp_db):
    with pytest.raises(ValueError, match="Invalid kind"):
        temp_db.add_item("feelings", "Calma")


# --- delete_item ---
def test_delete_emotion_success(temp_db):
    removed = temp_db.delete_item("emotions", "Alegria")
    assert removed == "Alegria"
    assert "Alegria" not in temp_db.get_emotions()

def test_delete_case_insensitive(temp_db):
    removed = temp_db.delete_item("emotions", "alegria")  # lowercase
    assert removed == "Alegria"

def test_delete_not_found_raises_error(temp_db):
    with pytest.raises(ValueError, match="not found"):
        temp_db.delete_item("emotions", "NoExiste")


# --- update_item ---
def test_update_emotion_success(temp_db):
    result = temp_db.update_item("emotions", "Alegria", "Felicidad")
    assert result["old"] == "Alegria"
    assert result["new"] == "Felicidad"
    assert "Felicidad" in temp_db.get_emotions()
    assert "Alegria" not in temp_db.get_emotions()

def test_update_not_found_raises_error(temp_db):
    with pytest.raises(ValueError, match="not found"):
        temp_db.update_item("emotions", "NoExiste", "Calma")

def test_update_duplicate_raises_error(temp_db):
    with pytest.raises(ValueError, match="Duplicate"):
        temp_db.update_item("emotions", "Alegria", "tristeza")  # tristeza ya existe


# --- normalize ---
def test_normalize():
    db = JSONDatabase()
    assert db.normalize("  Alegria  ") == "alegria"
    assert db.normalize("FIESTAS") == "fiestas"
    assert db.normalize("  Montaña  ") == "montaña"