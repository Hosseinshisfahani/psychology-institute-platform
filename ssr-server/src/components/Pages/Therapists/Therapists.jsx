import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';

const Therapists = ({ therapists = [] }) => {
  return (
    <>
      <Helmet>
        <title>درمانگران - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="تیم درمانگران متخصص و با تجربه مرکز مشاوره سرمد" />
        <meta name="keywords" content="درمانگر, روانشناس, مشاور, تیم درمان" />
        <link rel="canonical" href={`${process.env.SITE_URL}/therapists`} />
      </Helmet>

      <div className="container py-5">
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold">تیم درمانگران</h1>
          <p className="lead text-muted">
            تیم متخصص و با تجربه درمانگران مرکز مشاوره سرمد
          </p>
        </div>

        {therapists.length > 0 ? (
          <div className="row g-4">
            {therapists.map((therapist) => (
              <div key={therapist.id} className="col-lg-4 col-md-6">
                <div className="card h-100 border-0 shadow-sm">
                  {therapist.profile_image && (
                    <img
                      src={therapist.profile_image}
                      className="card-img-top"
                      alt={therapist.full_name}
                      style={{ height: '200px', objectFit: 'cover' }}
                    />
                  )}
                  <div className="card-body d-flex flex-column text-center">
                    <h5 className="card-title">
                      <Link 
                        to={`/therapists/${therapist.id}`} 
                        className="text-decoration-none text-dark"
                      >
                        {therapist.full_name}
                      </Link>
                    </h5>
                    <p className="card-text text-muted">
                      {therapist.specialization || 'روانشناس'}
                    </p>
                    <p className="card-text text-muted flex-grow-1">
                      {therapist.bio || 'متخصص روانشناسی با تجربه در زمینه مشاوره و درمان'}
                    </p>
                    <div className="d-flex justify-content-center gap-2 mt-auto">
                      <span className="badge bg-primary">{therapist.experience} سال تجربه</span>
                      <span className="badge bg-success">{therapist.specialization}</span>
                    </div>
                    <div className="mt-3">
                      <Link 
                        to={`/therapists/${therapist.id}`} 
                        className="btn btn-primary w-100"
                      >
                        <i className="fas fa-user me-2"></i>
                        مشاهده پروفایل
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
              <i className="fas fa-user-md text-muted mb-3" style={{ fontSize: '3rem' }}></i>
              <h5>درمانگری یافت نشد</h5>
              <p className="text-muted">به زودی درمانگران جدید اضافه خواهند شد</p>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Therapists;
