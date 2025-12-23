---
description: How to setup SSL certificates
---

# SSL Setup Workflow

1. **Prerequisite**: Ensure all DNS records point to the server IP (`35.195.232.166`).
   - markettina.com
   - ironrep.it
   - studiocentos.it
   - innovazionesocialesalernitana.it
   (and their `www` subdomains)

2. **Issue Certificates**:
   Run the centralized Certbot command:
   ```bash
   docker compose -f services/docker-compose.gateway.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d markettina.com -d www.markettina.com -d ironrep.it -d www.ironrep.it -d studiocentos.it -d www.studiocentos.it -d innovazionesocialesalernitana.it -d www.innovazionesocialesalernitana.it
   ```

3. **Enable SSL in Nginx**:
   Edit `services/nginx/conf.d/*.conf` files to uncomment the SSL blocks (Listen 443, SSL paths).

4. **Reload Nginx**:
   ```bash
   docker compose -f services/docker-compose.gateway.yml restart nginx-gateway
   ```
