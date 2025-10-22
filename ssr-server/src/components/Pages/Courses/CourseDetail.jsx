import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useParams } from 'react-router-dom';

const CourseDetail = ({ course }) => {
  const { slug } = useParams();

  if (!course) {
    return (
      <div className="container py-5">
        <div className="card">
          <div className="card-body text-center py-5">
            <h5>دوره یافت نشد</h5>
            <Link to="/courses" className="btn btn-primary">
              بازگشت به دوره‌ها
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{course.title} - دوره‌های مرکز مشاوره سرمد</title>
        <meta name="description" content={course.description || course.title} />
        <meta name="keywords" content={`دوره, ${course.title}, روانشناسی, آموزش`} />
        <link rel="canonical" href={`${process.env.SITE_URL}/courses/course/${course.slug}`} />
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
                  <Link to="/courses">دوره‌ها</Link>
                </li>
                <li className="breadcrumb-item active" aria-current="page">
                  {course.title}
                </li>
              </ol>
            </nav>

            <article>
              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <span className="badge bg-success me-2">دوره</span>
                  <small className="text-muted">{course.created_at}</small>
                </div>
                
                <h1 className="mb-3">{course.title}</h1>
                
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-user me-2"></i>
                    <span>{course.instructor_name}</span>
                  </div>
                  <div className="d-flex gap-3">
                    <small className="text-muted">
                      <i className="fas fa-clock me-1"></i>
                      {course.duration} ساعت
                    </small>
                    <small className="text-muted">
                      <i className="fas fa-users me-1"></i>
                      {course.students_count} دانشجو
                    </small>
                  </div>
                </div>

                {course.thumbnail && (
                  <img 
                    src={course.thumbnail} 
                    alt={course.title}
                    className="img-fluid rounded mb-4"
                    style={{ width: '100%', height: '400px', objectFit: 'cover' }}
                  />
                )}
              </div>

              <div 
                className="course-content"
                dangerouslySetInnerHTML={{ __html: course.content || course.description }}
              />

              <div className="mt-4 d-flex justify-content-between">
                <Link to="/courses" className="btn btn-outline-success">
                  <i className="fas fa-arrow-right me-2"></i>
                  بازگشت به دوره‌ها
                </Link>
                <button className="btn btn-success">
                  <i className="fas fa-play me-2"></i>
                  شروع دوره
                </button>
              </div>
            </article>
          </div>

          <div className="col-lg-4">
            {/* Course Info */}
            <div className="card mb-4">
              <div className="card-header">
                <h6>اطلاعات دوره</h6>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <strong>مدرس:</strong>
                  <p className="text-muted mb-0">{course.instructor_name}</p>
                </div>
                <div className="mb-3">
                  <strong>مدت زمان:</strong>
                  <p className="text-muted mb-0">{course.duration} ساعت</p>
                </div>
                <div className="mb-3">
                  <strong>تعداد دانشجو:</strong>
                  <p className="text-muted mb-0">{course.students_count} نفر</p>
                </div>
                {course.price && (
                  <div className="mb-3">
                    <strong>هزینه:</strong>
                    <p className="text-muted mb-0">{course.price} تومان</p>
                  </div>
                )}
              </div>
            </div>

            {/* Enrollment */}
            <div className="card">
              <div className="card-body text-center">
                <h6 className="card-title">شروع دوره</h6>
                <p className="card-text text-muted">
                  برای شروع این دوره ثبت‌نام کنید
                </p>
                <button className="btn btn-success w-100">
                  <i className="fas fa-play me-2"></i>
                  شروع دوره
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CourseDetail;
