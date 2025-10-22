import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useParams } from 'react-router-dom';

const WorkshopDetail = ({ workshop }) => {
  const { slug } = useParams();

  if (!workshop) {
    return (
      <div className="container py-5">
        <div className="card">
          <div className="card-body text-center py-5">
            <h5>کارگاه یافت نشد</h5>
            <Link to="/workshops" className="btn btn-primary">
              بازگشت به کارگاه‌ها
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{workshop.title} - کارگاه‌های مرکز مشاوره سرمد</title>
        <meta name="description" content={workshop.description || workshop.title} />
        <meta name="keywords" content={`کارگاه, ${workshop.title}, روانشناسی, آموزش`} />
        <link rel="canonical" href={`${process.env.SITE_URL}/workshops/${workshop.slug}`} />
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
                  <Link to="/workshops">کارگاه‌ها</Link>
                </li>
                <li className="breadcrumb-item active" aria-current="page">
                  {workshop.title}
                </li>
              </ol>
            </nav>

            <article>
              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <span className="badge bg-primary me-2">کارگاه</span>
                  <small className="text-muted">{workshop.start_date}</small>
                </div>
                
                <h1 className="mb-3">{workshop.title}</h1>
                
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-user me-2"></i>
                    <span>{workshop.instructor_name}</span>
                  </div>
                  <div className="d-flex gap-3">
                    <small className="text-muted">
                      <i className="fas fa-clock me-1"></i>
                      {workshop.duration} ساعت
                    </small>
                    <small className="text-muted">
                      <i className="fas fa-users me-1"></i>
                      {workshop.max_participants} نفر
                    </small>
                  </div>
                </div>

                {workshop.thumbnail && (
                  <img 
                    src={workshop.thumbnail} 
                    alt={workshop.title}
                    className="img-fluid rounded mb-4"
                    style={{ width: '100%', height: '400px', objectFit: 'cover' }}
                  />
                )}
              </div>

              <div 
                className="workshop-content"
                dangerouslySetInnerHTML={{ __html: workshop.content || workshop.description }}
              />

              <div className="mt-4 d-flex justify-content-between">
                <Link to="/workshops" className="btn btn-outline-primary">
                  <i className="fas fa-arrow-right me-2"></i>
                  بازگشت به کارگاه‌ها
                </Link>
                <button className="btn btn-primary">
                  <i className="fas fa-calendar-plus me-2"></i>
                  ثبت‌نام در کارگاه
                </button>
              </div>
            </article>
          </div>

          <div className="col-lg-4">
            {/* Workshop Info */}
            <div className="card mb-4">
              <div className="card-header">
                <h6>اطلاعات کارگاه</h6>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <strong>مدرس:</strong>
                  <p className="text-muted mb-0">{workshop.instructor_name}</p>
                </div>
                <div className="mb-3">
                  <strong>تاریخ شروع:</strong>
                  <p className="text-muted mb-0">{workshop.start_date}</p>
                </div>
                <div className="mb-3">
                  <strong>مدت زمان:</strong>
                  <p className="text-muted mb-0">{workshop.duration} ساعت</p>
                </div>
                <div className="mb-3">
                  <strong>ظرفیت:</strong>
                  <p className="text-muted mb-0">{workshop.max_participants} نفر</p>
                </div>
                {workshop.price && (
                  <div className="mb-3">
                    <strong>هزینه:</strong>
                    <p className="text-muted mb-0">{workshop.price} تومان</p>
                  </div>
                )}
              </div>
            </div>

            {/* Registration */}
            <div className="card">
              <div className="card-body text-center">
                <h6 className="card-title">ثبت‌نام در کارگاه</h6>
                <p className="card-text text-muted">
                  برای شرکت در این کارگاه ثبت‌نام کنید
                </p>
                <button className="btn btn-primary w-100">
                  <i className="fas fa-calendar-plus me-2"></i>
                  ثبت‌نام
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default WorkshopDetail;
