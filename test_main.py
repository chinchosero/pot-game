import json
import pytest
from unittest.mock import mock_open, patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

MOCK_DATA = {
    "emotions": ["Alegria", "Tristeza"],
    "topics": ["Fiestas", "Deportes"]
}

def make_mock_data():
    return json.loads(json.dumps(MOCK_DATA))

# --- GET / ---
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Pot-Game API is reading from JSON!"}


# --- GET /pot ---
def test_get_pot_success():
    with patch("main.load_data", return_value=make_mock_data()):
        response = client.get("/pot")
        assert response.status_code == 200
        data = response.json()
        assert data["emotions"] in MOCK_DATA["emotions"]
        assert data["topics"] in MOCK_DATA["topics"]

def test_get_pot_empty_lists():
    with patch("main.load_data", return_value={"emotions": [], "topics": []}):
        response = client.get("/pot")
        assert response.status_code == 404


# --- GET /items ---
def test_list_all_items():
    with patch("main.load_data", return_value=make_mock_data()):
        response = client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert "emotions" in data
        assert "topics" in data
        assert data["counts"]["emotions"] == 2
        assert data["counts"]["topics"] == 2


# --- POST /add-pot ---
def test_add_emotion_success():
    with patch("main.load_data", return_value=make_mock_data()), \
         patch("main.save_data") as mock_save:
        response = client.post("/add-pot", json={"emotions": "Esperanza"})
        assert response.status_code == 200
        assert response.json()["added"]["emotions"] == "Esperanza"
        mock_save.assert_called_once()

def test_add_topic_success():
    with patch("main.load_data", return_value=make_mock_data()), \
         patch("main.save_data") as mock_save:
        response = client.post("/add-pot", json={"topics": "Videojuegos"})
        assert response.status_code == 200
        assert response.json()["added"]["topics"] == "Videojuegos"

def test_add_both_fields_success():
    with patch("main.load_data", return_value=make_mock_data()), \
         patch("main.save_data"):
        response = client.post("/add-pot", json={"emotions": "Calma", "topics": "Montaña"})
        assert response.status_code == 200

def test_add_empty_body_returns_400():
    response = client.post("/add-pot", json={})
    assert response.status_code == 400

def test_add_duplicate_emotion_returns_409():
    with patch("main.load_data", return_value=make_mock_data()):
        response = client.post("/add-pot", json={"emotions": "alegria"})  # lowercase duplicate
        assert response.status_code == 409

def test_add_duplicate_topic_returns_409():
    with patch("main.load_data", return_value=make_mock_data()):
        response = client.post("/add-pot", json={"topics": "FIESTAS"})  # uppercase duplicate
        assert response.status_code == 409


# --- PUT /items ---
def test_update_emotion_success():
    with patch("main.load_data", return_value=make_mock_data()), \
         patch("main.save_data"):
        response = client.put("/items", json={
            "kind": "emotions",
            "old_value": "Alegria",
            "new_value": "Alegría intensa"
        })
        assert response.status_code == 200
        assert response.json()["new_value"] == "Alegría intensa"

def test_update_not_found_returns_404():
    with patch("main.load_data", return_value=make_mock_data()):
        response = client.put("/items", json={
            "kind": "emotions",
            "old_value": "NoExiste",
            "new_value": "Algo"
        })
        assert response.status_code == 404

def test_update_duplicate_new_value_returns_409():
    with patch("main.load_data", return_value=make_mock_data()):
        response = client.put("/items", json={
            "kind": "emotions",
            "old_value": "Alegria",
            "new_value": "tristeza"  # already exists (case-insensitive)
        })
        assert response.status_code == 409


# --- DELETE /items ---
def test_delete_emotion_success():
    with patch("main.load_data", return_value=make_mock_data()), \
         patch("main.save_data") as mock_save:
        response = client.delete("/items?kind=emotions&value=Alegria")
        assert response.status_code == 200
        assert response.json()["removed"] == "Alegria"
        mock_save.assert_called_once()

def test_delete_not_found_returns_404():
    with patch("main.load_data", return_value=make_mock_data()):
        response = client.delete("/items?kind=emotions&value=NoExiste")
        assert response.status_code == 404

def test_delete_case_insensitive():
    with patch("main.load_data", return_value=make_mock_data()), \
         patch("main.save_data"):
        response = client.delete("/items?kind=topics&value=deportes")  # lowercase
        assert response.status_code == 200
