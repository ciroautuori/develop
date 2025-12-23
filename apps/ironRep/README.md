# IronRep - README

**AI-Powered Rehabilitation Platform**

[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-blue)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)

## 🎯 Overview

IronRep is a multi-agent AI rehabilitation platform that provides personalized workout plans, nutritional guidance, and pain management through intelligent conversational interfaces.

## ✨ Features

- 🤖 **Multi-Agent AI System**: Workout Coach, Nutritionist, Medical Advisor
- 💪 **Adaptive Workouts**: Personalized training based on pain levels and progress
- 🍎 **Nutrition Planning**: AI-powered meal recommendations
- 📊 **Progress Tracking**: Comprehensive analytics and calendar views
- 🏥 **Pain Management**: Daily assessments with intelligent recommendations
- 🔒 **Secure Authentication**: Session-based token storage
- ♿ **Accessibility First**: ARIA labels, keyboard navigation, screen reader support

## 🏗️ Tech Stack

### Frontend
- React 19 + TypeScript
- Vite (build tool)
- TanStack Router + Query
- Zustand (state management)
- Tailwind CSS
- Framer Motion

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy 2.0
- Alembic (migrations)
- LangChain + OpenAI
- PostgreSQL 16
- ChromaDB (RAG)

### Infrastructure
- Docker + Docker Compose
- Arch Linux
- pnpm (frontend)
- uv (Python)

## 🚀 Quick Start

### Prerequisites
```bash
# Arch Linux
sudo pacman -S docker docker-compose nodejs pnpm postgresql

# Python UV
sudo pacman -S uv
```

### Installation

```bash
# Clone repo
git clone https://github.com/yourusername/ironRep.git
cd ironRep

# Frontend
cd apps/frontend
pnpm install
pnpm dev

# Backend
cd apps/backend
uv sync
uv run uvicorn main:app --reload
```

### Docker

```bash
docker-compose up -d
```

## 📚 Documentation

- [Development Guide](./apps/frontend/DEVELOPMENT_GUIDE.md)
- [Architecture Decisions](./docs/ADR.md)
- [Code Quality Report](./docs/CODE_QUALITY_REPORT.md)
- [API Documentation](http://localhost:8000/docs)

## 🧪 Testing

```bash
# Frontend
pnpm test

# Backend
pytest
```

## 📊 Code Quality

- **Type Safety**: 95%+ TypeScript strict mode
- **Test Coverage**: TBD
- **Accessibility**: WCAG 2.1 AA compliant
- **Performance**: Optimized with React.memo, lazy loading
- **Security**: Session-based auth, input validation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT

## 👥 Team

Built with ❤️ by the IronRep team

## 🙏 Acknowledgments

- OpenAI for GPT models
- LangChain team
- React ecosystem
- FastAPI community
