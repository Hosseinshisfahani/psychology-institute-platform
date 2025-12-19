


## SSL Certificate Renewal

Certificates are automatically renewed via systemd timer. To check status:

```bash
sudo systemctl status certbot.timer
```

To test renewal manually:
```bash
sudo certbot renew --dry-run
```

## Troubleshooting

### Certificate Not Obtained
- Verify DNS is pointing to your server: `dig sarmadclinic.ir`
- Check port 80 is open: `sudo ufw status` or `sudo iptables -L`
- Check nginx is running: `sudo systemctl status nginx`
- Check nginx logs: `sudo tail -f /var/log/nginx/error.log`

### Nginx Configuration Errors
- Test configuration: `sudo nginx -t`
- Check syntax: `sudo nginx -T`
- View logs: `sudo tail -f /var/log/nginx/error.log`

### Django Not Accessible
- Check Django is running: `ps aux | grep manage.py`
- Check Django logs
- Verify `ALLOWED_HOSTS` includes your domain
- Check CORS settings if frontend can't connect

## Email Configuration

Your email `porseshgareisfahani@gmail.com` is configured for:
- Let's Encrypt certificate notifications
- Certificate expiration warnings

The default FROM email is set to `noreply@sarmadclinic.ir` in settings.py.

## Security Notes

When `DEBUG=False` in production, the following security features are enabled:
- `SECURE_SSL_REDIRECT`: Forces HTTPS
- `SECURE_HSTS_SECONDS`: HTTP Strict Transport Security (1 year)
- `SESSION_COOKIE_SECURE`: Secure session cookies
- `CSRF_COOKIE_SECURE`: Secure CSRF cookies

Make sure to set `DEBUG=False` in your production environment!

## Files Modified

- `frontend/nginx.conf` - Updated server_name
- `frontend/nginx-ssl.conf` - New SSL-enabled configuration
- `psychology_institute/settings.py` - Updated domain settings
- `setup-ssl.sh` - New SSL setup script

## Support

If you encounter issues:
1. Check nginx error logs: `/var/log/nginx/error.log`
2. Check Django logs
3. Verify DNS propagation: `dig sarmadclinic.ir`
4. Test SSL: `openssl s_client -connect sarmadclinic.ir:443`

