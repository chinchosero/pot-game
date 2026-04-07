from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

MOCK_DATA = {
    "emotions": ["Alegria", "Tristeza"],
    "topics": ["Fiestas", "Deportes"],
    "colors": ["Azul", "Rojo"]
}


# ========== ROOT ==========

def test_read_root():
    """GET / debe retornar mensaje bienvenida."""
    response = client.get("/")
    assert response.status_code == 200
    assert "dynamic categories" in response.json()["message"].lower()


# ========== CATEGORÍAS ==========

class TestCategoriesEndpoints:
    
    def test_list_categories_success(self):
        """GET /categories lista todas las categorías."""
        with patch("main.db.get_categories", return_value=["emotions", "topics", "colors"]):
            response = client.get("/categories")
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 3
            assert "emotions" in data["categories"]
            assert "topics" in data["categories"]
            assert "colors" in data["categories"]
    
    def test_list_categories_empty(self):
        """GET /categories cuando no hay categorías."""
        with patch("main.db.get_categories", return_value=[]):
            response = client.get("/categories")
            assert response.status_code == 200
            assert response.json()["count"] == 0
    
    def test_create_category_success(self):
        """POST /categories crea una categoría."""
        with patch("main.db.add_category") as mock_add:
            response = client.post("/categories", json={"name": "animals"})
            assert response.status_code == 200
            assert "created successfully" in response.json()["message"]
            mock_add.assert_called_once_with("animals")
    
    def test_create_category_duplicate_returns_409(self):
        """POST /categories con duplicado retorna 409."""
        with patch("main.db.add_category", side_effect=ValueError("already exists")):
            response = client.post("/categories", json={"name": "emotions"})
            assert response.status_code == 409
    
    def test_delete_category_success(self):
        """DELETE /categories/{name} elimina categoría."""
        with patch("main.db.delete_category") as mock_delete:
            response = client.delete("/categories/animals")
            assert response.status_code == 200
            assert "deleted successfully" in response.json()["message"]
            mock_delete.assert_called_once_with("animals")
    
    def test_delete_category_not_found_returns_404(self):
        """DELETE /categories/{name} inexistente retorna 404."""
        with patch("main.db.delete_category", side_effect=ValueError("not found")):
            response = client.delete("/categories/nonexistent")
            assert response.status_code == 404


# ========== ITEMS ==========

class TestItemsEndpoints:
    
    def test_list_all_items_success(self):
        """GET /items sin query retorna todas las categorías."""
        with patch("main.db.get_all", return_value=MOCK_DATA):
            response = client.get("/items")
            assert response.status_code == 200
            data = response.json()
            assert data["items"] == MOCK_DATA
            assert data["summary"]["emotions"] == 2
            assert data["summary"]["topics"] == 2
            assert data["summary"]["colors"] == 2
    
    def test_list_items_filtered_by_category(self):
        """GET /items?category=X retorna ítems de una categoría."""
        with patch("main.db.get_items_by_category", return_value=["Alegria", "Tristeza"]):
            response = client.get("/items?category=emotions")
            assert response.status_code == 200
            data = response.json()
            assert data["emotions"] == ["Alegria", "Tristeza"]
            assert data["count"] == 2
    
    def test_list_items_category_not_found_returns_404(self):
        """GET /items?category=X inexistente retorna 404."""
        with patch("main.db.get_items_by_category", side_effect=ValueError("not found")):
            response = client.get("/items?category=nonexistent")
            assert response.status_code == 404
    
    def test_create_item_success(self):
        """POST /items crea un ítem."""
        with patch("main.db.add_item") as mock_add:
            response = client.post("/items", json={
                "category": "emotions",
                "value": "Esperanza"
            })
            assert response.status_code == 200
            assert "added successfully" in response.json()["message"]
            mock_add.assert_called_once_with("emotions", "Esperanza")
    
    def test_create_item_category_not_found_returns_404(self):
        """POST /items con categoría inexistente retorna 404."""
        with patch("main.db.add_item", side_effect=ValueError("Category not found")):
            response = client.post("/items", json={
                "category": "nonexistent",
                "value": "Something"
            })
            assert response.status_code == 404
    
    def test_create_item_duplicate_returns_409(self):
        """POST /items con duplicado retorna 409."""
        with patch("main.db.add_item", side_effect=ValueError("Duplicate item")):
            response = client.post("/items", json={
                "category": "emotions",
                "value": "Alegria"
            })
            assert response.status_code == 409
    
    def test_create_item_empty_value_returns_400(self):
        """POST /items con valor vacío retorna 400."""
        with patch("main.db.add_item", side_effect=ValueError("Value cannot be empty")):
            response = client.post("/items", json={
                "category": "emotions",
                "value": "   "
            })
            assert response.status_code == 400
    
    def test_update_item_success(self):
        """PUT /items actualiza un ítem."""
        with patch("main.db.update_item", return_value={"old": "Alegria", "new": "Joy"}):
            response = client.put("/items", json={
                "category": "emotions",
                "old_value": "Alegria",
                "new_value": "Joy"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["old_value"] == "Alegria"
            assert data["new_value"] == "Joy"
    
    def test_update_item_not_found_returns_404(self):
        """PUT /items con ítem inexistente retorna 404."""
        with patch("main.db.update_item", side_effect=ValueError("not found")):
            response = client.put("/items", json={
                "category": "emotions",
                "old_value": "Calma",
                "new_value": "Peace"
            })
            assert response.status_code == 404
    
    def test_update_item_duplicate_returns_409(self):
        """PUT /items con nuevo valor duplicado retorna 409."""
        with patch("main.db.update_item", side_effect=ValueError("Duplicate item")):
            response = client.put("/items", json={
                "category": "emotions",
                "old_value": "Alegria",
                "new_value": "Tristeza"
            })
            assert response.status_code == 409
    
    def test_delete_item_success(self):
        """DELETE /items elimina un ítem."""
        with patch("main.db.delete_item", return_value="Alegria") as mock_delete:
            response = client.delete("/items?category=emotions&value=Alegria")
            assert response.status_code == 200
            data = response.json()
            assert data["removed"] == "Alegria"
            mock_delete.assert_called_once_with("emotions", "Alegria")
    
    def test_delete_item_not_found_returns_404(self):
        """DELETE /items con ítem inexistente retorna 404."""
        with patch("main.db.delete_item", side_effect=ValueError("not found")):
            response = client.delete("/items?category=emotions&value=Calma")
            assert response.status_code == 404


# ========== POT (RECIPE) ==========

class TestPotEndpoint:
    
    def test_get_pot_single_category_success(self):
        """GET /pot?categories=emotions retorna una emoción aleatoria."""
        with patch("main.db.get_items_by_category", return_value=["Alegria", "Tristeza"]):
            response = client.get("/pot?categories=emotions")
            assert response.status_code == 200
            data = response.json()
            assert "ingredients" in data
            assert data["ingredients"]["emotions"] in ["Alegria", "Tristeza"]
    
    def test_get_pot_multiple_categories_success(self):
        """GET /pot con múltiples categorías retorna un ítem por categoría."""
        def mock_get_items(category):
            items_map = {
                "emotions": ["Alegria", "Tristeza"],
                "topics": ["Fiestas", "Deportes"],
                "colors": ["Azul", "Rojo"]
            }
            if category in items_map:
                return items_map[category]
            raise ValueError("not found")
        
        with patch("main.db.get_items_by_category", side_effect=mock_get_items):
            response = client.get("/pot?categories=emotions&categories=topics&categories=colors")
            assert response.status_code == 200
            data = response.json()
            assert "ingredients" in data
            assert len(data["ingredients"]) == 3
            assert data["ingredients"]["emotions"] in ["Alegria", "Tristeza"]
            assert data["ingredients"]["topics"] in ["Fiestas", "Deportes"]
            assert data["ingredients"]["colors"] in ["Azul", "Rojo"]
    
    def test_get_pot_category_not_found_returns_404(self):
        """GET /pot con categoría inexistente retorna 404."""
        with patch("main.db.get_items_by_category", side_effect=ValueError("not found")):
            response = client.get("/pot?categories=nonexistent")
            assert response.status_code == 404
    
    def test_get_pot_empty_category_returns_404(self):
        """GET /pot con categoría vacía retorna 404."""
        with patch("main.db.get_items_by_category", return_value=[]):
            response = client.get("/pot?categories=emotions")
            assert response.status_code == 404
    
    def test_get_pot_missing_categories_returns_error(self):
        """GET /pot sin parámetro retorna error."""
        response = client.get("/pot")
        assert response.status_code == 422  # Validation error (required query param)