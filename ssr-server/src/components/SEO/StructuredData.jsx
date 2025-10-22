import React from 'react';

const StructuredData = ({ data }) => {
  if (!data) return null;

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data, null, 2)
      }}
    />
  );
};

// Article structured data
export const ArticleStructuredData = ({ post }) => {
  if (!post) return null;

  const siteUrl = process.env.SITE_URL || 'http://localhost:3001';
  const siteName = process.env.SITE_NAME || 'مرکز مشاوره و خدمات روانشناسی سرمد';

  const articleData = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.excerpt || post.content?.substring(0, 160),
    image: post.featured_image ? (post.featured_image.startsWith('http') ? post.featured_image : `${siteUrl}${post.featured_image}`) : undefined,
    author: {
      '@type': 'Person',
      name: post.author_name || 'نویسنده'
    },
    publisher: {
      '@type': 'Organization',
      name: siteName,
      logo: {
        '@type': 'ImageObject',
        url: `${siteUrl}/images/logo.png`
      }
    },
    datePublished: post.published_at || post.created_at,
    dateModified: post.updated_at || post.created_at,
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `${siteUrl}/blog/post/${post.slug}`
    },
    articleSection: post.category?.name,
    keywords: post.tags?.map(tag => tag.name).join(', ')
  };

  return <StructuredData data={articleData} />;
};

// Breadcrumb structured data
export const BreadcrumbStructuredData = ({ breadcrumbs }) => {
  if (!breadcrumbs || breadcrumbs.length === 0) return null;

  const siteUrl = process.env.SITE_URL || 'http://localhost:3001';

  const breadcrumbData = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((crumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: crumb.name,
      item: crumb.url ? `${siteUrl}${crumb.url}` : undefined
    }))
  };

  return <StructuredData data={breadcrumbData} />;
};

// Organization structured data
export const OrganizationStructuredData = () => {
  const siteUrl = process.env.SITE_URL || 'http://localhost:3001';
  const siteName = process.env.SITE_NAME || 'مرکز مشاوره و خدمات روانشناسی سرمد';
  const siteDescription = process.env.SITE_DESCRIPTION || 'مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای';

  const organizationData = {
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
    },
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: '+98-21-12345678',
      contactType: 'customer service'
    }
  };

  return <StructuredData data={organizationData} />;
};

// Course/Workshop structured data
export const CourseStructuredData = ({ course, type = 'Course' }) => {
  if (!course) return null;

  const siteUrl = process.env.SITE_URL || 'http://localhost:3001';
  const siteName = process.env.SITE_NAME || 'مرکز مشاوره و خدمات روانشناسی سرمد';

  const courseData = {
    '@context': 'https://schema.org',
    '@type': type,
    name: course.title,
    description: course.description || course.excerpt,
    provider: {
      '@type': 'Organization',
      name: siteName,
      url: siteUrl
    },
    courseMode: course.is_online ? 'online' : 'blended',
    educationalLevel: 'beginner',
    inLanguage: 'fa',
    offers: course.price ? {
      '@type': 'Offer',
      price: course.price,
      priceCurrency: 'IRR'
    } : undefined
  };

  return <StructuredData data={courseData} />;
};

export default StructuredData;
