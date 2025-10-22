import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';

const Workshops = ({ workshops = [] }) => {
  return (
    <>
      <Helmet>
        <title>کارگاه‌ها - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="کارگاه‌های آموزشی و تخصصی روانشناسی برای بهبود مهارت‌های زندگی" />
        <meta name="keywords" content="کارگاه روانشناسی, آموزش, مهارت‌های زندگی, دوره آموزشی" />
        <link rel="canonical" href={`${process.env.SITE_URL}/workshops`} />
      </Helmet>

      <div className="container py-5">
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold">کارگاه‌های آموزشی</h1>
          <p className="lead text-muted">
            کارگاه‌های تخصصی روانشناسی برای بهبود مهارت‌های زندگی
          </p>
        </div>

        {workshops.length > 0 ? (
          <div className="row g-4">
            {workshops.map((workshop) => (
              <div key={workshop.id} className="col-lg-4 col-md-6">
                <div className="card h-100 border-0 shadow-sm">
                  {workshop.thumbnail && (
                    <img
                      src={workshop.thumbnail}
                      className="card-img-top"
                      alt={workshop.title}
                      style={{ height: '200px', objectFit: 'cover' }}
                    />
                  )}
                  <div className="card-body d-flex flex-column">
                    <div className="d-flex align-items-center mb-2">
                      <span className="badge bg-primary me-2">کارگاه</span>
                      <small className="text-muted">{workshop.start_date}</small>
                    </div>
                    <h5 className="card-title">
                      <Link 
                        to={`/workshops/${workshop.slug}`} 
                        className="text-decoration-none text-dark"
                      >
                        {workshop.title}
                      </Link>
                    </h5>
                    <p className="card-text text-muted flex-grow-1">
                      {workshop.description}
                    </p>
                    <div className="d-flex justify-content-between align-items-center mt-auto">
                      <div className="d-flex align-items-center">
                        <i className="fas fa-user me-2 text-muted"></i>
                        <small className="text-muted">{workshop.instructor_name}</small>
                      </div>
                      <div className="d-flex align-items-center">
                        <i className="fas fa-clock me-2 text-muted"></i>
                        <small className="text-muted">{workshop.duration} ساعت</small>
                      </div>
                    </div>
                    <div className="mt-3">
                      <Link 
                        to={`/workshops/${workshop.slug}`} 
                        className="btn btn-primary w-100"
                      >
                        <i className="fas fa-info-circle me-2"></i>
                        جزئیات بیشتر
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
              <i className="fas fa-graduation-cap text-muted mb-3" style={{ fontSize: '3rem' }}></i>
              <h5>کارگاهی یافت نشد</h5>
              <p className="text-muted">به زودی کارگاه‌های جدید اضافه خواهد شد</p>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Workshops;
