# SSR Server - Express.js + React

This is the Server-Side Rendering (SSR) server for the Psychology Institute project. It handles public pages with SEO optimization while the React SPA handles authenticated/admin pages.

## Architecture

- **Express.js** - SSR server
- **React 18** - UI library with SSR support
- **React Router 6** - Routing (StaticRouter for SSR)
- **Webpack 5** - Bundling for server and client
- **Django REST API** - Backend data source

## Features

- ✅ Server-Side Rendering for public pages
- ✅ SEO optimization (meta tags, structured data, OG tags)
- ✅ Dynamic sitemap generation
- ✅ Page-level caching with Redis
- ✅ Responsive design with Bootstrap 5
- ✅ Persian/RTL support
- ✅ Docker containerization

## Pages with SSR

- `/` - Home page
- `/blog` - Blog listing
- `/blog/post/:slug` - Blog post detail
- `/blog/category/:slug` - Category archive
- `/blog/tag/:slug` - Tag archive
- `/workshops` - Workshops listing
- `/workshops/:slug` - Workshop detail
- `/courses` - Courses listing
- `/courses/course/:slug` - Course detail
- `/packages` - Packages listing
- `/packages/:slug` - Package detail
- `/therapists` - Therapists listing
- `/therapists/:id` - Therapist detail
- `/about/founder` - About founder
- `/about/institute` - About institute

## Development

### Prerequisites

- Node.js 18+
- npm or yarn
- Django backend running on port 8000

### Setup

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update environment variables in `.env`:
```env
PORT=3001
NODE_ENV=development
DJANGO_API_URL=http://localhost:8000/api
SITE_URL=http://localhost:3001
SITE_NAME="مرکز مشاوره و خدمات روانشناسی سرمد"
SITE_DESCRIPTION="مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای"
REDIS_URL=redis://localhost:6379/2
REDIS_ENABLED=false
```

### Development Commands

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up ssr-server

# Or build individually
docker build -t ssr-server .
docker run -p 3001:3001 ssr-server
```

## Production Deployment

### Environment Variables

```env
NODE_ENV=production
PORT=3001
DJANGO_API_URL=http://django:8000/api
SITE_URL=https://yourdomain.com
SITE_NAME="مرکز مشاوره و خدمات روانشناسی سرمد"
SITE_DESCRIPTION="مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای"
REDIS_URL=redis://redis:6379/2
REDIS_ENABLED=true
CACHE_TTL=3600
PAGE_CACHE_TTL=1800
```

### Docker Production

```bash
# Build production image
docker build -t ssr-server:production .

# Run with environment variables
docker run -d \
  --name ssr-server \
  -p 3001:3001 \
  -e NODE_ENV=production \
  -e DJANGO_API_URL=http://django:8000/api \
  -e SITE_URL=https://yourdomain.com \
  ssr-server:production
```

## API Integration

The SSR server fetches data from Django REST API endpoints:

- `/api/blog/posts/` - Blog posts
- `/api/blog/categories/` - Blog categories
- `/api/blog/tags/` - Blog tags
- `/api/workshops/` - Workshops
- `/api/courses/` - Courses
- `/api/packages/` - Packages
- `/api/dashboard/therapists/` - Therapists

## SEO Features

- Dynamic meta tags (title, description, OG tags, Twitter cards)
- JSON-LD structured data for articles
- Canonical URLs
- Breadcrumb navigation
- Dynamic sitemap generation
- Robots.txt generation

## Caching

- Page-level caching with Redis (optional)
- API response caching
- Static asset caching
- Cache invalidation strategies

## Performance

- Webpack optimization for production builds
- Code splitting for client bundle
- CSS extraction and optimization
- Image optimization
- Gzip compression

## Monitoring

- Health check endpoint: `/health`
- Error handling and logging
- Performance monitoring
- Cache statistics

## Troubleshooting

### Common Issues

1. **Build errors**: Check Node.js version (18+ required)
2. **API connection errors**: Verify Django backend is running
3. **Cache issues**: Check Redis connection
4. **Memory issues**: Increase Docker memory limits

### Logs

```bash
# View logs
docker logs psychology_ssr_dev

# Follow logs
docker logs -f psychology_ssr_dev
```

## Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include SEO optimization for new pages
4. Test with Docker environment
5. Update documentation

## License

This project is part of the Psychology Institute system.
