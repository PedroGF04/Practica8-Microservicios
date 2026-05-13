# 🎮 El Salto del Trazacaminos — Práctica de Microservicios

Simulador backend de un sistema de "tiradas" (Gacha) implementado con arquitectura de microservicios y Docker.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE (Browser)                     │
│                     http://localhost:8080                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────────┐
│                    Frontend (Nginx)                          │
│                     puerto 8080                             │
└───────────────────────────┬─────────────────────────────────┘
                            │ Proxy /api/*
┌───────────────────────────▼─────────────────────────────────┐
│                    API Gateway                               │
│              puerto 5000  (Orquestador)                     │
└──────┬────────────────────┬────────────────┬────────────────┘
       │                    │                │
┌──────▼──────┐    ┌────────▼──────┐  ┌─────▼───────────┐
│  Inventario │    │  Banner/RNG   │  │  Pity/Historial │
│  puerto 5001│    │  puerto 5002  │  │  puerto 5003    │
│  SQLite     │    │  Stateless    │  │  SQLite         │
└─────────────┘    └───────────────┘  └─────────────────┘
```

## 📦 Microservicios

### 1. Microservicio de Inventario (:5001)
Gestiona los recursos del jugador y su colección de personajes.
- `GET  /player/:id`              — Datos completos del jugador
- `GET  /player/:id/resources`    — Monedas y tickets
- `POST /player/:id/spend`        — Gastar recursos
- `POST /player/:id/add_character`— Añadir personaje al inventario
- `POST /player/:id/add_resources`— Añadir recursos (monedas/tickets)
- `GET  /player/:id/inventory/stats` — Estadísticas por rareza
- `GET  /health`

### 2. Microservicio de Banner/RNG (:5002)
Contiene toda la lógica matemática y probabilidades.

**Sistema de Pity:**
- Base SSR: 0.6%, SR: 5.1%, R: 94.3%
- **Soft Pity** (pull 74+): la probabilidad de SSR aumenta 6% por pull
- **Hard Pity** (pull 90): garantiza SSR al 100%

Endpoints:
- `GET  /banners`                         — Listar todos los banners
- `GET  /banners/:id`                     — Detalles de un banner
- `POST /pull`                            — Ejecutar tirada(s)
- `GET  /simulate_rates?banner_id=...`    — Tabla de probabilidades por pity

### 3. Microservicio de Pity/Historial (:5003)
Registra cada tirada y ajusta dinámicamente las probabilidades.
- `GET  /pity/:player/:banner`      — Estado actual del pity
- `POST /record_pull`               — Registrar resultados
- `GET  /history/:player`           — Historial de tiradas
- `GET  /stats/:player`             — Estadísticas globales

### 4. API Gateway (:5000)
Orquesta las llamadas entre microservicios. El cliente solo habla con él.

**Flujo de una tirada:**
1. Obtiene info del banner (Banner Service)
2. Verifica el pity actual (Pity Service)
3. Deduce recursos (Inventory Service)
4. Ejecuta el RNG (Banner Service)
5. Registra historial y pity (Pity Service)
6. Añade personajes al inventario (Inventory Service)

---

## 🚀 Cómo ejecutar

### Prerrequisitos
- Docker Desktop instalado
- Docker Compose v2+

### Iniciar todo el sistema
```bash
cd gacha-microservices
docker compose up --build
```

### Acceder
| Servicio   | URL                         |
|------------|------------------------------|
| Frontend   | http://localhost:8081        |
| API Gateway| http://localhost:5000/health |
| Inventario | http://localhost:5001/health |
| Banner     | http://localhost:5002/health |
| Pity       | http://localhost:5003/health |

### Detener
```bash
docker compose down
# Para borrar también los datos:
docker compose down -v
```

---

## 🧪 Pruebas con curl

```bash
# Ver estado del jugador
curl http://localhost:5000/api/player/player1

# Hacer 1 tirada con ticket
curl -X POST http://localhost:5000/api/pull \
  -H "Content-Type: application/json" \
  -d '{"player_id":"player1","banner_id":"standard","count":1}'

# Hacer 10 tiradas
curl -X POST http://localhost:5000/api/pull \
  -H "Content-Type: application/json" \
  -d '{"player_id":"player1","banner_id":"limited","count":10}'

# Ver historial
curl http://localhost:5000/api/history/player1

# Ver estadísticas
curl http://localhost:5000/api/stats/player1

# Añadir recursos
curl -X POST http://localhost:5000/api/player/player1/add_resources \
  -H "Content-Type: application/json" \
  -d '{"tickets":50,"coins":10000}'

# Probabilidades del banner estándar
curl http://localhost:5002/simulate_rates?banner_id=standard
```

---

## 📁 Estructura del Proyecto

```
gacha-microservices/
├── docker-compose.yml
├── README.md
├── api-gateway/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/app.py
├── inventory-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/app.py
├── banner-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/app.py
├── pity-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/app.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── index.html
```

---

## 🎓 Conceptos de Microservicios aplicados

| Concepto | Implementación |
|----------|---------------|
| **Separación de responsabilidades** | Cada servicio maneja un dominio específico |
| **Comunicación via HTTP/REST** | Los servicios se comunican por red interna |
| **API Gateway Pattern** | Un punto de entrada único para el cliente |
| **Persistencia independiente** | Cada servicio tiene su propia base de datos SQLite |
| **Containerización** | Cada servicio corre en su propio contenedor Docker |
| **Service Discovery** | Docker Compose gestiona los nombres de host |
| **Health Checks** | Cada servicio expone `/health` |
| **Volúmenes persistentes** | Los datos sobreviven reinicios del contenedor |
| **Redes internas** | Los servicios internos no son accesibles desde fuera |

---

*Práctica elaborada para materia de Sistemas Distribuidos*
# Practica8-Microservicios
