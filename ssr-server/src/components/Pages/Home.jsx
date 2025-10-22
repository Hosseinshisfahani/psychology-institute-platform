import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <>
      <Helmet>
        <title>خانه - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای و تیم متخصص درمانگران" />
        <meta name="keywords" content="مشاوره روانشناسی, درمان, کارگاه روانشناسی, دوره روانشناسی" />
      </Helmet>

      {/* Hero Section */}
      <section className="bg-primary text-white py-5">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6">
              <h1 className="display-4 fw-bold mb-4">
                مرکز مشاوره و خدمات روانشناسی سرمد
              </h1>
              <p className="lead mb-4">
                مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای 
                و تیم متخصص درمانگران برای بهبود کیفیت زندگی شما
              </p>
              <div className="d-flex gap-3">
                <Link to="/therapists" className="btn btn-light btn-lg">
                  <i className="fas fa-user-md me-2"></i>
                  درمانگران ما
                </Link>
                <Link to="/workshops" className="btn btn-outline-light btn-lg">
                  <i className="fas fa-graduation-cap me-2"></i>
                  کارگاه‌ها
                </Link>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="text-center">
                <i className="fas fa-heart fa-10x text-white-50"></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-5 fw-bold">خدمات ما</h2>
            <p className="lead text-muted">
              خدمات تخصصی روانشناسی برای بهبود کیفیت زندگی
            </p>
          </div>
          
          <div className="row g-4">
            <div className="col-lg-4 col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                    <i className="fas fa-user-md fa-2x text-primary"></i>
                  </div>
                  <h5 className="card-title">مشاوره فردی</h5>
                  <p className="card-text text-muted">
                    مشاوره تخصصی برای حل مشکلات شخصی و بهبود روابط
                  </p>
                  <Link to="/therapists" className="btn btn-outline-primary">
                    بیشتر بدانید
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="col-lg-4 col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <div className="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                    <i className="fas fa-graduation-cap fa-2x text-success"></i>
                  </div>
                  <h5 className="card-title">کارگاه‌های آموزشی</h5>
                  <p className="card-text text-muted">
                    کارگاه‌های تخصصی برای یادگیری مهارت‌های زندگی
                  </p>
                  <Link to="/workshops" className="btn btn-outline-success">
                    بیشتر بدانید
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="col-lg-4 col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body text-center p-4">
                  <div className="bg-warning bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                    <i className="fas fa-book fa-2x text-warning"></i>
                  </div>
                  <h5 className="card-title">دوره‌های آموزشی</h5>
                  <p className="card-text text-muted">
                    دوره‌های جامع روانشناسی و مهارت‌های زندگی
                  </p>
                  <Link to="/courses" className="btn btn-outline-warning">
                    بیشتر بدانید
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Latest Blog Posts */}
      <section className="bg-light py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-5 fw-bold">آخرین مقالات</h2>
            <p className="lead text-muted">
              مطالب تخصصی روانشناسی و مهارت‌های زندگی
            </p>
          </div>
          
          <div className="row g-4">
            <div className="col-lg-4 col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body">
                  <div className="d-flex align-items-center mb-3">
                    <span className="badge bg-primary me-2">روانشناسی</span>
                    <small className="text-muted">2 روز پیش</small>
                  </div>
                  <h5 className="card-title">تکنیک‌های مدیریت استرس</h5>
                  <p className="card-text text-muted">
                    راهکارهای عملی برای کاهش استرس و بهبود کیفیت زندگی
                  </p>
                  <Link to="/blog" className="btn btn-outline-primary">
                    ادامه مطلب
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="col-lg-4 col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body">
                  <div className="d-flex align-items-center mb-3">
                    <span className="badge bg-success me-2">مهارت‌های زندگی</span>
                    <small className="text-muted">5 روز پیش</small>
                  </div>
                  <h5 className="card-title">بهبود روابط اجتماعی</h5>
                  <p className="card-text text-muted">
                    راهکارهایی برای تقویت روابط و ارتباطات اجتماعی
                  </p>
                  <Link to="/blog" className="btn btn-outline-success">
                    ادامه مطلب
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="col-lg-4 col-md-6">
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body">
                  <div className="d-flex align-items-center mb-3">
                    <span className="badge bg-warning me-2">خانواده</span>
                    <small className="text-muted">1 هفته پیش</small>
                  </div>
                  <h5 className="card-title">روابط خانوادگی سالم</h5>
                  <p className="card-text text-muted">
                    راهکارهایی برای تقویت روابط خانوادگی و حل تعارضات
                  </p>
                  <Link to="/blog" className="btn btn-outline-warning">
                    ادامه مطلب
                  </Link>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-center mt-4">
            <Link to="/blog" className="btn btn-primary btn-lg">
              <i className="fas fa-newspaper me-2"></i>
              مشاهده همه مقالات
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary text-white py-5">
        <div className="container text-center">
          <h2 className="display-5 fw-bold mb-3">آماده شروع هستید؟</h2>
          <p className="lead mb-4">
            با تیم متخصص ما همراه شوید و زندگی بهتری را تجربه کنید
          </p>
          <div className="d-flex justify-content-center gap-3">
            <Link to="/therapists" className="btn btn-light btn-lg">
              <i className="fas fa-calendar-alt me-2"></i>
              رزرو نوبت
            </Link>
            <Link to="/contact" className="btn btn-outline-light btn-lg">
              <i className="fas fa-phone me-2"></i>
              تماس با ما
            </Link>
          </div>
        </div>
      </section>
    </>
  );
};

export default Home;
