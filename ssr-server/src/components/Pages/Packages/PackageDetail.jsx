import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useParams } from 'react-router-dom';

const PackageDetail = ({ packageItem }) => {
  const { slug } = useParams();

  if (!packageItem) {
    return (
      <div className="container py-5">
        <div className="card">
          <div className="card-body text-center py-5">
            <h5>پکیج یافت نشد</h5>
            <Link to="/packages" className="btn btn-primary">
              بازگشت به پکیج‌ها
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{packageItem.title} - پکیج‌های مرکز مشاوره سرمد</title>
        <meta name="description" content={packageItem.description || packageItem.title} />
        <meta name="keywords" content={`پکیج, ${packageItem.title}, روانشناسی, مشاوره`} />
        <link rel="canonical" href={`${process.env.SITE_URL}/packages/${packageItem.slug}`} />
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
                  <Link to="/packages">پکیج‌ها</Link>
                </li>
                <li className="breadcrumb-item active" aria-current="page">
                  {packageItem.title}
                </li>
              </ol>
            </nav>

            <article>
              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <span className="badge bg-warning me-2">پکیج</span>
                  <small className="text-muted">{packageItem.created_at}</small>
                </div>
                
                <h1 className="mb-3">{packageItem.title}</h1>
                
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-tag me-2"></i>
                    <span>{packageItem.price} تومان</span>
                  </div>
                  <div className="d-flex gap-3">
                    <small className="text-muted">
                      <i className="fas fa-clock me-1"></i>
                      {packageItem.duration} جلسه
                    </small>
                    <small className="text-muted">
                      <i className="fas fa-users me-1"></i>
                      {packageItem.max_participants} نفر
                    </small>
                  </div>
                </div>

                {packageItem.image && (
                  <img 
                    src={packageItem.image} 
                    alt={packageItem.title}
                    className="img-fluid rounded mb-4"
                    style={{ width: '100%', height: '400px', objectFit: 'cover' }}
                  />
                )}
              </div>

              <div 
                className="package-content"
                dangerouslySetInnerHTML={{ __html: packageItem.content || packageItem.description }}
              />

              <div className="mt-4 d-flex justify-content-between">
                <Link to="/packages" className="btn btn-outline-warning">
                  <i className="fas fa-arrow-right me-2"></i>
                  بازگشت به پکیج‌ها
                </Link>
                <button className="btn btn-warning">
                  <i className="fas fa-shopping-cart me-2"></i>
                  خرید پکیج
                </button>
              </div>
            </article>
          </div>

          <div className="col-lg-4">
            {/* Package Info */}
            <div className="card mb-4">
              <div className="card-header">
                <h6>اطلاعات پکیج</h6>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <strong>قیمت:</strong>
                  <p className="text-muted mb-0">{packageItem.price} تومان</p>
                </div>
                <div className="mb-3">
                  <strong>مدت زمان:</strong>
                  <p className="text-muted mb-0">{packageItem.duration} جلسه</p>
                </div>
                <div className="mb-3">
                  <strong>ظرفیت:</strong>
                  <p className="text-muted mb-0">{packageItem.max_participants} نفر</p>
                </div>
                {packageItem.discount && (
                  <div className="mb-3">
                    <strong>تخفیف:</strong>
                    <p className="text-success mb-0">{packageItem.discount}%</p>
                  </div>
                )}
              </div>
            </div>

            {/* Purchase */}
            <div className="card">
              <div className="card-body text-center">
                <h6 className="card-title">خرید پکیج</h6>
                <p className="card-text text-muted">
                  برای خرید این پکیج اقدام کنید
                </p>
                <button className="btn btn-warning w-100">
                  <i className="fas fa-shopping-cart me-2"></i>
                  خرید پکیج
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default PackageDetail;
