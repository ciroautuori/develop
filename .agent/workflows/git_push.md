---
description: How to push changes to app repos
---

# 📤 Git Push Workflow

## Overview
The `develop` monorepo contains all apps. Each app can be pushed to its own repo using git subtree.

---

## Quick Commands

```bash
cd /home/autcir_gmail_com/develop

# Push single app with message
make push-iss MSG="Fix login bug"
make push-studiocentos MSG="Add booking feature"
make push-markettina MSG="Update homepage"
make push-ironrep MSG="API refactor"

# Push develop repo
make push-develop MSG="Infrastructure update"

# Push ALL repos at once
make push-all MSG="Release v2.0"
```

---

## Git Remotes Configured

| Remote | Repository |
|--------|------------|
| `origin` | github.com/ciroautuori/develop.git |
| `iss-repo` | github.com/ciroautuori/iss_ws.git |
| `studiocentos-repo` | github.com/ciroautuori/studiocentos_ws.git |
| `markettina-repo` | github.com/ciroautuori/markettina.git |
| `ironrep-repo` | github.com/ciroautuori/ironrep.git |

---

## Manual Commands (without Make)

```bash
# Commit first
git add . && git commit -m "Your message"

# Push to develop
git push origin main

# Push app subtree
git push iss-repo $(git subtree split --prefix=apps/iss):main --force
git push studiocentos-repo $(git subtree split --prefix=apps/studiocentos):main --force
git push markettina-repo $(git subtree split --prefix=apps/markettina):main --force
git push ironrep-repo $(git subtree split --prefix=apps/ironRep):main --force
```

---

## Notes
- Each `make push-*` command automatically commits pending changes
- Without `MSG=`, uses timestamp as commit message
- Subtree push uses `--force` to sync from monorepo → app repo
