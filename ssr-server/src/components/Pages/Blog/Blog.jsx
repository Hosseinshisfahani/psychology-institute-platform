import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useSearchParams } from 'react-router-dom';
import { blogApi } from '../../../lib/api';

const Blog = ({ posts = [], categories = [], searchQuery = '' }) => {
  const [searchParams] = useSearchParams();
  const currentQuery = searchQuery || searchParams.get('q') || '';

  return (
    <>
      <Helmet>
        <title>وبلاگ - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="آخرین مقالات و مطالب روانشناسی، مهارت‌های زندگی و راهکارهای بهبود کیفیت زندگی" />
        <meta name="keywords" content="مقالات روانشناسی, مهارت‌های زندگی, مشاوره, درمان, روانشناسی" />
        <link rel="canonical" href={`${process.env.SITE_URL}/blog`} />
      </Helmet>

      <div className="container py-5">
        <div className="row">
          <div className="col-lg-8">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h1>وبلاگ</h1>
              {currentQuery && (
                <div className="alert alert-info mb-0">
                  نتایج جستجو برای: <strong>"{currentQuery}"</strong>
                </div>
              )}
            </div>

            {/* Search and Filter */}
            <div className="card mb-4">
              <div className="card-body">
                <form method="GET" action="/blog/search">
                  <div className="row">
                    <div className="col-md-8">
                      <div className="input-group">
                        <input
                          type="text"
                          className="form-control"
                          name="q"
                          placeholder="جستجو در مقالات..."
                          defaultValue={currentQuery}
                        />
                        <button type="submit" className="btn btn-outline-primary">
                          <i className="fas fa-search"></i>
                        </button>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <select className="form-select" name="category">
                        <option value="">همه دسته‌بندی‌ها</option>
                        {categories.map((category) => (
                          <option key={category.id} value={category.slug}>
                            {category.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </form>
              </div>
            </div>

            {/* Posts */}
            {posts.length > 0 ? (
              <div className="row">
                {posts.map((post) => (
                  <div key={post.id} className="col-md-6 col-lg-4 mb-4">
                    <div className="card h-100 border-0 shadow-sm">
                      {post.featured_image && (
                        <img
                          src={post.featured_image}
                          className="card-img-top"
                          alt={post.title}
                          style={{ height: '200px', objectFit: 'cover' }}
                        />
                      )}
                      <div className="card-body d-flex flex-column">
                        <div className="d-flex align-items-center mb-2">
                          <span className="badge bg-primary me-2">{post.category.name}</span>
                          <small className="text-muted">{post.created_at_persian}</small>
                        </div>
                        <h5 className="card-title">
                          <Link 
                            to={`/blog/post/${post.slug}`} 
                            className="text-decoration-none text-dark"
                          >
                            {post.title}
                          </Link>
                        </h5>
                        <p className="card-text text-muted flex-grow-1">
                          {post.excerpt}
                        </p>
                        <div className="d-flex justify-content-between align-items-center mt-auto">
                          <small className="text-muted">
                            <i className="fas fa-user me-1"></i>
                            {post.author_name}
                          </small>
                          <div className="d-flex gap-3">
                            <small className="text-muted">
                              <i className="fas fa-eye me-1"></i>
                              {post.view_count}
                            </small>
                            <small className="text-muted">
                              <i className="fas fa-heart me-1"></i>
                              {post.like_count}
                            </small>
                            <small className="text-muted">
                              <i className="fas fa-comment me-1"></i>
                              {post.comment_count || 0}
                            </small>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card">
                <div className="card-body text-center py-5">
                  <i className="fas fa-newspaper text-muted mb-3" style={{ fontSize: '3rem' }}></i>
                  <h5>مقاله‌ای یافت نشد</h5>
                  <p className="text-muted">
                    {currentQuery ? 'لطفاً جستجوی خود را تغییر دهید' : 'هنوز مقاله‌ای منتشر نشده است'}
                  </p>
                  {currentQuery && (
                    <Link to="/blog" className="btn btn-primary">
                      مشاهده همه مقالات
                    </Link>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="col-lg-4">
            {/* Categories */}
            <div className="card mb-4">
              <div className="card-header">
                <h6>دسته‌بندی‌ها</h6>
              </div>
              <div className="card-body">
                <div className="list-group list-group-flush">
                  <Link to="/blog" className="list-group-item list-group-item-action">
                    همه دسته‌بندی‌ها
                  </Link>
                  {categories.map((category) => (
                    <Link
                      key={category.id}
                      to={`/blog/category/${category.slug}`}
                      className="list-group-item list-group-item-action"
                    >
                      {category.name}
                    </Link>
                  ))}
                </div>
              </div>
            </div>

            {/* Popular Posts */}
            <div className="card">
              <div className="card-header">
                <h6>مقالات محبوب</h6>
              </div>
              <div className="card-body">
                <p className="text-muted text-center">به زودی...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Blog;
