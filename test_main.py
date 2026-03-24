from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

MOCK_DATA = {
    "emotions": ["Alegria", "Tristeza"],
    "topics": ["Fiestas", "Deportes"]
}

# --- GET / ---
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Pot-Game API is reading from JSON!"}

# --- GET /pot ---
def test_get_pot_success():
    with patch("main.db.get_emotions", return_value=["Alegria", "Tristeza"]), \
         patch("main.db.get_topics", return_value=["Fiestas", "Deportes"]):
        response = client.get("/pot")
        assert response.status_code == 200
        data = response.json()
        assert data["emotions"] in ["Alegria", "Tristeza"]
        assert data["topics"] in ["Fiestas", "Deportes"]

def test_get_pot_empty_lists():
    with patch("main.db.get_emotions", return_value=[]), \
         patch("main.db.get_topics", return_value=[]):
        response = client.get("/pot")
        assert response.status_code == 404

# --- GET /items ---
def test_list_all_items():
    with patch("main.db.get_all", return_value=MOCK_DATA):
        response = client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert data["emotions"] == ["Alegria", "Tristeza"]
        assert data["topics"] == ["Fiestas", "Deportes"]
        assert data["counts"]["emotions"] == 2
        assert data["counts"]["topics"] == 2

# --- POST /add-pot ---
def test_add_emotion_success():
    with patch("main.db.add_item") as mock_add_item:
        response = client.post("/add-pot", json={"emotions": "Esperanza"})
        assert response.status_code == 200
        assert response.json()["added"]["emotions"] == "Esperanza"
        assert response.json()["added"]["topics"] is None
        mock_add_item.assert_called_once_with("emotions", "Esperanza")

def test_add_topic_success():
    with patch("main.db.add_item") as mock_add_item:
        response = client.post("/add-pot", json={"topics": "Videojuegos"})
        assert response.status_code == 200
        assert response.json()["added"]["topics"] == "Videojuegos"
        assert response.json()["added"]["emotions"] is None
        mock_add_item.assert_called_once_with("topics", "Videojuegos")

def test_add_both_fields_success():
    with patch("main.db.add_item") as mock_add_item:
        response = client.post("/add-pot", json={"emotions": "Calma", "topics": "Montaña"})
        assert response.status_code == 200
        assert response.json()["added"] == {
            "emotions": "Calma",
            "topics": "Montaña"
        }
        assert mock_add_item.call_count == 2

def test_add_empty_body_returns_400():
    response = client.post("/add-pot", json={})
    assert response.status_code == 400

def test_add_duplicate_emotion_returns_409():
    with patch("main.db.add_item", side_effect=ValueError("Duplicate item")):
        response = client.post("/add-pot", json={"emotions": "alegria"})  # lowercase duplicate
        assert response.status_code == 409

def test_add_duplicate_topic_returns_409():
    with patch("main.db.add_item", side_effect=ValueError("Duplicate item")):
        response = client.post("/add-pot", json={"topics": "FIESTAS"})  # uppercase duplicate
        assert response.status_code == 409


# --- PUT /items ---
def test_update_item_success():
    with patch("main.db.update_item", return_value={"old": "Alegria", "new": "Esperanza"}):
        response = client.put("/items", json={
            "kind": "emotions",
            "old_value": "Alegria",
            "new_value": "Esperanza"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["kind"] == "emotions"
        assert data["old_value"] == "Alegria"
        assert data["new_value"] == "Esperanza"

def test_update_item_not_found_returns_404():
    with patch("main.db.update_item", side_effect=ValueError("Emotion not found: Alegria")):
        response = client.put("/items", json={
            "kind": "emotions",
            "old_value": "Alegria",
            "new_value": "Esperanza"
        })
        assert response.status_code == 404

def test_update_item_duplicate_returns_409():
    with patch("main.db.update_item", side_effect=ValueError('Duplicate emotion: "Tristeza" already exists.')):
        response = client.put("/items", json={
            "kind": "emotions",
            "old_value": "Alegria",
            "new_value": "Tristeza"
        })
        assert response.status_code == 409

# --- DELETE /items ---
def test_delete_item_success():
    with patch("main.db.delete_item", return_value="Alegria") as mock_delete:
        response = client.delete("/items?kind=emotions&value=Alegria")
        assert response.status_code == 200
        assert response.json()["removed"] == "Alegria"
        mock_delete.assert_called_once_with("emotions", "Alegria")


def test_delete_item_not_found_returns_404():
    with patch("main.db.delete_item", side_effect=ValueError("Emotion not found: Alegria")):
        response = client.delete("/items?kind=emotions&value=Alegria")
        assert response.status_code == 404
