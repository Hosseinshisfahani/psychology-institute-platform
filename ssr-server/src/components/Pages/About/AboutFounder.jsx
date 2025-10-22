import React from 'react';
import { Helmet } from 'react-helmet-async';

const AboutFounder = () => {
  return (
    <>
      <Helmet>
        <title>درباره بنیان‌گذار - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="درباره بنیان‌گذار مرکز مشاوره و خدمات روانشناسی سرمد" />
        <meta name="keywords" content="بنیان‌گذار, موسس, مرکز مشاوره, روانشناسی" />
        <link rel="canonical" href={`${process.env.SITE_URL}/about/founder`} />
      </Helmet>

      <div className="container py-5">
        <div className="row">
          <div className="col-lg-8">
            <h1 className="display-4 fw-bold mb-4">درباره بنیان‌گذار</h1>
            
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body">
                <div className="row align-items-center">
                  <div className="col-md-4 text-center mb-3 mb-md-0">
                    <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center" style={{width: '150px', height: '150px'}}>
                      <i className="fas fa-user fa-3x text-primary"></i>
                    </div>
                  </div>
                  <div className="col-md-8">
                    <h3 className="card-title">دکتر [نام بنیان‌گذار]</h3>
                    <p className="card-text text-muted">
                      بنیان‌گذار و مدیر مرکز مشاوره و خدمات روانشناسی سرمد
                    </p>
                    <div className="d-flex flex-wrap gap-2">
                      <span className="badge bg-primary">روانشناس</span>
                      <span className="badge bg-success">مشاور</span>
                      <span className="badge bg-warning">استاد دانشگاه</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="content">
              <h4 className="mb-3">زندگینامه</h4>
              <p className="lead">
                دکتر [نام بنیان‌گذار] با بیش از [X] سال تجربه در زمینه روانشناسی و مشاوره، 
                بنیان‌گذار مرکز مشاوره و خدمات روانشناسی سرمد است.
              </p>
              
              <p>
                ایشان پس از تحصیل در رشته روانشناسی و کسب مدارج عالی، 
                فعالیت خود را در زمینه مشاوره و درمان آغاز کرد و با تجربه‌اندوزی 
                در مراکز معتبر درمانی، تصمیم به تأسیس مرکز مشاوره سرمد گرفت.
              </p>

              <h4 className="mb-3 mt-5">تحصیلات و مدارک</h4>
              <ul className="list-unstyled">
                <li className="mb-2">
                  <i className="fas fa-graduation-cap text-primary me-2"></i>
                  دکترای روانشناسی از دانشگاه [نام دانشگاه]
                </li>
                <li className="mb-2">
                  <i className="fas fa-certificate text-success me-2"></i>
                  گواهینامه تخصصی در زمینه [زمینه تخصصی]
                </li>
                <li className="mb-2">
                  <i className="fas fa-award text-warning me-2"></i>
                  عضو انجمن روانشناسی ایران
                </li>
              </ul>

              <h4 className="mb-3 mt-5">تجربیات و فعالیت‌ها</h4>
              <p>
                دکتر [نام بنیان‌گذار] در طول سال‌های فعالیت خود، 
                خدمات مشاوره و درمانی به هزاران مراجع ارائه داده و 
                در زمینه آموزش و تربیت درمانگران جوان نیز فعالیت داشته است.
              </p>

              <h4 className="mb-3 mt-5">دیدگاه و اهداف</h4>
              <blockquote className="blockquote">
                <p className="mb-0">
                  "هدف ما در مرکز مشاوره سرمد، ارائه خدمات روانشناسی با کیفیت 
                  و کمک به بهبود کیفیت زندگی مراجعان است. ما معتقدیم که هر فرد 
                  شایسته زندگی بهتر و شادتر است."
                </p>
                <footer className="blockquote-footer mt-2">
                  دکتر [نام بنیان‌گذار]، بنیان‌گذار مرکز مشاوره سرمد
                </footer>
              </blockquote>
            </div>
          </div>

          <div className="col-lg-4">
            <div className="card mb-4">
              <div className="card-header">
                <h6>اطلاعات تماس</h6>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <strong>ایمیل:</strong>
                  <p className="text-muted mb-0">founder@sarmadclinic.ir</p>
                </div>
                <div className="mb-3">
                  <strong>تلفن:</strong>
                  <p className="text-muted mb-0">021-12345678</p>
                </div>
                <div className="mb-3">
                  <strong>ساعات کاری:</strong>
                  <p className="text-muted mb-0">شنبه تا پنج‌شنبه: 9:00 - 18:00</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h6>مقالات و کتاب‌ها</h6>
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

export default AboutFounder;
