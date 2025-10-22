import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Breadcrumbs = ({ data = {} }) => {
  const location = useLocation();
  const path = location.pathname;

  const breadcrumbs = generateBreadcrumbs(path, data);

  if (breadcrumbs.length <= 1) return null;

  return (
    <nav aria-label="breadcrumb" className="mb-4">
      <ol className="breadcrumb">
        {breadcrumbs.map((crumb, index) => (
          <li 
            key={index} 
            className={`breadcrumb-item ${index === breadcrumbs.length - 1 ? 'active' : ''}`}
            aria-current={index === breadcrumbs.length - 1 ? 'page' : undefined}
          >
            {crumb.url ? (
              <Link to={crumb.url} className="text-decoration-none">
                {crumb.name}
              </Link>
            ) : (
              crumb.name
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

const generateBreadcrumbs = (path, data = {}) => {
  const breadcrumbs = [
    { name: 'خانه', url: '/' }
  ];

  const pathSegments = path.split('/').filter(segment => segment);

  if (pathSegments.includes('blog')) {
    breadcrumbs.push({ name: 'وبلاگ', url: '/blog' });
    
    if (pathSegments.includes('post') && data.post) {
      breadcrumbs.push({ name: data.post.title, url: null });
    } else if (pathSegments.includes('category') && data.category) {
      breadcrumbs.push({ name: data.category.name, url: null });
    } else if (pathSegments.includes('tag') && data.tag) {
      breadcrumbs.push({ name: data.tag.name, url: null });
    }
  } else if (pathSegments.includes('workshops')) {
    breadcrumbs.push({ name: 'کارگاه‌ها', url: '/workshops' });
    if (data.workshop) {
      breadcrumbs.push({ name: data.workshop.title, url: null });
    }
  } else if (pathSegments.includes('courses')) {
    breadcrumbs.push({ name: 'دوره‌ها', url: '/courses' });
    if (data.course) {
      breadcrumbs.push({ name: data.course.title, url: null });
    }
  } else if (pathSegments.includes('packages')) {
    breadcrumbs.push({ name: 'پکیج‌ها', url: '/packages' });
    if (data.package) {
      breadcrumbs.push({ name: data.package.title, url: null });
    }
  } else if (pathSegments.includes('therapists')) {
    breadcrumbs.push({ name: 'درمانگران', url: '/therapists' });
    if (data.therapist) {
      breadcrumbs.push({ name: data.therapist.full_name, url: null });
    }
  } else if (pathSegments.includes('about')) {
    if (pathSegments.includes('founder')) {
      breadcrumbs.push({ name: 'درباره بنیان‌گذار', url: null });
    } else if (pathSegments.includes('institute')) {
      breadcrumbs.push({ name: 'درباره موسسه', url: null });
    }
  }

  return breadcrumbs;
};

export default Breadcrumbs;
