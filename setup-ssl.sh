#!/bin/bash

# SSL Certificate Setup Script for sarmadclinic.ir
# This script sets up Let's Encrypt SSL certificates using certbot

set -eu

DOMAIN="sarmadclinic.ir"
EMAIL="porseshgareisfahani@gmail.com"
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"
CERTBOT_WEBROOT="/var/www/certbot"

echo "=========================================="
echo "SSL Certificate Setup for $DOMAIN"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Create certbot webroot directory
echo "Creating certbot webroot directory..."
mkdir -p "$CERTBOT_WEBROOT"
chown -R www-data:www-data "$CERTBOT_WEBROOT"

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "Installing nginx..."
    apt-get update
    apt-get install -y nginx
fi

# Create temporary nginx config for certificate validation
TEMP_NGINX_CONF="$NGINX_CONF_DIR/sarmadclinic-temp"
cat > "$TEMP_NGINX_CONF" <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root $CERTBOT_WEBROOT;
    }

    location / {
        return 200 "Certificate validation in progress...";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable temporary config
ln -sf "$TEMP_NGINX_CONF" "$NGINX_ENABLED_DIR/sarmadclinic-temp"

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Reload nginx
echo "Reloading nginx..."
systemctl reload nginx

# Obtain SSL certificate
echo ""
echo "Obtaining SSL certificate from Let's Encrypt..."
echo "This will validate your domain ownership. Make sure:"
echo "1. Your domain $DOMAIN points to this server's IP address"
echo "2. Port 80 is open and accessible from the internet"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

certbot certonly \
    --webroot \
    --webroot-path="$CERTBOT_WEBROOT" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --domains "$DOMAIN" \
    --domains "www.$DOMAIN" \
    --non-interactive

# Check if certificate was obtained successfully
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo ""
    echo "✓ SSL certificate obtained successfully!"
    echo ""
    
    # Copy production nginx config
    if [ -f "/root/psychology-institute-platform/frontend/nginx-ssl.conf" ]; then
        echo "Setting up production nginx configuration..."
        cp /root/psychology-institute-platform/frontend/nginx-ssl.conf "$NGINX_CONF_DIR/sarmadclinic"
        
        # Remove temporary config
        rm -f "$NGINX_ENABLED_DIR/sarmadclinic-temp"
        rm -f "$TEMP_NGINX_CONF"
        
        # Enable production config
        ln -sf "$NGINX_CONF_DIR/sarmadclinic" "$NGINX_ENABLED_DIR/sarmadclinic"
        
        # Test nginx configuration
        echo "Testing nginx configuration..."
        nginx -t
        
        if [ $? -eq 0 ]; then
            echo "Reloading nginx with SSL configuration..."
            systemctl reload nginx
            echo ""
            echo "✓ SSL setup complete!"
            echo ""
            echo "Your site should now be accessible at:"
            echo "  https://$DOMAIN"
            echo "  https://www.$DOMAIN"
            echo ""
            echo "Certificate will auto-renew. To test renewal:"
            echo "  certbot renew --dry-run"
        else
            echo "✗ Nginx configuration test failed. Please check the configuration."
            exit 1
        fi
    else
        echo "⚠ Production nginx config not found. Please copy nginx-ssl.conf manually."
    fi
    
    # Set up auto-renewal
    echo ""
    echo "Setting up automatic certificate renewal..."
    systemctl enable certbot.timer
    systemctl start certbot.timer
    
    echo ""
    echo "Certificate renewal status:"
    systemctl status certbot.timer --no-pager -l
    
else
    echo ""
    echo "✗ Failed to obtain SSL certificate."
    echo "Please check:"
    echo "1. Domain DNS is pointing to this server"
    echo "2. Port 80 is accessible from the internet"
    echo "3. No firewall is blocking the connection"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="

