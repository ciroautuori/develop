#!/bin/bash
set -x
LOGfile="/tmp/certbot_debug.log"
echo "Starting Certbot Debug at $(date)" > "$LOGfile"
whoami >> "$LOGfile"
pwd >> "$LOGfile"

docker compose -f services/docker-compose.gateway.yml run --rm --entrypoint certbot certbot-gateway certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email autcir@gmail.com \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  -d markettina.com \
  -d www.markettina.com \
  -d ironrep.it \
  -d www.ironrep.it \
  -d studiocentos.it \
  -d www.studiocentos.it \
  -d innovazionesocialesalernitana.it \
  -d www.innovazionesocialesalernitana.it \
  >> "$LOGfile" 2>&1

RET=$?
echo "Certbot Debug Finished with exit code $RET" >> "$LOGfile"
exit $RET
