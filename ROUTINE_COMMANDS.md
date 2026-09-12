# Routine Commands — sarmadclinic.ir

Current architecture (since Sep 12, 2026):
- Nginx (:443) serves the React build from /var/www/psychology/frontend
  and proxies /api/ and /admin/ to Django on 127.0.0.1:8000
- Django backend runs via systemd service `psychology-backend.service`
  (uses the psychology-backend:py312 Docker image as its Python 3.12 runtime,
   project code is mounted from /root/psychology-institute-platform)
- PostgreSQL 18 on localhost:5432, database: psychology_institute
- Config file: /root/psychology-institute-platform/dependencies/.env

==========================================
1) DEPLOY FRONTEND (after changing frontend code)
==========================================

cd /root/psychology-institute-platform

# Build (uses node:20-alpine image, ~1-3 minutes)
docker run --rm -v "$PWD/frontend:/app" -w /app \
  -e GENERATE_SOURCEMAP=false \
  -e REACT_APP_API_URL=https://sarmadclinic.ir \
  -e NODE_OPTIONS="--max-old-space-size=1024" \
  node:20-alpine npx --no-install react-scripts build

# Copy build to the folder nginx serves
cp -r frontend/build/* /var/www/psychology/frontend/

# No restart needed — new files are served immediately.
# In the browser use Ctrl+Shift+R (hard refresh) to bypass cache.

==========================================
2) DEPLOY BACKEND (after changing backend code)
==========================================

# Code is mounted into the container, so just restart:
systemctl restart psychology-backend.service

# The service runs "manage.py migrate" automatically on every start.

# Verify:
sleep 8
curl -I http://127.0.0.1:8000/admin/     # expect HTTP 301

==========================================
3) CHECK STATUS / LOGS
==========================================

# Services
systemctl status psychology-backend.service
systemctl is-active psychology-backend nginx postgresql

# Backend logs (live)
journalctl -u psychology-backend -f

# Backend logs (last 50 lines)
journalctl -u psychology-backend -n 50 --no-pager

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Is port 8000 listening?
ss -ltn | grep 8000

# Site health from the server
curl -I https://sarmadclinic.ir
curl -I https://sarmadclinic.ir/api/

==========================================
4) NGINX
==========================================

# Config file:
#   /etc/nginx/sites-available/psychology.conf

# Test config, then reload (reload = no downtime)
nginx -t && systemctl reload nginx

# Full restart (rarely needed)
systemctl restart nginx

==========================================
5) DATABASE
==========================================

# Backup (JSON dump via Django)
cd /root/psychology-institute-platform
docker run --rm --network host \
  -v /root/psychology-institute-platform:/app -w /app \
  psychology-backend:py312 \
  python dependencies/manage.py dumpdata \
    --exclude contenttypes --exclude auth.permission \
    --indent 2 > dependencies/db_backup_$(date +%Y%m%d).json

# Backup (raw SQL dump — faster, recommended)
sudo -u postgres pg_dump psychology_institute > /root/db_backup_$(date +%Y%m%d).sql

# Open a psql shell
sudo -u postgres psql -d psychology_institute

# Open a Django shell
docker run --rm -it --network host \
  -v /root/psychology-institute-platform:/app -w /app \
  psychology-backend:py312 \
  python dependencies/manage.py shell

# Create a superuser
docker run --rm -it --network host \
  -v /root/psychology-institute-platform:/app -w /app \
  psychology-backend:py312 \
  python dependencies/manage.py createsuperuser

==========================================
6) SSL CERTIFICATE (Let's Encrypt)
==========================================

# Check expiry
certbot certificates

# Renew (auto-renewal is scheduled, this is manual)
certbot renew

# Test renewal without changing anything
certbot renew --dry-run

==========================================
7) AFTER SERVER REBOOT
==========================================

# Everything starts automatically (enabled services).
# If something is down, check in this order:
systemctl status postgresql
systemctl status docker
systemctl status psychology-backend.service
systemctl status nginx

==========================================
8) TROUBLESHOOTING
==========================================

# Backend won't start → read the actual error:
journalctl -u psychology-backend -n 100 --no-pager | grep -E "Error|FATAL"

# "password authentication failed" → .env DB_PASSWORD must match postgres:
#   sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'PASSWORD_FROM_ENV';"

# Site shows old version → rebuild + copy (section 1), then hard refresh browser.

# Site shows "Welcome to nginx" → root directive missing or files not copied
#   to /var/www/psychology/frontend/ (section 1, copy step).

# Frontend build killed (out of memory) → check swap:
free -h
swapon --show
