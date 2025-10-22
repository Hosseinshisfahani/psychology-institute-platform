import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useParams } from 'react-router-dom';

const PostDetail = ({ post }) => {
  const { slug } = useParams();

  if (!post) {
    return (
      <div className="container py-5">
        <div className="card">
          <div className="card-body text-center py-5">
            <h5>مقاله یافت نشد</h5>
            <Link to="/blog" className="btn btn-primary">
              بازگشت به وبلاگ
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{post.title} - وبلاگ مرکز مشاوره سرمد</title>
        <meta name="description" content={post.excerpt || post.content?.substring(0, 160)} />
        <meta name="keywords" content={post.tags?.map(tag => tag.name).join(', ')} />
        <meta name="author" content={post.author_name} />
        <meta name="article:published_time" content={post.published_at || post.created_at} />
        <meta name="article:modified_time" content={post.updated_at} />
        <meta name="article:section" content={post.category?.name} />
        <meta name="article:tag" content={post.tags?.map(tag => tag.name).join(', ')} />
        
        {/* Open Graph */}
        <meta property="og:type" content="article" />
        <meta property="og:title" content={post.title} />
        <meta property="og:description" content={post.excerpt || post.content?.substring(0, 160)} />
        <meta property="og:image" content={post.featured_image || `${process.env.SITE_URL}/images/og-default.jpg`} />
        <meta property="og:url" content={`${process.env.SITE_URL}/blog/post/${post.slug}`} />
        <meta property="og:site_name" content="مرکز مشاوره و خدمات روانشناسی سرمد" />
        <meta property="article:author" content={post.author_name} />
        <meta property="article:published_time" content={post.published_at || post.created_at} />
        <meta property="article:modified_time" content={post.updated_at} />
        <meta property="article:section" content={post.category?.name} />
        <meta property="article:tag" content={post.tags?.map(tag => tag.name).join(', ')} />
        
        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={post.title} />
        <meta name="twitter:description" content={post.excerpt || post.content?.substring(0, 160)} />
        <meta name="twitter:image" content={post.featured_image || `${process.env.SITE_URL}/images/og-default.jpg`} />
        
        <link rel="canonical" href={`${process.env.SITE_URL}/blog/post/${post.slug}`} />
      </Helmet>

      <div className="container py-5">
        <div className="row">
          <div className="col-lg-8">
            <article>
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
                    {post.title}
                  </li>
                </ol>
              </nav>

              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <span className="badge bg-primary me-2">{post.category?.name}</span>
                  <small className="text-muted">{post.created_at_persian}</small>
                </div>
                
                <h1 className="mb-3">{post.title}</h1>
                
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-user me-2"></i>
                    <span>{post.author_name}</span>
                  </div>
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

                {post.featured_image && (
                  <img 
                    src={post.featured_image} 
                    alt={post.title}
                    className="img-fluid rounded mb-4"
                    style={{ width: '100%', height: '400px', objectFit: 'cover' }}
                  />
                )}
              </div>

              <div 
                className="post-content"
                dangerouslySetInnerHTML={{ __html: post.content }}
              />

              {post.tags && post.tags.length > 0 && (
                <div className="mt-4">
                  <h6>برچسب‌ها:</h6>
                  <div className="d-flex flex-wrap gap-2">
                    {post.tags.map((tag) => (
                      <span key={tag.slug} className="badge bg-secondary">
                        {tag.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-4 d-flex justify-content-between">
                <Link to="/blog" className="btn btn-outline-primary">
                  <i className="fas fa-arrow-right me-2"></i>
                  بازگشت به وبلاگ
                </Link>
                <div className="d-flex gap-2">
                  <button className="btn btn-outline-danger">
                    <i className="fas fa-heart me-2"></i>
                    لایک
                  </button>
                  <button className="btn btn-outline-primary">
                    <i className="fas fa-share me-2"></i>
                    اشتراک
                  </button>
                </div>
              </div>
            </article>
          </div>

          <div className="col-lg-4">
            {/* Author Info */}
            <div className="card mb-4">
              <div className="card-header">
                <h6>درباره نویسنده</h6>
              </div>
              <div className="card-body">
                <div className="d-flex align-items-center mb-3">
                  <div className="bg-primary bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center me-3" style={{width: '50px', height: '50px'}}>
                    <i className="fas fa-user text-primary"></i>
                  </div>
                  <div>
                    <h6 className="mb-0">{post.author_name}</h6>
                    <small className="text-muted">نویسنده</small>
                  </div>
                </div>
                <p className="text-muted small">
                  متخصص روانشناسی با تجربه در زمینه مشاوره و درمان
                </p>
              </div>
            </div>

            {/* Related Posts */}
            <div className="card">
              <div className="card-header">
                <h6>مقالات مرتبط</h6>
              </div>
              <div className="card-body">
                <p className="text-muted">به زودی...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default PostDetail;
