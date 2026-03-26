# Pot Game API 🍯

API REST robusta construida con _FastAPI_ diseñada para contribuir en la escritura creativa mediante la colisión aleatoria de conceptos (emociones y tópicos) y la gestión integral de un catálogo creativo con CRUD implementado.

## 🚀 Inicio Rápido

### Requisitos Previos

•⁠ ⁠Python 3.11+
•⁠ ⁠Git

### Instalación

```bash
# 1. Clonar el repositorio
git clone [https://github.com/tu-usuario/pot-Game.git](https://github.com/tu-usuario/Pot-Game.git)
cd Pot-Game

# 2. Configurar entorno virtual
python3 -m venv venv

# 3. Activar entorno
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

```bash
uvicorn main:app --reload
```

La API estará disponible en: http://127.0.0.1:8000

Documentación interactiva (Swagger UI):

- http://127.0.0.1:8000/docs

## 🛠️ Stack Técnico e Infraestructura

- Framework: FastAPI (Python 3.11)
- Arquitectura: Desacoplamiento por capas (API, lógica de datos y persistencia)
- Persistencia: JSON local con validación de esquemas vía Pydantic
- Calidad: Ruff (análisis estático de código)
- CI/CD: GitHub Actions (pipeline automatizado de lint y tests)

## 🧪 Calidad y Pruebas

Este proyecto utiliza Pytest para garantizar la integridad de los endpoints y la lógica de negocio.

```bash
# Ejecutar linter (Ruff)
ruff check .

# Ejecutar suite de tests (integración y unitarios)
pytest

# Generar reporte de cobertura de código
pytest --cov=main --cov=database --cov-report=term-missing
```

## 🛰️ Referencia de Endpoints

| Método | Endpoint | Funcionalidad                                            |
| ------ | -------- | -------------------------------------------------------- |
| GET    | /        | Health check / root                                      |
| GET    | /pot     | Genera una combinación aleatoria                         |
| GET    | /items   | Lista todos los elementos del catálogo                   |
| POST   | /add-pot | Registra un nuevo ítem (validación Pydantic)             |
| PUT    | /items   | Actualiza un ítem existente                              |
| DELETE | /items   | Elimina un ítem (requiere query params `kind` y `value`) |

## 🔍 Verificación del Sistema

Para confirmar que la instalación fue exitosa, ejecuta:

```bash
curl http://127.0.0.1:8000/
```

Debe retornar algo como:

```json
{ "message": "Pot-Game API is reading from JSON!" }
```

## ⚠️ Troubleshooting

- Error: command not found: uvicorn
  Activa el entorno virtual (`venv`) y reinstala dependencias con `pip install -r requirements.txt`.

- Fallo en GitHub Actions
  Verifica que todas las dependencias nuevas estén en `requirements.txt` y vuelve a ejecutar CI.

- Problemas de persistencia
  Si `data.json` no se encuentra o está corrupto, restaura el archivo en la raíz del proyecto.

## Tracks de Desarrollo Futuro (Roadmap)

- [ ] Migración de JSON a persistencia relacional con SQLite
- [ ] Implementación de autenticación basada en JWT
- [ ] Containerización con Docker para despliegue simplificado
