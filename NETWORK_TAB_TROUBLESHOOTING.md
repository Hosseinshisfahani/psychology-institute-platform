# Network Tab Not Showing Requests - Troubleshooting Guide

## Issue
Your site is working properly, but the browser's Network tab is not showing any requests (GET, POST, etc.).

## Common Causes & Solutions

### 1. **Network Tab Filters** (Most Common)
The Network tab might have filters applied that hide requests:

**Solution:**
- Open DevTools (F12)
- Go to Network tab
- Check the filter buttons at the top:
  - Click "All" to show all requests
  - Uncheck any active filters (XHR, Fetch, JS, CSS, etc.)
  - Clear any text in the filter box

### 2. **Preserve Log Disabled**
If "Preserve log" is off, navigation clears the network log:

**Solution:**
- In Network tab, check the "Preserve log" checkbox (top left)
- This keeps requests visible even after page navigation

### 3. **Disable Cache**
If "Disable cache" is enabled, cached requests might not show:

**Solution:**
- In Network tab, check/uncheck "Disable cache" as needed
- Try both settings to see if requests appear

### 4. **Browser Extensions**
Ad blockers or privacy extensions might hide network requests:

**Solution:**
- Disable browser extensions temporarily
- Try incognito/private mode (extensions usually disabled)
- Check if requests appear

### 5. **Service Worker**
Service workers can intercept requests and hide them from Network tab:

**Solution:**
- Open DevTools → Application tab
- Check "Service Workers" section
- If any are registered, click "Unregister"
- Refresh the page

### 6. **Hardcoded localhost URLs**
Check if any code has hardcoded localhost addresses:

**Current Configuration:**
- ✅ Frontend `.env`: `REACT_APP_API_URL=http://185.8.175.241:8000`
- ✅ Axios baseURL: `http://185.8.175.241:8000`
- ✅ All API calls use relative URLs with baseURL

### 7. **CORS Issues**
If requests are blocked by CORS, they might not show in Network tab:

**Check:**
- Open Console tab (not Network)
- Look for CORS errors
- Check if requests are being blocked

### 8. **Browser Cache**
Cached responses might not appear in Network tab:

**Solution:**
- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Clear browser cache
- Check "Disable cache" in Network tab

## Quick Diagnostic Steps

1. **Open DevTools Console** (F12 → Console tab)
   - Look for any errors
   - Check if axios requests are logged

2. **Check Network Tab Settings:**
   ```
   - Click "All" filter
   - Enable "Preserve log"
   - Check "Disable cache" (try both on/off)
   ```

3. **Test with a Simple Request:**
   Open browser console and run:
   ```javascript
   fetch('http://185.8.175.241:8000/api/workshops/')
     .then(r => r.json())
     .then(d => console.log('Response:', d))
     .catch(e => console.error('Error:', e));
   ```
   This should appear in Network tab.

4. **Check Request Headers:**
   - In Network tab, click on a request (if visible)
   - Check "Request URL" - should be `http://185.8.175.241:8000/api/...`
   - Not `localhost` or `127.0.0.1`

## Verification

Your current setup:
- ✅ Frontend: Port 3000 (served by `serve`)
- ✅ Backend: Port 8000 (Django)
- ✅ API Base URL: `http://185.8.175.241:8000`
- ✅ All requests use full URLs (not localhost)

## If Still Not Working

1. **Check Browser Console** for errors
2. **Try Different Browser** (Chrome, Firefox, Edge)
3. **Check Server Logs** - requests should appear in Django logs
4. **Use Browser Extension** like "Requestly" to monitor requests

## Expected Behavior

When working correctly:
- Network tab should show requests to `http://185.8.175.241:8000/api/...`
- Requests should have status codes (200, 404, etc.)
- You can click on requests to see headers, response, etc.
