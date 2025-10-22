import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useParams } from 'react-router-dom';

const TherapistDetail = ({ therapist }) => {
  const { id } = useParams();

  if (!therapist) {
    return (
      <div className="container py-5">
        <div className="card">
          <div className="card-body text-center py-5">
            <h5>درمانگر یافت نشد</h5>
            <Link to="/therapists" className="btn btn-primary">
              بازگشت به درمانگران
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{therapist.full_name} - درمانگران مرکز مشاوره سرمد</title>
        <meta name="description" content={`پروفایل ${therapist.full_name}، ${therapist.specialization} با ${therapist.experience} سال تجربه`} />
        <meta name="keywords" content={`${therapist.full_name}, ${therapist.specialization}, درمانگر, روانشناس`} />
        <link rel="canonical" href={`${process.env.SITE_URL}/therapists/${therapist.id}`} />
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
                  <Link to="/therapists">درمانگران</Link>
                </li>
                <li className="breadcrumb-item active" aria-current="page">
                  {therapist.full_name}
                </li>
              </ol>
            </nav>

            <article>
              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <span className="badge bg-primary me-2">درمانگر</span>
                  <span className="badge bg-success me-2">{therapist.specialization}</span>
                  <small className="text-muted">{therapist.experience} سال تجربه</small>
                </div>
                
                <h1 className="mb-3">{therapist.full_name}</h1>
                
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-graduation-cap me-2"></i>
                    <span>{therapist.education || 'روانشناسی'}</span>
                  </div>
                  <div className="d-flex gap-3">
                    <small className="text-muted">
                      <i className="fas fa-star me-1"></i>
                      {therapist.rating || '5.0'}
                    </small>
                    <small className="text-muted">
                      <i className="fas fa-users me-1"></i>
                      {therapist.clients_count || 0} مراجع
                    </small>
                  </div>
                </div>

                {therapist.profile_image && (
                  <img 
                    src={therapist.profile_image} 
                    alt={therapist.full_name}
                    className="img-fluid rounded mb-4"
                    style={{ width: '100%', height: '400px', objectFit: 'cover' }}
                  />
                )}
              </div>

              <div 
                className="therapist-content"
                dangerouslySetInnerHTML={{ __html: therapist.bio || therapist.description }}
              />

              <div className="mt-4 d-flex justify-content-between">
                <Link to="/therapists" className="btn btn-outline-primary">
                  <i className="fas fa-arrow-right me-2"></i>
                  بازگشت به درمانگران
                </Link>
                <button className="btn btn-primary">
                  <i className="fas fa-calendar-alt me-2"></i>
                  رزرو نوبت
                </button>
              </div>
            </article>
          </div>

          <div className="col-lg-4">
            {/* Therapist Info */}
            <div className="card mb-4">
              <div className="card-header">
                <h6>اطلاعات درمانگر</h6>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <strong>تخصص:</strong>
                  <p className="text-muted mb-0">{therapist.specialization}</p>
                </div>
                <div className="mb-3">
                  <strong>تجربه:</strong>
                  <p className="text-muted mb-0">{therapist.experience} سال</p>
                </div>
                <div className="mb-3">
                  <strong>تحصیلات:</strong>
                  <p className="text-muted mb-0">{therapist.education || 'روانشناسی'}</p>
                </div>
                <div className="mb-3">
                  <strong>امتیاز:</strong>
                  <p className="text-muted mb-0">
                    <i className="fas fa-star text-warning"></i>
                    {therapist.rating || '5.0'}
                  </p>
                </div>
                <div className="mb-3">
                  <strong>تعداد مراجعان:</strong>
                  <p className="text-muted mb-0">{therapist.clients_count || 0} نفر</p>
                </div>
              </div>
            </div>

            {/* Contact */}
            <div className="card">
              <div className="card-body text-center">
                <h6 className="card-title">رزرو نوبت</h6>
                <p className="card-text text-muted">
                  برای رزرو نوبت با این درمانگر اقدام کنید
                </p>
                <button className="btn btn-primary w-100">
                  <i className="fas fa-calendar-alt me-2"></i>
                  رزرو نوبت
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default TherapistDetail;
