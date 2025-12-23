# 🔐 Secrets Management Rules

## ❌ NEVER COMMIT SECRETS

- API keys
- Database passwords
- JWT secrets
- OAuth tokens
- HuggingFace tokens

## ✅ CORRECT APPROACH

### In Code
```python
# ❌ WRONG
API_KEY = "sk-abc123..."

# ✅ CORRECT
API_KEY = os.getenv("API_KEY", "")
```

### In Docker Compose
```yaml
# ❌ WRONG
environment:
  - API_KEY=sk-abc123...

# ✅ CORRECT
environment:
  - API_KEY=${API_KEY}
env_file:
  - .env.prod  # NOT committed
```

### .env Files
```bash
# .env.example (committed - placeholder values)
API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@host:5432/db

# .env.prod (NOT committed - real values)
API_KEY=sk-abc123...
DATABASE_URL=postgresql://admin:real_password@central-postgres:5432/db
```

## .gitignore Rules (Already Configured)

```gitignore
*.env
.env.*
!.env.example
**/*.pem
**/*.key
**/secrets/
```

## Files with Known Secrets (Excluded)

- `apps/studiocentos/apps/ai_microservice/.env`
- `apps/*/config/docker/.env.prod`
- Any file with HuggingFace token `hf_*`
- Any file with Groq key `gsk_*`
- Any file with OpenAI key `sk-*`

## GitHub Push Protection

GitHub blocks pushes with detected secrets. If push fails:
1. Check error message for file path
2. Replace secret with `os.getenv()`
3. Reset commit: `git reset HEAD~1 --soft`
4. Re-commit without secrets
5. Push again

*Ultimo aggiornamento: 2025-12-23*
