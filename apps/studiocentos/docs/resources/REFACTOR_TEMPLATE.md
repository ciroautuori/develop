# 🔧 REFACTORING CHECKLIST - TEMPLATE

> ⚠️ **IMPORTANTE: QUESTO È UN TEMPLATE DI ESEMPIO**
> 
> **NON USARE DIRETTAMENTE QUESTO FILE!**
> 
> Questo è un template di riferimento. Per usarlo:
> 1. Copia questo file con un nuovo nome (es. `REFACTOR_AUTH_MODULE.md`)
> 2. Compila con i dettagli del tuo refactoring
> 3. Traccia il progresso delle modifiche
> 4. NON modificare questo template originale

---
title: "REFACTORING CHECKLIST - Template"
tags: [refactor, checklist, template]
owner: "[Team]"
status: DRAFT
version: 1.0.0
---

<!-- Embedded standard header (vanilla) -->
owner: "[Team]"
status: DRAFT
version: 1.0.0
last_updated: "YYYY-MM-DD"

| Priority | Total | Done | Progress | Status |
|----------|------:|-----:|---------:|--------|
| 🚨 **CRITICAL** | 0 | 0 | 0% | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ |
| ⚠️ **HIGH** | 0 | 0 | 0% | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ |
| 🟡 **MEDIUM** | 0 | 0 | 0% | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ |
| 🟢 **LOW** | 0 | 0 | 0% | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ |
| **TOTAL** | **0** | **0** | **0%** | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ |

Nota: aggiorna la tabella per questo documento.

## Purpose
Checklist professionale per pianificare, eseguire e validare refactor di produzione con rischio controllato.

## Pre-Refactor (Preparation)
- [ ] Create branch `feature/refactor-<name>` and push current state
- [ ] Backup DB (if applicable)
- [ ] Baseline test coverage and performance metrics
- [ ] Stakeholder communication & schedule

## Analysis
- [ ] Codebase scanning (LOC, modules)
- [ ] Duplication scan (jscpd or similar)
- [ ] Dependency & circular import analysis
- [ ] Architecture assessment & ADR if needed

## Planning
- [ ] Choose migration strategy (Big Bang / Incremental / Strangler)
- [ ] Define domain boundaries and directory structure
- [ ] Testing strategy (unit/integration/e2e)
- [ ] Rollback & contingency plan

## Execution (recommended incremental steps)
- [ ] Create new structure and move non-critical modules first
- [ ] Update imports and run full test suite after each domain
- [ ] Remove duplicated code by extracting shared modules
- [ ] Keep PRs small and well-documented

## Validation
- [ ] Type check (npx tsc --noEmit)
- [ ] Linting passes
- [ ] Unit & integration tests pass
- [ ] E2E tests and smoke tests in staging
- [ ] Performance benchmarks within target

## Documentation
- [ ] Update README, ADRs, migration guides
- [ ] Release notes and changelog

## Post-deploy
- [ ] Monitor errors and performance for 24-72h
- [ ] Run retrospective and capture lessons learned

## Usage
- Use this checklist as template in refactor planning and attach relevant tickets for each item.

