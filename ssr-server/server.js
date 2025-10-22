const express = require('express');
const path = require('path');
const compression = require('compression');
const helmet = require('helmet');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet({
  contentSecurityPolicy: false, // Disable CSP for development
  crossOriginEmbedderPolicy: false
}));

// CORS configuration
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://yourdomain.com'] 
    : ['http://localhost:3000', 'http://localhost:3001'],
  credentials: true
}));

// Compression middleware
app.use(compression());

// Static files
app.use('/static', express.static(path.join(__dirname, 'dist/public')));

// Import server bundle (will be available after build)
let renderApp;
try {
  renderApp = require('./dist/server.js').default;
} catch (error) {
  console.error('Server bundle not found. Please run "npm run build" first.');
  process.exit(1);
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'ssr-server',
    timestamp: new Date().toISOString()
  });
});

// Sitemap endpoint
app.get('/sitemap.xml', async (req, res) => {
  try {
    const { generateSitemap } = require('./dist/server.js');
    const sitemap = await generateSitemap();
    res.set('Content-Type', 'application/xml');
    res.send(sitemap);
  } catch (error) {
    console.error('Error generating sitemap:', error);
    res.status(500).send('Error generating sitemap');
  }
});

// Robots.txt endpoint
app.get('/robots.txt', (req, res) => {
  try {
    const { generateRobotsTxt } = require('./dist/server.js');
    const robotsTxt = generateRobotsTxt();
    res.set('Content-Type', 'text/plain');
    res.send(robotsTxt);
  } catch (error) {
    console.error('Error generating robots.txt:', error);
    res.status(500).send('Error generating robots.txt');
  }
});

// API proxy endpoints (optional - for direct API access)
app.get('/api/*', (req, res) => {
  res.redirect(`${process.env.DJANGO_API_URL}${req.path}`);
});

// All other routes handled by React SSR
app.get('*', renderApp);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('SSR Error:', err);
  
  // Don't send error details in production
  const errorMessage = process.env.NODE_ENV === 'production' 
    ? 'Internal Server Error' 
    : err.message;
  
  res.status(500).send(`
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
      <meta charset="UTF-8">
      <title>خطا - ${process.env.SITE_NAME || 'مرکز مشاوره'}</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    </head>
    <body>
      <div class="container mt-5">
        <div class="alert alert-danger">
          <h4>خطا در بارگذاری صفحه</h4>
          <p>${errorMessage}</p>
          <a href="/" class="btn btn-primary">بازگشت به صفحه اصلی</a>
        </div>
      </div>
    </body>
    </html>
  `);
});

// Start server
app.listen(PORT, () => {
  console.log(`SSR Server running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`Django API: ${process.env.DJANGO_API_URL || 'http://localhost:8000/api'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});
