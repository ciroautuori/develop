# Centralized Services Architecture

## Overview
This project uses a centralized service messuage to host multiple applications (`ironRep`, `iss`, `markettina`, `studiocentos`) on a single server.

## Core Infrastructure
- **Gateway**: Nginx (handling SSL termination and routing)
- **Database**: PostgreSQL (shared instance)
- **Cache**: Redis (shared instance)
- **AI**: Ollama & ChromaDB (shared instances)

## Applications
1. **IronRep**: Local Port 8000 (Backend) / 80 (Frontend)
2. **ISS**: Local Port 8000 (Backend) / 3000 (Frontend)
3. **Markettina**: Local Port 8000 (Backend) / 80 (Frontend)
4. **StudioCentos**: Local Port 8000 (Backend) / 80 (Frontend)

## Maintenance
- **Logs**: `docker logs <container_name>`
- **Restart**: `docker compose restart <service>`
