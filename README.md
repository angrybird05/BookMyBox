<h2>BookMyBox</h2>
Enterprise-grade booking platform for box-cricket grounds — backend in FastAPI (async) with a TypeScript + React frontend (Vite). Designed for high-concurrency booking flows (transactional row-locking, Redis locks), background workers, and production deployment via Docker / Kubernetes.

<h3>Quick summary</h3>
<h4>Purpose:</h4> Allow users to browse grounds, block/select slots, complete multi-slot bookings, manage wallets, and receive real-time updates.
<h4>Audience:</h4> Developers, DevOps, and reviewers who want to run, extend, or deploy the platform.
<h3>Tech stack</h3>
<h4>Language(s):</h4> Python (backend), TypeScript + React (frontend)
<h4>Backend framework & runtime: </h4>FastAPI (async), Uvicorn
<h4>Frontend framework & runtime:</h4> React 19 + TypeScript, built with Vite
<h4>Database & infra:</h4> PostgreSQL (asyncpg), Redis (caching + locks), Celery (background tasks)
<h4>Migrations & schema:</h4> Alembic
<h4>Containerization / orchestration:</h4> Docker, Docker Compose, Kubernetes manifests present
<h3>Notable libraries:</h3>
<h4>Backend:</h4> SQLAlchemy 2.0 (async), Alembic, Celery
<h4>Frontend:</h4> TanStack Router / React Query, Radix UI, Tailwind CSS, Zod, Vite
