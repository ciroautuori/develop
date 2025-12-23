---
description: How to setup SSL certificates
---

# 🔒 SSL Setup Workflow

## Prerequisites
- DNS records pointing to `35.195.232.166`:
  - markettina.com, www.markettina.com
  - ironrep.it, www.ironrep.it
  - studiocentos.it, www.studiocentos.it
  - innovazionesocialesalernitana.it, www.innovazionesocialesalernitana.it

---

## Step 1: Issue Certificates

```bash
cd /home/autcir_gmail_com/develop

docker compose -f services/docker-compose.gateway.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  -d markettina.com -d www.markettina.com \
  -d ironrep.it -d www.ironrep.it \
  -d studiocentos.it -d www.studiocentos.it \
  -d innovazionesocialesalernitana.it -d www.innovazionesocialesalernitana.it
```

---

## Step 2: Verify Certificates

```bash
ls -la services/data/letsencrypt/live/
```

Each domain should have:
- `fullchain.pem`
- `privkey.pem`

---

## Step 3: Enable SSL in Nginx

Nginx configs in `services/nginx/conf.d/` already have SSL blocks.
Certificates are mounted at `/etc/letsencrypt/`.

---

## Step 4: Reload Nginx

```bash
docker compose -f services/docker-compose.gateway.yml restart nginx-gateway
```

---

## Step 5: Test HTTPS

```bash
curl -I https://markettina.com
curl -I https://ironrep.it
curl -I https://studiocentos.it
curl -I https://innovazionesocialesalernitana.it
```

---

## Auto-Renewal (Cron)

Add to crontab:
```bash
0 3 * * * docker compose -f /home/autcir_gmail_com/develop/services/docker-compose.gateway.yml run --rm certbot renew
```
