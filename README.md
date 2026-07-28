<h2>BookMyBox</h2>
<h5>Enterprise-grade booking platform for box-cricket grounds — backend in FastAPI (async) with a TypeScript + React frontend (Vite). Designed for high-concurrency booking flows (transactional row-locking, Redis locks), background workers, and production deployment via Docker / Kubernetes.</h5>

<h2>Quick summary</h2>
<h3>Purpose:</h3> Allow users to browse grounds, block/select slots, complete multi-slot bookings, manage wallets, and receive real-time updates.
<h3>Audience:</h3> Developers, DevOps, and reviewers who want to run, extend, or deploy the platform.
<h2>Tech stack</h2>
<h3>Language(s):</h3> Python (backend), TypeScript + React (frontend)
<h3>Backend framework & runtime: </h3>FastAPI (async), Uvicorn
<h3>Frontend framework & runtime:</h3> React 19 + TypeScript, built with Vite
<h3>Database & infra:</h3> PostgreSQL (asyncpg), Redis (caching + locks), Celery (background tasks)
<h3>Migrations & schema:</h3> Alembic
<h3>Containerization / orchestration:</h3> Docker, Docker Compose, Kubernetes manifests present
<h2>T</h2>
<h3>Backend:</h3> SQLAlchemy 2.0 (async), Alembic, Celery
<h3>Frontend:</h3> TanStack Router / React Query, Radix UI, Tailwind CSS, Zod, Vite
