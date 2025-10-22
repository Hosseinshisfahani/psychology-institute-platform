import React from 'react';
import { Helmet } from 'react-helmet-async';

const AboutInstitute = () => {
  return (
    <>
      <Helmet>
        <title>درباره موسسه - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="درباره موسسه مشاوره و خدمات روانشناسی سرمد، تاریخچه، اهداف و خدمات" />
        <meta name="keywords" content="درباره موسسه, مرکز مشاوره, روانشناسی, خدمات درمانی" />
        <link rel="canonical" href={`${process.env.SITE_URL}/about/institute`} />
      </Helmet>

      <div className="container py-5">
        <div className="row">
          <div className="col-lg-8">
            <h1 className="display-4 fw-bold mb-4">درباره موسسه</h1>
            
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body">
                <h3 className="card-title">مرکز مشاوره و خدمات روانشناسی سرمد</h3>
                <p className="card-text text-muted">
                  مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای 
                  و تیم متخصص درمانگران برای بهبود کیفیت زندگی شما
                </p>
                <div className="d-flex flex-wrap gap-2">
                  <span className="badge bg-primary">مشاوره فردی</span>
                  <span className="badge bg-success">کارگاه‌های آموزشی</span>
                  <span className="badge bg-warning">دوره‌های تخصصی</span>
                  <span className="badge bg-info">پکیج‌های خدمات</span>
                </div>
              </div>
            </div>

            <div className="content">
              <h4 className="mb-3">تاریخچه موسسه</h4>
              <p className="lead">
                مرکز مشاوره و خدمات روانشناسی سرمد در سال [سال تأسیس] 
                با هدف ارائه خدمات روانشناسی با کیفیت تأسیس شد.
              </p>
              
              <p>
                این مرکز با تکیه بر تجربه و تخصص تیم درمانگران خود، 
                در طول سال‌های فعالیت، خدمات مشاوره و درمانی به هزاران 
                مراجع ارائه داده و در زمینه آموزش و تربیت درمانگران 
                جوان نیز فعالیت داشته است.
              </p>

              <h4 className="mb-3 mt-5">ماموریت و اهداف</h4>
              <div className="row g-3">
                <div className="col-md-6">
                  <div className="card h-100 border-0 bg-light">
                    <div className="card-body text-center">
                      <i className="fas fa-heart fa-2x text-primary mb-3"></i>
                      <h6>ماموریت</h6>
                      <p className="text-muted small">
                        ارائه خدمات روانشناسی با کیفیت برای بهبود کیفیت زندگی مراجعان
                      </p>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card h-100 border-0 bg-light">
                    <div className="card-body text-center">
                      <i className="fas fa-target fa-2x text-success mb-3"></i>
                      <h6>اهداف</h6>
                      <p className="text-muted small">
                        کمک به حل مشکلات روانی و بهبود روابط اجتماعی مراجعان
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <h4 className="mb-3 mt-5">خدمات ما</h4>
              <div className="row g-3">
                <div className="col-md-6">
                  <div className="d-flex align-items-start">
                    <i className="fas fa-user-md text-primary me-3 mt-1"></i>
                    <div>
                      <h6>مشاوره فردی</h6>
                      <p className="text-muted small">
                        مشاوره تخصصی برای حل مشکلات شخصی و بهبود روابط
                      </p>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex align-items-start">
                    <i className="fas fa-graduation-cap text-success me-3 mt-1"></i>
                    <div>
                      <h6>کارگاه‌های آموزشی</h6>
                      <p className="text-muted small">
                        کارگاه‌های تخصصی برای یادگیری مهارت‌های زندگی
                      </p>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex align-items-start">
                    <i className="fas fa-book text-warning me-3 mt-1"></i>
                    <div>
                      <h6>دوره‌های آموزشی</h6>
                      <p className="text-muted small">
                        دوره‌های جامع روانشناسی و مهارت‌های زندگی
                      </p>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex align-items-start">
                    <i className="fas fa-box text-info me-3 mt-1"></i>
                    <div>
                      <h6>پکیج‌های خدمات</h6>
                      <p className="text-muted small">
                        پکیج‌های متنوع خدمات روانشناسی و مشاوره
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <h4 className="mb-3 mt-5">تیم ما</h4>
              <p>
                تیم مرکز مشاوره سرمد متشکل از درمانگران متخصص و با تجربه است 
                که با تکیه بر دانش و تجربه خود، خدمات روانشناسی با کیفیت 
                به مراجعان ارائه می‌دهند.
              </p>

              <h4 className="mb-3 mt-5">تماس با ما</h4>
              <div className="row g-3">
                <div className="col-md-6">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-map-marker-alt text-primary me-3"></i>
                    <div>
                      <strong>آدرس:</strong>
                      <p className="text-muted mb-0">تهران، خیابان ولیعصر</p>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-phone text-success me-3"></i>
                    <div>
                      <strong>تلفن:</strong>
                      <p className="text-muted mb-0">021-12345678</p>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-envelope text-warning me-3"></i>
                    <div>
                      <strong>ایمیل:</strong>
                      <p className="text-muted mb-0">info@sarmadclinic.ir</p>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-clock text-info me-3"></i>
                    <div>
                      <strong>ساعات کاری:</strong>
                      <p className="text-muted mb-0">شنبه تا پنج‌شنبه: 9:00 - 18:00</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-lg-4">
            <div className="card mb-4">
              <div className="card-header">
                <h6>آمار و اطلاعات</h6>
              </div>
              <div className="card-body">
                <div className="row text-center">
                  <div className="col-6 mb-3">
                    <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-2" style={{width: '60px', height: '60px'}}>
                      <i className="fas fa-users text-primary"></i>
                    </div>
                    <h5 className="mb-0">1000+</h5>
                    <small className="text-muted">مراجع</small>
                  </div>
                  <div className="col-6 mb-3">
                    <div className="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-2" style={{width: '60px', height: '60px'}}>
                      <i className="fas fa-user-md text-success"></i>
                    </div>
                    <h5 className="mb-0">10+</h5>
                    <small className="text-muted">درمانگر</small>
                  </div>
                  <div className="col-6 mb-3">
                    <div className="bg-warning bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-2" style={{width: '60px', height: '60px'}}>
                      <i className="fas fa-graduation-cap text-warning"></i>
                    </div>
                    <h5 className="mb-0">50+</h5>
                    <small className="text-muted">کارگاه</small>
                  </div>
                  <div className="col-6 mb-3">
                    <div className="bg-info bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-2" style={{width: '60px', height: '60px'}}>
                      <i className="fas fa-book text-info"></i>
                    </div>
                    <h5 className="mb-0">20+</h5>
                    <small className="text-muted">دوره</small>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h6>گواهینامه‌ها</h6>
              </div>
              <div className="card-body">
                <p className="text-muted">به زودی...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default AboutInstitute;
