import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <>
      <Helmet>
        <title>صفحه یافت نشد - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="صفحه مورد نظر یافت نشد. لطفاً از منوی اصلی استفاده کنید." />
        <meta name="robots" content="noindex, nofollow" />
      </Helmet>

      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-lg-6 text-center">
            <div className="mb-4">
              <i className="fas fa-exclamation-triangle text-warning" style={{ fontSize: '5rem' }}></i>
            </div>
            <h1 className="display-1 fw-bold text-primary">404</h1>
            <h2 className="mb-3">صفحه یافت نشد</h2>
            <p className="lead text-muted mb-4">
              متأسفانه صفحه مورد نظر شما یافت نشد. ممکن است آدرس اشتباه باشد یا صفحه حذف شده باشد.
            </p>
            <div className="d-flex justify-content-center gap-3">
              <Link to="/" className="btn btn-primary">
                <i className="fas fa-home me-2"></i>
                بازگشت به خانه
              </Link>
              <Link to="/blog" className="btn btn-outline-primary">
                <i className="fas fa-newspaper me-2"></i>
                وبلاگ
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default NotFound;
