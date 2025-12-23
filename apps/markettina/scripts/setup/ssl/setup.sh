#!/bin/bash
# ============================================================================
# Setup Nginx + SSL PRODUZIONE - markettina.it
# Dominio definitivo: markettina.it
# ============================================================================

set -e

echo "🚀 SETUP SSL PRODUZIONE - markettina.IT"
echo "=========================================="

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Domini
MAIN_DOMAIN="markettina.it"
WWW_DOMAIN="www.markettina.it"

# Email per Let's Encrypt
EMAIL="admin@markettina.it"

echo -e "${YELLOW}📋 Dominio produzione:${NC}"
echo "  - $MAIN_DOMAIN"
echo "  - $WWW_DOMAIN (redirect a $MAIN_DOMAIN)"
echo ""

# ============================================================================
# 1. Verifica prerequisiti
# ============================================================================
echo -e "${GREEN}[1/7] Verifica prerequisiti...${NC}"

# Verifica DNS
echo "🔍 Verifica DNS per $MAIN_DOMAIN..."
if ! host $MAIN_DOMAIN &> /dev/null; then
    echo -e "${RED}❌ ERRORE: $MAIN_DOMAIN non risolve!${NC}"
    echo "Assicurati che il DNS punti all'IP del server"
    exit 1
fi

echo "✅ DNS configurato correttamente"

# Verifica porte aperte
echo "🔍 Verifica porte 80 e 443..."
if ! sudo ss -tlnp | grep -q ':80 '; then
    echo -e "${YELLOW}⚠️  Porta 80 non in ascolto (verrà configurata da Nginx)${NC}"
fi

# ============================================================================
# 2. Installa Nginx e Certbot
# ============================================================================
echo -e "${GREEN}[2/7] Installazione Nginx e Certbot...${NC}"

if ! command -v nginx &> /dev/null; then
    echo "📦 Installazione Nginx..."
    sudo pacman -S --noconfirm nginx
else
    echo "✅ Nginx già installato"
fi

if ! command -v certbot &> /dev/null; then
    echo "📦 Installazione Certbot..."
    sudo pacman -S --noconfirm certbot certbot-nginx
else
    echo "✅ Certbot già installato"
fi

# ============================================================================
# 3. Crea directory per configurazioni
# ============================================================================
echo -e "${GREEN}[3/7] Creazione directory...${NC}"

sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled
sudo mkdir -p /etc/nginx/ssl
sudo mkdir -p /var/www/certbot
sudo mkdir -p /var/log/nginx

# ============================================================================
# 4. Configurazione Nginx principale
# ============================================================================
echo -e "${GREEN}[4/7] Configurazione Nginx principale...${NC}"

sudo tee /etc/nginx/nginx.conf > /dev/null <<'EOF'
user http;
worker_processes auto;
worker_cpu_affinity auto;

error_log /var/log/nginx/error.log warn;
pid /run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json
               image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=ai_limit:10m rate=50r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=200r/s;

    # Include site configs
    include /etc/nginx/sites-enabled/*;
}
EOF

# ============================================================================
# 5. Configurazione sito HTTP temporaneo (per certbot)
# ============================================================================
echo -e "${GREEN}[5/7] Configurazione HTTP temporanea...${NC}"

sudo tee /etc/nginx/sites-available/markettina.conf > /dev/null <<EOF
# HTTP - Temporaneo per certbot challenge
server {
    listen 80;
    server_name $MAIN_DOMAIN $WWW_DOMAIN;

    # Certbot challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Temporaneo: proxy ai servizi (prima di SSL)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /ai/ {
        rewrite ^/ai/(.*)$ /api/v1/\$1 break;
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Abilita sito
sudo ln -sf /etc/nginx/sites-available/markettina.conf /etc/nginx/sites-enabled/

# ============================================================================
# 6. Test e avvio Nginx
# ============================================================================
echo -e "${GREEN}[6/7] Test configurazione Nginx...${NC}"

sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configurazione Nginx valida"
    
    # Avvia/riavvia Nginx
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    echo "✅ Nginx avviato"
else
    echo -e "${RED}❌ Errore nella configurazione Nginx${NC}"
    exit 1
fi

# ============================================================================
# 7. Ottieni certificati SSL
# ============================================================================
echo -e "${GREEN}[7/7] Ottenimento certificati SSL...${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "  1. Il dominio $MAIN_DOMAIN deve puntare all'IP pubblico di questo server"
echo "  2. Le porte 80 e 443 devono essere aperte nel firewall"
echo "  3. I servizi backend (8002), ai (8001) e frontend (3000) devono essere attivi"
echo ""
read -p "Procedere con l'ottenimento dei certificati SSL? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Ottenimento certificati SSL per $MAIN_DOMAIN..."
    
    # Certificato per dominio principale + www
    sudo certbot --nginx \
        -d $MAIN_DOMAIN \
        -d $WWW_DOMAIN \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --redirect
    
    if [ $? -eq 0 ]; then
        echo "✅ Certificati SSL installati con successo!"
        
        # Auto-renewal
        sudo systemctl enable certbot-renew.timer
        sudo systemctl start certbot-renew.timer
        
        echo "✅ Auto-renewal configurato"
        
        # Copia configurazione SSL completa
        echo "📝 Aggiornamento configurazione Nginx con SSL..."
        sudo cp /home/autcir_gmail_com/markettina_ws/config/services/nginx/markettina-production.conf \
                /etc/nginx/sites-available/markettina.conf
        
        # Reload Nginx
        sudo nginx -t && sudo systemctl reload nginx
        
        echo "✅ Configurazione SSL completa attivata"
    else
        echo -e "${RED}❌ Errore nell'ottenimento dei certificati SSL${NC}"
        echo "Verifica che:"
        echo "  - Il DNS sia configurato correttamente"
        echo "  - Le porte 80 e 443 siano aperte"
        echo "  - Non ci siano altri servizi in ascolto su porta 80/443"
        exit 1
    fi
else
    echo "⏭️  Certificati SSL saltati"
    echo "Esegui manualmente: sudo certbot --nginx -d $MAIN_DOMAIN -d $WWW_DOMAIN"
fi

# ============================================================================
# 8. Configurazione Firewall
# ============================================================================
echo ""
echo -e "${GREEN}Configurazione Firewall...${NC}"

if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    echo "✅ Firewall configurato (ufw)"
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
    echo "✅ Firewall configurato (firewalld)"
else
    echo "⚠️  Configura manualmente il firewall per aprire porte 80 e 443"
fi

# ============================================================================
# RIEPILOGO
# ============================================================================
echo ""
echo -e "${GREEN}✅ SETUP SSL PRODUZIONE COMPLETATO!${NC}"
echo "===================================="
echo ""
echo "📊 Status servizi:"
echo "  - Nginx: $(systemctl is-active nginx)"
echo "  - Certbot renewal: $(systemctl is-active certbot-renew.timer)"
echo ""
echo "🌐 Dominio configurato:"
echo -e "  - ${BLUE}https://$MAIN_DOMAIN${NC} (Frontend + Backend + AI)"
echo -e "  - ${BLUE}https://$WWW_DOMAIN${NC} (redirect a $MAIN_DOMAIN)"
echo ""
echo "🔗 Endpoints:"
echo "  - Frontend: https://$MAIN_DOMAIN/"
echo "  - Backend API: https://$MAIN_DOMAIN/api/"
echo "  - AI Service: https://$MAIN_DOMAIN/ai/"
echo ""
echo "📝 Comandi utili:"
echo "  - Reload Nginx: sudo systemctl reload nginx"
echo "  - Test config: sudo nginx -t"
echo "  - Rinnova SSL: sudo certbot renew --dry-run"
echo "  - Logs Nginx: sudo tail -f /var/log/nginx/access.log"
echo "  - Logs SSL: sudo certbot certificates"
echo "  - Status SSL: sudo certbot certificates"
echo ""
echo "🔧 File configurazione:"
echo "  - /etc/nginx/nginx.conf"
echo "  - /etc/nginx/sites-available/markettina.conf"
echo "  - /etc/letsencrypt/live/$MAIN_DOMAIN/"
echo ""
echo "🚀 Prossimi passi:"
echo "  1. Avvia i servizi con: ./scripts/start_production.sh"
echo "  2. Verifica: https://$MAIN_DOMAIN"
echo "  3. Monitora logs: sudo tail -f /var/log/nginx/access.log"
echo ""
