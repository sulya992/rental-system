# Architecture (Draft)

- Monorepo structure:
  - backend: FastAPI + PostgreSQL
  - telegram-bot: separate service using the same API / DB
  - frontend: web client consuming backend API
- Infrastructure:
  - Docker + docker-compose for local and server deployments
  - GCP VM as initial hosting target
