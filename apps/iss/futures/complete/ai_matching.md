# ✅ Feature: AI Matching & Score Persistence

## Status
- **Status**: Completed
- **Completion Date**: 2025-12-24
- **Priority**: High

## Description
Integrated AI analysis to calculate a compatibility score (0-100) between a tender (bando) and the association's profile. Results are persisted in the database to allow "Perfect Match" results to be returned instantly (<1s), avoiding real-time LLM overhead for the end user.

## Implementation Details
- **Database**: Added `ai_score` and `ai_reasoning` to the `bandi` table.
- **Service**: `match_service.py` prioritizes cached scores and triggers background backfilling.
- **Models**: Updated Pydantic schemas and SQLAlchemy models.
- **Automation**: Daily monitoring tasks automatically pre-calculate scores for new opportunities.

## Benefits
- Instant UI response times.
- Reduced API costs/load.
- Clear justification for every recommended tender.
