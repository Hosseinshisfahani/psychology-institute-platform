import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useParams } from 'react-router-dom';

const TagArchive = ({ posts = [], tag }) => {
  const { slug } = useParams();

  return (
    <>
      <Helmet>
        <title>برچسب: {tag?.name || 'نامشخص'} - وبلاگ مرکز مشاوره سرمد</title>
        <meta name="description" content={`مقالات برچسب ${tag?.name || 'انتخاب شده'} در وبلاگ مرکز مشاوره سرمد`} />
        <link rel="canonical" href={`${process.env.SITE_URL}/blog/tag/${slug}`} />
      </Helmet>

      <div className="container py-5">
        <div className="row">
          <div className="col-lg-8">
            {/* Breadcrumb */}
            <nav aria-label="breadcrumb" className="mb-4">
              <ol className="breadcrumb">
                <li className="breadcrumb-item">
                  <Link to="/">خانه</Link>
                </li>
                <li className="breadcrumb-item">
                  <Link to="/blog">وبلاگ</Link>
                </li>
                <li className="breadcrumb-item active" aria-current="page">
                  برچسب: {tag?.name || 'نامشخص'}
                </li>
              </ol>
            </nav>

            <div className="d-flex justify-content-between align-items-center mb-4">
              <h1>برچسب: {tag?.name || 'نامشخص'}</h1>
              <span className="badge bg-secondary">{posts.length} مقاله</span>
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
                          <span className="badge bg-primary me-2">{post.category?.name}</span>
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
                  <i className="fas fa-tag text-muted mb-3" style={{ fontSize: '3rem' }}></i>
                  <h5>مقاله‌ای با این برچسب یافت نشد</h5>
                  <p className="text-muted">لطفاً برچسب دیگری را انتخاب کنید</p>
                  <Link to="/blog" className="btn btn-primary">
                    مشاهده همه مقالات
                  </Link>
                </div>
              </div>
            )}
          </div>

          <div className="col-lg-4">
            {/* Tag Info */}
            <div className="card mb-4">
              <div className="card-header">
                <h6>درباره این برچسب</h6>
              </div>
              <div className="card-body">
                <h5>
                  <span className="badge bg-secondary me-2">{tag?.name || 'نامشخص'}</span>
                </h5>
                <div className="d-flex align-items-center">
                  <span className="badge bg-primary me-2">{posts.length}</span>
                  <span className="text-muted">مقاله</span>
                </div>
              </div>
            </div>

            {/* Back to Blog */}
            <div className="card">
              <div className="card-body text-center">
                <Link to="/blog" className="btn btn-outline-primary">
                  <i className="fas fa-arrow-right me-2"></i>
                  بازگشت به وبلاگ
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default TagArchive;
