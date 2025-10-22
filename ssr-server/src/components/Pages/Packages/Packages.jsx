import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';

const Packages = ({ packages = [] }) => {
  return (
    <>
      <Helmet>
        <title>پکیج‌ها - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="پکیج‌های خدمات روانشناسی و مشاوره" />
        <meta name="keywords" content="پکیج روانشناسی, مشاوره, خدمات روانشناسی" />
        <link rel="canonical" href={`${process.env.SITE_URL}/packages`} />
      </Helmet>

      <div className="container py-5">
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold">پکیج‌های خدمات</h1>
          <p className="lead text-muted">
            پکیج‌های متنوع خدمات روانشناسی و مشاوره
          </p>
        </div>

        {packages.length > 0 ? (
          <div className="row g-4">
            {packages.map((packageItem) => (
              <div key={packageItem.id} className="col-lg-4 col-md-6">
                <div className="card h-100 border-0 shadow-sm">
                  {packageItem.image && (
                    <img
                      src={packageItem.image}
                      className="card-img-top"
                      alt={packageItem.title}
                      style={{ height: '200px', objectFit: 'cover' }}
                    />
                  )}
                  <div className="card-body d-flex flex-column">
                    <div className="d-flex align-items-center mb-2">
                      <span className="badge bg-warning me-2">پکیج</span>
                      <small className="text-muted">{packageItem.created_at}</small>
                    </div>
                    <h5 className="card-title">
                      <Link 
                        to={`/packages/${packageItem.slug}`} 
                        className="text-decoration-none text-dark"
                      >
                        {packageItem.title}
                      </Link>
                    </h5>
                    <p className="card-text text-muted flex-grow-1">
                      {packageItem.description}
                    </p>
                    <div className="d-flex justify-content-between align-items-center mt-auto">
                      <div className="d-flex align-items-center">
                        <i className="fas fa-tag me-2 text-muted"></i>
                        <small className="text-muted">{packageItem.price} تومان</small>
                      </div>
                      <div className="d-flex align-items-center">
                        <i className="fas fa-clock me-2 text-muted"></i>
                        <small className="text-muted">{packageItem.duration} جلسه</small>
                      </div>
                    </div>
                    <div className="mt-3">
                      <Link 
                        to={`/packages/${packageItem.slug}`} 
                        className="btn btn-warning w-100"
                      >
                        <i className="fas fa-shopping-cart me-2"></i>
                        خرید پکیج
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card">
            <div className="card-body text-center py-5">
              <i className="fas fa-box text-muted mb-3" style={{ fontSize: '3rem' }}></i>
              <h5>پکیجی یافت نشد</h5>
              <p className="text-muted">به زودی پکیج‌های جدید اضافه خواهد شد</p>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Packages;
