import pytest
import os
import json
from database import JSONDatabase


@pytest.fixture
def temp_db():
    """Fixture que crea una BD temporal con datos iniciales."""
    test_file = "test_data.json"
    initial_data = {
        "emotions": ["Alegria", "Tristeza"],
        "topics": ["Fiestas"],
        "colors": ["Azul", "Rojo"]
    }
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f)
    
    db = JSONDatabase(test_file)
    yield db
    
    if os.path.exists(test_file):
        os.remove(test_file)


# ========== CATEGORÍAS ==========

class TestCategories:
    
    def test_get_categories_success(self, temp_db):
        """Obtener todas las categorías."""
        categories = temp_db.get_categories()
        assert "emotions" in categories
        assert "topics" in categories
        assert len(categories) == 3
    
    def test_add_category_success(self, temp_db):
        """Crear una nueva categoría."""
        temp_db.add_category("animals")
        categories = temp_db.get_categories()
        assert "animals" in categories
        assert temp_db.get_items_by_category("animals") == []
    
    def test_add_category_empty_name_raises_error(self, temp_db):
        """No permitir categoría vacía."""
        with pytest.raises(ValueError, match="cannot be empty"):
            temp_db.add_category("   ")
    
    def test_add_category_duplicate_raises_error(self, temp_db):
        """No permitir duplicado de categoría."""
        with pytest.raises(ValueError, match="already exists"):
            temp_db.add_category("emotions")
    
    def test_delete_category_success(self, temp_db):
        """Eliminar una categoría."""
        temp_db.delete_category("topics")
        categories = temp_db.get_categories()
        assert "topics" not in categories
        assert "emotions" in categories
    
    def test_delete_category_not_found_raises_error(self, temp_db):
        """Error si categoría no existe."""
        with pytest.raises(ValueError, match="not found"):
            temp_db.delete_category("nonexistent")
    
    def test_delete_category_case_insensitive(self, temp_db):
        """La búsqueda de categoría es case-insensitive."""
        temp_db.delete_category("EMOTIONS")  # mayúsculas
        categories = temp_db.get_categories()
        assert "emotions" not in categories


# ========== ÍTEMS ==========

class TestItems:
    
    def test_get_all_success(self, temp_db):
        """Obtener todos los ítems."""
        data = temp_db.get_all()
        assert "emotions" in data
        assert "topics" in data
        assert len(data["emotions"]) == 2
        assert len(data["topics"]) == 1
    
    def test_get_items_by_category_success(self, temp_db):
        """Obtener ítems de una categoría específica."""
        items = temp_db.get_items_by_category("emotions")
        assert "Alegria" in items
        assert "Tristeza" in items
        assert len(items) == 2
    
    def test_get_items_by_category_not_found_raises_error(self, temp_db):
        """Error si categoría no existe."""
        with pytest.raises(ValueError, match="not found"):
            temp_db.get_items_by_category("nonexistent")
    
    def test_get_items_by_category_case_insensitive(self, temp_db):
        """La búsqueda de categoría es case-insensitive."""
        items = temp_db.get_items_by_category("EMOTIONS")
        assert "Alegria" in items
    
    def test_add_item_success(self, temp_db):
        """Agregar un ítem a una categoría."""
        temp_db.add_item("emotions", "Esperanza")
        items = temp_db.get_items_by_category("emotions")
        assert "Esperanza" in items
        assert len(items) == 3
    
    def test_add_item_empty_value_raises_error(self, temp_db):
        """No permitir ítem vacío."""
        with pytest.raises(ValueError, match="cannot be empty"):
            temp_db.add_item("emotions", "   ")
    
    def test_add_item_duplicate_raises_error(self, temp_db):
        """No permitir duplicado (case-insensitive)."""
        with pytest.raises(ValueError, match="Duplicate"):
            temp_db.add_item("emotions", "alegria")  # existe como "Alegria"
    
    def test_add_item_category_not_found_raises_error(self, temp_db):
        """Error si categoría no existe."""
        with pytest.raises(ValueError, match="not found"):
            temp_db.add_item("nonexistent", "Blue")
    
    def test_delete_item_success(self, temp_db):
        """Eliminar un ítem."""
        removed = temp_db.delete_item("emotions", "Alegria")
        assert removed == "Alegria"
        items = temp_db.get_items_by_category("emotions")
        assert "Alegria" not in items
        assert len(items) == 1
    
    def test_delete_item_case_insensitive(self, temp_db):
        """La búsqueda de ítem es case-insensitive."""
        removed = temp_db.delete_item("emotions", "alegria")  # minúsculas
        assert removed == "Alegria"  # retorna valor original
    
    def test_delete_item_not_found_raises_error(self, temp_db):
        """Error si ítem no existe."""
        with pytest.raises(ValueError, match="not found"):
            temp_db.delete_item("emotions", "Calma")
    
    def test_delete_item_category_not_found_raises_error(self, temp_db):
        """Error si categoría no existe."""
        with pytest.raises(ValueError, match="not found"):
            temp_db.delete_item("nonexistent", "Blue")
    
    def test_update_item_success(self, temp_db):
        """Actualizar un ítem."""
        result = temp_db.update_item("emotions", "Alegria", "Felicidad")
        assert result["old"] == "Alegria"
        assert result["new"] == "Felicidad"
        items = temp_db.get_items_by_category("emotions")
        assert "Felicidad" in items
        assert "Alegria" not in items
    
    def test_update_item_empty_new_value_raises_error(self, temp_db):
        """No permitir nuevo valor vacío."""
        with pytest.raises(ValueError, match="cannot be empty"):
            temp_db.update_item("emotions", "Alegria", "   ")
    
    def test_update_item_old_not_found_raises_error(self, temp_db):
        """Error si el ítem viejo no existe."""
        with pytest.raises(ValueError, match="not found"):
            temp_db.update_item("emotions", "Calma", "Paz")
    
    def test_update_item_duplicate_raises_error(self, temp_db):
        """Error si el nuevo valor ya existe."""
        with pytest.raises(ValueError, match="Duplicate"):
            temp_db.update_item("emotions", "Alegria", "tristeza")  # existe como "Tristeza"
    
    def test_update_item_category_not_found_raises_error(self, temp_db):
        """Error si categoría no existe."""
        with pytest.raises(ValueError, match="not found"):
            temp_db.update_item("nonexistent", "Blue", "Red")
    
    def test_update_item_case_insensitive(self, temp_db):
        """La búsqueda de ítem es case-insensitive."""
        result = temp_db.update_item("emotions", "ALEGRIA", "Joy")
        assert result["old"] == "Alegria"  # retorna valor original


# ========== NORMALIZACIÓN ==========

class TestNormalization:
    
    def test_normalize_whitespace(self):
        db = JSONDatabase()
        assert db.normalize("  Alegria  ") == "alegria"
    
    def test_normalize_case(self):
        db = JSONDatabase()
        assert db.normalize("FIESTAS") == "fiestas"
        assert db.normalize("Montaña") == "montaña"
    
    def test_normalize_combined(self):
        db = JSONDatabase()
        assert db.normalize("  CERVEZA  ") == "cerveza"