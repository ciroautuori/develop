# 📅 Feature: Multi-tenancy Support

## Status
- **Status**: Planned
- **Priority**: Critical

## Description
Allow multiple organizations (APS/ETS) to use the ISS platform while keeping their data (profiles, saved bandi, projects) strictly isolated.

## Implementation Plan
- **Database Schema**: Transition to standard multi-tenant schema (OrgID in all tables or schema-per-tenant).
- **Authentication**: Update JWT to include `OrgID`.
- **RAG Isolation**: Use ChromaDB collections or partitions with tenant-specific IDs.
- **Shared Resources**: Shared knowledge base for public documents, private knowledge for organization-specific docs.

## Benefits
- SaaS scalability.
- Data privacy and security.
- Centralized infrastructure management for multiple entities.
