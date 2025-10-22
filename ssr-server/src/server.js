import React from 'react';
import { renderToString } from 'react-dom/server';
import { StaticRouter } from 'react-router-dom/server';
import { HelmetProvider } from 'react-helmet-async';
import App from './App';
import { generateMetaTags, generateArticleStructuredData, generateBreadcrumbStructuredData, generateBreadcrumbs } from './lib/seo';
import { cacheUtils, pageCacheUtils, generatePageCacheKey } from './lib/cache';
import { blogApi, workshopsApi, coursesApi, packagesApi, therapistsApi } from './lib/api';
import fs from 'fs';
import path from 'path';

// Read HTML template
const templatePath = path.join(process.cwd(), 'public', 'index.html');
const template = fs.readFileSync(templatePath, 'utf8');

/**
 * Fetch data for specific routes
 */
const fetchRouteData = async (path, query = {}) => {
  try {
    const pathSegments = path.split('/').filter(segment => segment);
    
    // Blog routes
    if (pathSegments.includes('blog')) {
      if (pathSegments.includes('post') && pathSegments[pathSegments.indexOf('post') + 1]) {
        const slug = pathSegments[pathSegments.indexOf('post') + 1];
        const post = await blogApi.getPost(slug);
        return { post };
      } else if (pathSegments.includes('category') && pathSegments[pathSegments.indexOf('category') + 1]) {
        const slug = pathSegments[pathSegments.indexOf('category') + 1];
        const [posts, categories] = await Promise.all([
          blogApi.getPostsByCategory(slug),
          blogApi.getCategories()
        ]);
        return { posts: posts.results, categories, category: { slug, name: slug } };
      } else if (pathSegments.includes('tag') && pathSegments[pathSegments.indexOf('tag') + 1]) {
        const slug = pathSegments[pathSegments.indexOf('tag') + 1];
        const [posts, tags] = await Promise.all([
          blogApi.getPostsByTag(slug),
          blogApi.getTags()
        ]);
        return { posts: posts.results, tags, tag: { slug, name: slug } };
      } else if (pathSegments.includes('search')) {
        const searchQuery = query.q || '';
        const [posts, categories] = await Promise.all([
          blogApi.searchPosts(searchQuery),
          blogApi.getCategories()
        ]);
        return { posts: posts.results, categories, searchQuery };
      } else {
        // Blog listing
        const [posts, categories] = await Promise.all([
          blogApi.getPosts(query),
          blogApi.getCategories()
        ]);
        return { posts: posts.results, categories };
      }
    }
    
    // Workshop routes
    if (pathSegments.includes('workshops')) {
      if (pathSegments[pathSegments.indexOf('workshops') + 1] && !pathSegments.includes('workshops', pathSegments.indexOf('workshops') + 1)) {
        const slug = pathSegments[pathSegments.indexOf('workshops') + 1];
        const workshop = await workshopsApi.getWorkshop(slug);
        return { workshop };
      } else {
        const workshops = await workshopsApi.getWorkshops(query);
        return { workshops: workshops.results };
      }
    }
    
    // Course routes
    if (pathSegments.includes('courses')) {
      if (pathSegments.includes('course') && pathSegments[pathSegments.indexOf('course') + 1]) {
        const slug = pathSegments[pathSegments.indexOf('course') + 1];
        const course = await coursesApi.getCourse(slug);
        return { course };
      } else {
        const courses = await coursesApi.getCourses(query);
        return { courses: courses.results };
      }
    }
    
    // Package routes
    if (pathSegments.includes('packages')) {
      if (pathSegments[pathSegments.indexOf('packages') + 1] && !pathSegments.includes('packages', pathSegments.indexOf('packages') + 1)) {
        const slug = pathSegments[pathSegments.indexOf('packages') + 1];
        const packageItem = await packagesApi.getPackage(slug);
        return { package: packageItem };
      } else {
        const packages = await packagesApi.getPackages(query);
        return { packages: packages.results };
      }
    }
    
    // Therapist routes
    if (pathSegments.includes('therapists')) {
      if (pathSegments[pathSegments.indexOf('therapists') + 1] && !pathSegments.includes('therapists', pathSegments.indexOf('therapists') + 1)) {
        const id = pathSegments[pathSegments.indexOf('therapists') + 1];
        const therapist = await therapistsApi.getTherapist(id);
        return { therapist };
      } else {
        const therapists = await therapistsApi.getTherapists(query);
        return { therapists: therapists.results };
      }
    }
    
    return {};
  } catch (error) {
    console.error('Error fetching route data:', error);
    return {};
  }
};

/**
 * Main SSR render function
 */
const renderApp = async (req, res) => {
  try {
    // Check cache first
    const cacheKey = generatePageCacheKey(req.path, req.query);
    const cached = pageCacheUtils.get(cacheKey);
    
    if (cached) {
      console.log(`Cache hit for ${req.path}`);
      return res.send(cached);
    }

    // Fetch data for the route
    const routeData = await fetchRouteData(req.path, req.query);

    // Create helmet context
    const helmetContext = {};

    // Render React app to string
    const html = renderToString(
      <HelmetProvider context={helmetContext}>
        <StaticRouter location={req.url}>
          <App />
        </StaticRouter>
      </HelmetProvider>
    );

    // Get helmet data
    const { helmet } = helmetContext;

    // Generate meta tags based on route
    const metaData = generateMetaTagsForRoute(req.path, req.query, routeData);
    
    // Generate structured data
    const structuredData = generateStructuredDataForRoute(req.path, req.query, routeData);

    // Replace template variables
    const finalHtml = template
      .replace('{{title}}', metaData.title || helmet?.title?.toString() || 'مرکز مشاوره و خدمات روانشناسی سرمد')
      .replace('{{description}}', metaData.description || helmet?.meta?.find(m => m.name === 'description')?.content || 'مرکز تخصصی مشاوره و خدمات روانشناسی')
      .replace('{{content}}', html)
      .replace('{{initialData}}', JSON.stringify(routeData))
      .replace('{{initialState}}', JSON.stringify(routeData))
      .replace('{{structuredData}}', structuredData ? `<script type="application/ld+json">${structuredData}</script>` : '')
      // Meta tags
      .replace('{{ogType}}', metaData.ogType || 'website')
      .replace('{{ogUrl}}', metaData.ogUrl || `${process.env.SITE_URL}${req.path}`)
      .replace('{{ogTitle}}', metaData.ogTitle || metaData.title)
      .replace('{{ogDescription}}', metaData.ogDescription || metaData.description)
      .replace('{{ogImage}}', metaData.ogImage || `${process.env.SITE_URL}/images/og-default.jpg`)
      .replace('{{twitterUrl}}', metaData.twitterUrl || metaData.ogUrl)
      .replace('{{twitterTitle}}', metaData.twitterTitle || metaData.ogTitle)
      .replace('{{twitterDescription}}', metaData.twitterDescription || metaData.ogDescription)
      .replace('{{twitterImage}}', metaData.twitterImage || metaData.ogImage)
      .replace('{{robots}}', metaData.robots || 'index, follow')
      .replace('{{author}}', metaData.author || '')
      .replace('{{keywords}}', metaData.keywords || '')
      .replace('{{canonical}}', metaData.canonical || `${process.env.SITE_URL}${req.path}`)
      .replace('{{siteName}}', process.env.SITE_NAME || 'مرکز مشاوره و خدمات روانشناسی سرمد');

    // Cache the response
    pageCacheUtils.set(cacheKey, finalHtml);

    res.send(finalHtml);
  } catch (error) {
    console.error('SSR Render Error:', error);
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
            <p>لطفاً دوباره تلاش کنید.</p>
            <a href="/" class="btn btn-primary">بازگشت به صفحه اصلی</a>
          </div>
        </div>
      </body>
      </html>
    `);
  }
};

/**
 * Generate meta tags based on route
 */
const generateMetaTagsForRoute = (path, query, routeData = {}) => {
  const baseUrl = process.env.SITE_URL || 'http://localhost:3001';
  
  // Default meta tags
  let metaData = {
    title: 'مرکز مشاوره و خدمات روانشناسی سرمد',
    description: 'مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای',
    url: `${baseUrl}${path}`,
    type: 'website',
    robots: 'index, follow'
  };

  // Route-specific meta tags with data
  if (path === '/') {
    metaData.title = 'خانه - مرکز مشاوره و خدمات روانشناسی سرمد';
    metaData.description = 'مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای';
  } else if (path.startsWith('/blog')) {
    if (routeData.post) {
      metaData.title = `${routeData.post.title} - وبلاگ مرکز مشاوره سرمد`;
      metaData.description = routeData.post.excerpt || routeData.post.content?.substring(0, 160);
      metaData.type = 'article';
      metaData.author = routeData.post.author_name;
      metaData.publishedTime = routeData.post.published_at || routeData.post.created_at;
      metaData.modifiedTime = routeData.post.updated_at;
      metaData.keywords = routeData.post.tags?.map(tag => tag.name) || [];
    } else if (path === '/blog') {
      metaData.title = 'وبلاگ - مرکز مشاوره و خدمات روانشناسی سرمد';
      metaData.description = 'آخرین مقالات و مطالب روانشناسی';
    }
  } else if (path.startsWith('/workshops')) {
    if (routeData.workshop) {
      metaData.title = `${routeData.workshop.title} - کارگاه‌های مرکز مشاوره سرمد`;
      metaData.description = routeData.workshop.description || routeData.workshop.title;
    } else {
      metaData.title = 'کارگاه‌ها - مرکز مشاوره و خدمات روانشناسی سرمد';
      metaData.description = 'کارگاه‌های آموزشی و تخصصی روانشناسی';
    }
  } else if (path.startsWith('/courses')) {
    if (routeData.course) {
      metaData.title = `${routeData.course.title} - دوره‌های مرکز مشاوره سرمد`;
      metaData.description = routeData.course.description || routeData.course.title;
    } else {
      metaData.title = 'دوره‌ها - مرکز مشاوره و خدمات روانشناسی سرمد';
      metaData.description = 'دوره‌های آموزشی روانشناسی';
    }
  } else if (path.startsWith('/packages')) {
    if (routeData.package) {
      metaData.title = `${routeData.package.title} - پکیج‌های مرکز مشاوره سرمد`;
      metaData.description = routeData.package.description || routeData.package.title;
    } else {
      metaData.title = 'پکیج‌ها - مرکز مشاوره و خدمات روانشناسی سرمد';
      metaData.description = 'پکیج‌های خدمات روانشناسی';
    }
  } else if (path.startsWith('/therapists')) {
    if (routeData.therapist) {
      metaData.title = `${routeData.therapist.full_name} - درمانگران مرکز مشاوره سرمد`;
      metaData.description = `پروفایل ${routeData.therapist.full_name}، ${routeData.therapist.specialization} با ${routeData.therapist.experience} سال تجربه`;
    } else {
      metaData.title = 'درمانگران - مرکز مشاوره و خدمات روانشناسی سرمد';
      metaData.description = 'تیم درمانگران متخصص ما';
    }
  } else if (path.startsWith('/about')) {
    if (path.includes('founder')) {
      metaData.title = 'درباره بنیان‌گذار - مرکز مشاوره و خدمات روانشناسی سرمد';
      metaData.description = 'درباره بنیان‌گذار مرکز مشاوره و خدمات روانشناسی سرمد';
    } else if (path.includes('institute')) {
      metaData.title = 'درباره موسسه - مرکز مشاوره و خدمات روانشناسی سرمد';
      metaData.description = 'درباره موسسه مشاوره و خدمات روانشناسی سرمد';
    }
  }

  return generateMetaTags(metaData);
};

/**
 * Generate structured data based on route
 */
const generateStructuredDataForRoute = (path, query, routeData = {}) => {
  if (routeData.post) {
    return generateArticleStructuredData(routeData.post);
  }
  
  // Return basic organization structured data for other pages
  const siteUrl = process.env.SITE_URL || 'http://localhost:3001';
  const siteName = process.env.SITE_NAME || 'مرکز مشاوره و خدمات روانشناسی سرمد';
  const siteDescription = process.env.SITE_DESCRIPTION || 'مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای';

  return JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: siteName,
    description: siteDescription,
    url: siteUrl,
    logo: `${siteUrl}/images/logo.png`,
    address: {
      '@type': 'PostalAddress',
      addressCountry: 'IR',
      addressLocality: 'تهران'
    }
  }, null, 2);
};

// Export sitemap functions for server.js
export { generateSitemap, generateRobotsTxt } from './lib/sitemap';

export default renderApp;
