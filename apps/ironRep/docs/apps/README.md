# 📚 IronRep Documentation

## 🏗️ Enterprise Architecture Documentation

### 📁 Structure Overview

```
docs/
├── 📋 README.md                    # This file - documentation index
├── 🏛️ architecture/                # Technical architecture
│   ├── ER_SCHEMA_BACKEND.md       # Database ER diagram
│   └── FRONTEND_ARCHITECTURE.md    # Frontend component architecture
├── 🚀 implementation/             # Implementation guides
│   ├── ALIGNMENT_IMPLEMENTATION_COMPLETE.md
│   └── CONSEGNA_FINALE_NUTRITION_AGENT.md
├── 📊 reports/                    # Analysis & reports
│   └── AGENT_TRAINING_MASTER_PLAN.md
├── 📖 guides/                     # General guides
│   └── ARCHITECTURE.md            # DDD architecture overview
├── 🗃️ archived/                   # Historical documents (40+ files)
└── 🧹 CLEANUP_TIMESTAMP_ANALYSIS.md # Cleanup analysis report
```

---

## 🎯 Quick Navigation

### 🔥 Most Important Documents
| Document | Purpose | Last Updated |
|----------|---------|--------------|
| [ER Schema Backend](architecture/ER_SCHEMA_BACKEND.md) | Database structure | 2025-11-25 |
| [Frontend Architecture](architecture/FRONTEND_ARCHITECTURE.md) | React/TanStack structure | 2025-11-25 |
| [DDD Architecture](guides/ARCHITECTURE.md) | Domain-driven design | 2024-11-24 |
| [Agent Training](reports/AGENT_TRAINING_MASTER_PLAN.md) | AI agent specifications | 2024-11-24 |

### 🛠️ Implementation Guides
- [Backend-Frontend Alignment](implementation/ALIGNMENT_IMPLEMENTATION_COMPLETE.md)
- [Nutrition Agent](implementation/CONSEGNA_FINALE_NUTRITION_AGENT.md)

### 📊 Analysis Reports
- [Agent Training Master Plan](reports/AGENT_TRAINING_MASTER_PLAN.md)

---

## 🏛️ Architecture Overview

### Backend Stack
- **FastAPI** + SQLAlchemy 2.0
- **PostgreSQL 16** + ChromaDB (RAG)
- **UV** package manager
- **Docker** multi-stage builds

### Frontend Stack
- **React 19** + TypeScript
- **TanStack Router** + TanStack Query
- **TailwindCSS** + Framer Motion
- **Vite** build system

### AI/Agent System
- **LangChain** agents with RAG
- **UserContextRAG** for personalization
- **Medical**, **Workout**, **Nutrition** agents

---

## 📈 Recent Changes (2025-11-25)

### ✅ Completed
- Fixed food filters in frontend
- Implemented protected routes
- Integrated UserContextRAG across all agents
- Connected profile/wizard updates to RAG
- Enterprise documentation cleanup

### 🔄 Current Status
- **Backend**: ✅ Production ready
- **Frontend**: ✅ Production ready
- **Deployment**: ✅ Live at https://ironrep.it
- **Documentation**: ✅ Clean & organized

---

## 🗂️ Historical Archive

The `/archived/` folder contains 40+ historical documents that were consolidated during the enterprise cleanup on 2025-11-25. These include:

- Duplicate analysis reports
- Multiple architecture versions
- Implementation status documents
- Various proposal documents

**Note**: These files are preserved for reference but should not be used for current development.

---

## 🚀 Getting Started

1. **For Database Schema**: See `architecture/ER_SCHEMA_BACKEND.md`
2. **For Frontend Structure**: See `architecture/FRONTEND_ARCHITECTURE.md`
3. **For Development Guidelines**: See `guides/ARCHITECTURE.md`
4. **For AI Agent Details**: See `reports/AGENT_TRAINING_MASTER_PLAN.md`

---

*Last updated: 2025-11-25*
*Documentation version: 2.0 (post-cleanup)*
