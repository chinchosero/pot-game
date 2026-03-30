# Pot Game API 🍯

API REST construida con FastAPI para apoyar escritura creativa mediante combinaciones aleatorias de emociones y topicos, ademas de gestion CRUD del catalogo.

## 🚀 Inicio Rapido

### Requisitos Previos

- Python 3.11+
- Git
- Docker (opcional, solo si quieres ejecutar en contenedor)

### Instalacion

```bash
# 1. Clonar el repositorio
git clone https://github.com/chinchosero/pot-game.git
cd pot-game

# 2. Configurar entorno virtual
python3 -m venv venv

# 3. Activar entorno
# macOS/Linux:
source venv/bin/activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### Ejecucion Local

```bash
uvicorn main:app --reload
```

La API estara disponible en: http://127.0.0.1:8000

Documentacion interactiva (Swagger UI):

- http://127.0.0.1:8000/docs

## 🐳 Despliegue con Docker

Si prefieres ejecutar la aplicacion de forma aislada, usa Docker.

### 1. Construir la imagen

```bash
docker build -t pot-game-api .
```

### 2. Ejecutar el contenedor

```bash
docker run -d --name pot-game-container -p 8000:8000 pot-game-api
```

### 3. Comandos utiles de Docker

```bash
# Ver contenedores en ejecucion
docker ps

# Ver logs en tiempo real
docker logs -f pot-game-container

# Detener contenedor
docker stop pot-game-container

# Eliminar contenedor
docker rm pot-game-container
```

## 🛠️ Stack Tecnico e Infraestructura

- Framework: FastAPI (Python 3.11)
- Arquitectura: desacoplamiento por capas (API, logica de datos y persistencia)
- Persistencia: JSON local con validacion de esquemas via Pydantic
- Calidad: Ruff (analisis estatico de codigo)
- CI/CD: GitHub Actions (pipeline automatizado de lint y tests)

## 🧪 Calidad y Pruebas

Este proyecto utiliza pytest para garantizar la integridad de endpoints y logica de negocio.

```bash
# Ejecutar linter (Ruff)
ruff check .

# Ejecutar suite de tests (integracion y unitarios)
pytest

# Generar reporte de cobertura de codigo
pytest --cov=main --cov=database --cov-report=term-missing
```

## 🛰️ Referencia de Endpoints

| Metodo | Endpoint | Funcionalidad                                            |
| ------ | -------- | -------------------------------------------------------- |
| GET    | /        | Health check / root                                      |
| GET    | /pot     | Genera una combinacion aleatoria                         |
| GET    | /items   | Lista todos los elementos del catalogo                   |
| POST   | /add-pot | Registra un nuevo item (validacion Pydantic)             |
| PUT    | /items   | Actualiza un item existente                              |
| DELETE | /items   | Elimina un item (requiere query params `kind` y `value`) |

## 🔍 Verificacion del Sistema

Para confirmar que la instalacion fue exitosa, ejecuta:

```bash
curl http://127.0.0.1:8000/
```

Debe retornar algo como:

```json
{ "message": "Pot-Game API is reading from JSON!" }
```

## ⚠️ Troubleshooting

- Error: `command not found: uvicorn`
  Activa el entorno virtual (`venv`) y reinstala dependencias con `pip install -r requirements.txt`.

- Fallo en GitHub Actions
  Verifica que nuevas dependencias esten en `requirements.txt` y vuelve a ejecutar CI.

- Problemas de persistencia
  Si `data.json` no se encuentra o esta corrupto, restauralo en la raiz del proyecto.

## Tracks de Desarrollo Futuro (Roadmap)

- [ ] Migracion de JSON a persistencia relacional con SQLite
- [ ] Implementacion de autenticacion basada en JWT
- [ ] Containerizacion con Docker para despliegue simplificado
