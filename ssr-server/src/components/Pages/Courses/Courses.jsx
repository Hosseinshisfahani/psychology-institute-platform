import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';

const Courses = ({ courses = [] }) => {
  return (
    <>
      <Helmet>
        <title>دوره‌ها - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="دوره‌های آموزشی روانشناسی و مهارت‌های زندگی" />
        <meta name="keywords" content="دوره روانشناسی, آموزش, مهارت‌های زندگی, دوره آموزشی" />
        <link rel="canonical" href={`${process.env.SITE_URL}/courses`} />
      </Helmet>

      <div className="container py-5">
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold">دوره‌های آموزشی</h1>
          <p className="lead text-muted">
            دوره‌های جامع روانشناسی و مهارت‌های زندگی
          </p>
        </div>

        {courses.length > 0 ? (
          <div className="row g-4">
            {courses.map((course) => (
              <div key={course.id} className="col-lg-4 col-md-6">
                <div className="card h-100 border-0 shadow-sm">
                  {course.thumbnail && (
                    <img
                      src={course.thumbnail}
                      className="card-img-top"
                      alt={course.title}
                      style={{ height: '200px', objectFit: 'cover' }}
                    />
                  )}
                  <div className="card-body d-flex flex-column">
                    <div className="d-flex align-items-center mb-2">
                      <span className="badge bg-success me-2">دوره</span>
                      <small className="text-muted">{course.created_at}</small>
                    </div>
                    <h5 className="card-title">
                      <Link 
                        to={`/courses/course/${course.slug}`} 
                        className="text-decoration-none text-dark"
                      >
                        {course.title}
                      </Link>
                    </h5>
                    <p className="card-text text-muted flex-grow-1">
                      {course.description}
                    </p>
                    <div className="d-flex justify-content-between align-items-center mt-auto">
                      <div className="d-flex align-items-center">
                        <i className="fas fa-user me-2 text-muted"></i>
                        <small className="text-muted">{course.instructor_name}</small>
                      </div>
                      <div className="d-flex align-items-center">
                        <i className="fas fa-clock me-2 text-muted"></i>
                        <small className="text-muted">{course.duration} ساعت</small>
                      </div>
                    </div>
                    <div className="mt-3">
                      <Link 
                        to={`/courses/course/${course.slug}`} 
                        className="btn btn-success w-100"
                      >
                        <i className="fas fa-play me-2"></i>
                        شروع دوره
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
              <i className="fas fa-book text-muted mb-3" style={{ fontSize: '3rem' }}></i>
              <h5>دوره‌ای یافت نشد</h5>
              <p className="text-muted">به زودی دوره‌های جدید اضافه خواهد شد</p>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Courses;
