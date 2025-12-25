# 🚧 Feature: Agent Analyst (Deep Analysis)

## Status
- **Status**: In Progress
- **Priority**: High

## Description
A specialized AI agent that performs deep, multi-step evaluations of tenders. It goes beyond the basic score by performing SWOT analysis, checking legal requirements against the Personal RAG, and proposing a specific approach strategy.

## Planned Features
- **Multi-step Reasoning**: Keyword extraction -> RAG Query -> SWOT Analysis -> Strategy Generation.
- **Persistent Reports**: Storing deep analysis JSON in the `Bando` record.
- **Document Checklist**: Automatic identification of required documents based on internal guides.

## Technical Tasks
- [x] Backend Service (`analyst_service.py`).
- [x] API Integration (`/analyze` endpoint).
- [ ] Frontend UI for detailed reports.
- [ ] Optimization of reasoning loops.
