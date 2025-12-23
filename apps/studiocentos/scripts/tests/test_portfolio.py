#!/usr/bin/env python3
"""Test portfolio endpoint"""
import asyncio
import sys
sys.path.insert(0, '/home/autcir_gmail_com/studiocentos/apps/backend')

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.domain.portfolio.models import Project, Service
from app.domain.portfolio.schemas import ProjectResponse, ServiceResponse, PortfolioPublicResponse

DATABASE_URL = "postgresql+asyncpg://studiocentos:studiocentos2025@localhost:5433/studiocentos"

async def test():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Get projects
        projects_query = select(Project).where(
            Project.is_public == True,
            Project.status == "active"
        ).order_by(Project.order, Project.created_at.desc())
        
        projects_result = await db.execute(projects_query)
        projects = projects_result.scalars().all()
        
        print(f"Found {len(projects)} projects")
        for p in projects:
            print(f"  - {p.title}")
            try:
                pr = ProjectResponse.model_validate(p)
                print(f"    ✅ Validated")
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        # Get services
        services_query = select(Service).where(
            Service.is_active == True
        ).order_by(Service.order, Service.created_at.desc())
        
        services_result = await db.execute(services_query)
        services = services_result.scalars().all()
        
        print(f"\nFound {len(services)} services")
        for s in services:
            print(f"  - {s.title}")
            try:
                sr = ServiceResponse.model_validate(s)
                print(f"    ✅ Validated")
            except Exception as e:
                print(f"    ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
