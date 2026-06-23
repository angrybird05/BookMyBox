# BookMyBox — Production Backend

BookMyBox is an enterprise-grade box cricket ground booking platform. This directory houses the complete production-ready backend system built using **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, **PostgreSQL**, **Redis**, and **Celery**.

---

## Features

- **Asynchronous Architecture**: FastAPI with fully async database queries using SQLAlchemy 2.0 ORM and `asyncpg`.
- **Advanced Booking Engine**: Multi-slot bookings with transactional row locking (`SELECT FOR UPDATE`) and Redis checkout locks to eliminate double-booking race conditions.
- **Smart Discount Engine**: Dynamic bulk booking discounts (10% on 3+ slots) and promo code validation capped to specified limits.
- **Secure Wallet & Transactions**: Internal wallet ledger (debits/credits) for instant booking payments and automatic partial/full cancellations refunds.
- **Real-Time Synchronization**: WebSockets update ground slot availabilities in real-time as users block, book, or cancel.
- **DevOps & Scaling Ready**: Ready to deploy with multi-stage Docker build, Docker Compose, Nginx, and Kubernetes manifests (including HPA scaling and PV storage).
- **Background Jobs**: Celery task runner for asynchronous emails, OTP sends, and ticket PDF generation.
- **Enterprise Security**: Rate limiting, defense-in-depth security headers, and JWT-based Role-Based Access Control (RBAC).

---

## Technology Stack

- **Framework**: FastAPI (Python 3.11/3.12/3.14)
- **Database**: PostgreSQL (via asyncpg)
- **Caching & Locking**: Redis (v7)
- **Migrations**: Alembic
- **Task Queue**: Celery (Redis Broker)
- **Server/Proxy**: Uvicorn & Nginx
- **Containerization & Orchestration**: Docker, Docker Compose, Kubernetes

---

## Scaffolding & Structure

```
backend/
├── app/
│   ├── main.py                  # App initialization, routes registration, and exception handlers
│   ├── api/
│   │   ├── deps.py              # Dependency injections (Auth, DB, Redis)
│   │   └── v1/
│   │       ├── auth.py          # Registration, login, JWT rotation, OTP verify
│   │       ├── grounds.py       # Browse grounds, get slots, view reviews
│   │       ├── bookings.py      # Checkout booking, cancel, ticket PDF
│   │       ├── wallet.py        # Wallet balance, transactions history, top-up
│   │       └── admin.py         # Dashboard stats, grounds CRUD, block users
│   ├── core/
│   │   ├── config.py            # Pydantic-settings config validation
│   │   └── security.py          # JWT generation, token verification, bcrypt hashing
│   ├── database/
│   │   ├── base.py              # DeclarativeBase, UUIDMixin, TimestampMixin
│   │   └── session.py           # Async engine and async session makers
│   ├── models/                  # SQLAlchemy ORM Models
│   │   ├── user.py
│   │   ├── ground.py
│   │   ├── booking.py
│   │   └── wallet.py
│   ├── repositories/            # Modular CRUD database layers
│   ├── services/                # Core Business Logic services
│   ├── middleware/              # RateLimit, Cors, SecurityHeaders, RequestId
│   ├── workers/                 # Celery app and email/ticket PDF generation tasks
│   └── core/websocket.py        # WebSocket client manager and updates broadcaster
├── alembic/                     # Alembic configuration and migrations scripts
├── tests/                       # Complete automated test suite
│   ├── conftest.py              # Pytest setup and mock connection fixtures
│   ├── unit/                    # Unit tests for Services logic
│   └── load/                    # Locust load testing script
├── nginx/                       # Nginx reverse proxy configuration
├── k8s/                         # Kubernetes manifests (Deployments, Services, HPA, Ingress)
├── Dockerfile                   # Multi-stage optimized Docker build
└── docker-compose.yml           # Local multi-container development orchestration
```

---

## Local Development Setup

### Option 1: Docker Compose (Recommended)

To run the entire system including PostgreSQL, Redis, Celery, Nginx, and the FastAPI application in one command:

1. Clone the repository and navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Generate a local `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Spin up all services:
   ```bash
   docker-compose up --build
   ```

The application is now accessible via the Nginx reverse proxy at `http://localhost`. 
- **Interactive Documentation**: `http://localhost/docs` (Swagger)
- **Alternative Docs**: `http://localhost/redoc`

---

### Option 2: Manual Development Setup

If you prefer to run services manually on your local host:

1. **Prerequisites**: Ensure you have Python 3.11+, PostgreSQL, and Redis installed.

2. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**: Create a `.env` file in the `backend/` directory using `.env.example` as a reference.

5. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start Redis**: Ensure your local Redis server is running on `port 6379`.

7. **Start Celery Worker** (in a separate terminal):
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```

8. **Start Application** (Uvicorn Dev Server):
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

---

## Database Migrations

This project uses Alembic to manage relational schema changes. 

- **Create a new migration**:
  ```bash
  alembic revision --autogenerate -m "description_of_change"
  ```
- **Apply migrations**:
  ```bash
  alembic upgrade head
  ```
- **Rollback last migration**:
  ```bash
  alembic downgrade -1
  ```

---

## Automated Testing

### Unit and Integration Tests

Run unit tests via Pytest (uses mock database and cache fixtures, so no external service is required):

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=app --cov-report=html
```

### Load Testing

Locust is configured to run load tests against the endpoints to evaluate concurrency limits:

1. Start the API locally.
2. Start Locust:
   ```bash
   locust -f tests/load/locustfile.py
   ```
3. Open `http://localhost:8089` in your browser, enter target host URL, spawn rate, and simulate thousands of users browsing cricket grounds.

---

## Kubernetes Production Deployment

The `k8s/` folder contains Kubernetes manifests configured for enterprise-grade deployment:

1. Set up the namespace:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   ```
2. Apply configurations and secrets:
   ```bash
   kubectl apply -f k8s/configmap.yaml -f k8s/secrets.yaml
   ```
3. Setup persistent storage:
   ```bash
   kubectl apply -f k8s/pvc.yaml
   ```
4. Start database and caching layers:
   ```bash
   kubectl apply -f k8s/postgres-deployment.yaml -f k8s/redis-deployment.yaml
   ```
5. Deploy backend and background workers:
   ```bash
   kubectl apply -f k8s/backend-deployment.yaml -f k8s/worker-deployment.yaml
   ```
6. Route traffic using Ingress and scale automatically using HPA:
   ```bash
   kubectl apply -f k8s/ingress.yaml -f k8s/hpa.yaml
   ```
