import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

const AboutInstitute: React.FC = () => {
  // Helper function to get image path (handles space in directory name)
  const getImagePath = (filename: string): string => {
    // URL encode the space in directory name
    return `/images/about%20institue/${filename}`;
  };

  // Helper function to handle image loading errors
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    const target = e.target as HTMLImageElement;
    // Hide broken images
    target.style.display = 'none';
  };

  return (
    <>
      <Helmet>
        <title>درباره مؤسسه - مرکز مشاوره و خدمات روانشناسی سرمد</title>
        <meta name="description" content="آشنایی با تاریخچه، دستاوردها و فعالیت‌های مرکز مشاوره و خدمات روانشناسی سرمد" />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "مرکز مشاوره و خدمات روانشناسی سرمد",
            "alternateName": "مرکز مشاوره سرمد",
            "description": "بیش از ۱۵ سال تجربه در ارائه خدمات روانشناسی و مشاوره تخصصی",
            "url": "https://sarmadclinic.ir",
            "logo": "/images/IMG_20240123_171348_081.png",
            "image": "/images/IMG_20240123_171348_081.png",
            "foundingDate": "2009",
            "founder": {
              "@type": "Person",
              "name": "دکتر سید مجتبی امامی دوست"
            },
            "address": {
              "@type": "PostalAddress",
              "addressCountry": "IR",
              "addressLocality": "ایران"
            },
            "contactPoint": {
              "@type": "ContactPoint",
              "telephone": "+98-21-91090097",
              "contactType": "customer service",
              "availableLanguage": "Persian"
            },
            "sameAs": [
              "https://sarmadclinic.ir"
            ],
            "serviceType": [
              "مشاوره روانشناسی",
              "درمان شناختی",
              "طرحواره درمانی",
              "دوره‌های آموزشی",
              "تست‌های روانشناسی"
            ],
            "areaServed": {
              "@type": "Country",
              "name": "ایران"
            },
            "hasOfferCatalog": {
              "@type": "OfferCatalog",
              "name": "خدمات روانشناسی",
              "itemListElement": [
                {
                  "@type": "Offer",
                  "itemOffered": {
                    "@type": "Service",
                    "name": "مشاوره فردی"
                  }
                },
                {
                  "@type": "Offer",
                  "itemOffered": {
                    "@type": "Service",
                    "name": "دوره‌های آموزشی"
                  }
                },
                {
                  "@type": "Offer",
                  "itemOffered": {
                    "@type": "Service",
                    "name": "تست‌های روانشناسی"
                  }
                }
              ]
            }
          })}
        </script>
      </Helmet>

      {/* Hero Section */}
      <section className="institute-hero">
        <Container className="institute-content">
          <Row className="align-items-center">
            <Col lg={4} className="text-center">
              <img 
                src="/images/1744027219152.png" 
                alt="مرکز مشاوره و خدمات روانشناسی سرمد" 
                className="institute-logo-large"
                loading="lazy"
              />
            </Col>
            <Col lg={8}>
              <h1 className="display-4 mb-3">مرکز مشاوره و خدمات روانشناسی سرمد</h1>
              <h4 className="mb-4">بیش از ۱۵ سال تجربه در ارائه خدمات روانشناسی</h4>
              <p className="lead">
                از سال ۱۳۸۸ با مؤسسه علمی پژوهشی روان‌شناسی فعالیت خودمان را آغاز کردیم و در طول این سال‌ها توانسته‌ایم خدمات متنوع و با کیفیتی را ارائه دهیم.
              </p>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Introduction Image Gallery */}
      <section className="py-5">
        <Container>
          <Row className="g-4 mb-5">
            <Col md={6}>
              <div className="content-image-wrapper">
                <img 
                  src={getImagePath('20240725_165904.jpg')}
                  onError={handleImageError}
                  alt="فعالیت‌های مرکز مشاوره سرمد" 
                  className="content-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={6}>
              <div className="content-image-wrapper">
                <img 
                  src={getImagePath('20240726_095433.jpg')}
                  onError={handleImageError} 
                  alt="کارگاه‌های آموزشی مرکز مشاوره سرمد" 
                  className="content-image"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Timeline Section */}
      <section className="py-5">
        <Container>
          <h2 className="section-title">تاریخچه مؤسسه</h2>
          
          {/* 1388 Start */}
          <div className="timeline-section">
            <div className="timeline-year">۱۳۸۸ - آغاز فعالیت</div>
            <Row className="align-items-center g-4">
              <Col lg={6}>
                <p className="mb-3">
                  از سال ۱۳۸۸ با مؤسسه علمی پژوهشی روان‌شناسی فعالیت خودمان را آغاز کردیم.
                </p>
                <div className="activities-grid">
                  <div className="activity-card">
                    <i className="fas fa-chalkboard-teacher activity-icon"></i>
                    <h5>کارگاه‌های تخصصی و عمومی</h5>
                    <p className="text-muted mb-0">برگزاری دوره‌های آموزشی متنوع برای متخصصان و عموم</p>
                  </div>
                  <div className="activity-card">
                    <i className="fas fa-microscope activity-icon"></i>
                    <h5>پژوهش‌های علمی</h5>
                    <p className="text-muted mb-0">اجرای پروژه‌های تحقیقاتی در حوزه روانشناسی</p>
                  </div>
                  <div className="activity-card">
                    <i className="fas fa-users activity-icon"></i>
                    <h5>نشست‌های تخصصی</h5>
                    <p className="text-muted mb-0">برگزاری جلسات علمی و تبادل نظر متخصصان</p>
                  </div>
                  <div className="activity-card">
                    <i className="fas fa-hospital activity-icon"></i>
                    <h5>بازدید از بیمارستان‌ها</h5>
                    <p className="text-muted mb-0">بازدیدهای علمی از بیمارستان‌های روانی</p>
                  </div>
                </div>
              </Col>
              <Col lg={6}>
                <div className="content-image-wrapper">
                  <img 
                    src={getImagePath('IMG_20250811_112847_556.jpg')}
                    onError={handleImageError}
                    alt="آغاز فعالیت مؤسسه در سال ۱۳۸۸" 
                    className="content-image"
                    loading="lazy"
                  />
                </div>
              </Col>
            </Row>
          </div>
          
          {/* 1389 Collaboration */}
          <div className="timeline-section">
            <div className="timeline-year">۱۳۸۹ - همکاری با دانشگاه تهران</div>
            <Row className="align-items-center g-4">
              <Col lg={6} className="order-lg-2">
                <p className="mb-3">
                  با همکاری مؤسسه روان‌شناسی دانشگاه تهران از سال ۱۳۸۹، آزمون‌های خاص روان‌شناختی را برای برخی پژوهشگران فراهم کردیم تا توانسته باشیم در راستای اجرای پژوهش‌های علمی قدمی جدی برداشته باشیم.
                </p>
                <div className="activity-card">
                  <i className="fas fa-database activity-icon"></i>
                  <h5>بزرگترین بانک آزمون‌های روان‌شناختی</h5>
                  <p className="text-muted mb-0">ایجاد مجموعه‌ای جامع از ابزارهای تشخیصی و ارزیابی روانشناختی</p>
                </div>
              </Col>
              <Col lg={6} className="order-lg-1">
                <div className="content-image-wrapper">
                  <img 
                    src={getImagePath('IMG_20250811_112847_826.jpg')}
                    onError={handleImageError}
                    alt="همکاری با دانشگاه تهران" 
                    className="content-image"
                    loading="lazy"
                  />
                </div>
              </Col>
            </Row>
          </div>
          
          {/* 1396 Center Establishment */}
          <div className="timeline-section">
            <div className="timeline-year">۱۳۹۶ - تأسیس مرکز مشاوره سرمد</div>
            <Row className="align-items-center g-4">
              <Col lg={6}>
                <p className="mb-3">
                  از سال ۱۳۹۶، مرکز مشاوره و خدمات روا‌ن‌شناختی سرمد را تحت نظارت سازمان بهزیستی تأسیس کردیم تا بتوانیم در عرصه خدمات مشاوره و درمانی نیز فعالیت داشته باشیم.
                </p>
                <p className="mb-0">
                  در این راستا توانستیم با همکاری با درمانگران حرفه‌ای و متخصص به هزاران نفر از مراجعان و درمان‌جویان کمک شایانی انجام دهیم.
                </p>
              </Col>
              <Col lg={6}>
                <div className="content-image-wrapper">
                  <img 
                    src={getImagePath('IMG_20250811_112847_901.jpg')}
                    onError={handleImageError}
                    alt="تأسیس مرکز مشاوره سرمد" 
                    className="content-image"
                    loading="lazy"
                  />
                </div>
              </Col>
            </Row>
          </div>
        </Container>
      </section>

      {/* Achievements Section */}
      <section className="py-5 bg-light">
        <Container>
          <h2 className="section-title">دستاوردها و افتخارات</h2>
          
          <div className="collaboration-section">
            <div className="text-center mb-4">
              <i className="fas fa-award activity-icon"></i>
              <h3>نوآوری‌ها و اولین‌ها</h3>
            </div>
            <Row className="align-items-center g-4 mb-4">
              <Col lg={6}>
                <p className="mb-3">
                  مفتخر هستیم که توانسته‌ایم ابزارهای علمی روان‌شناختی را برای اولین بار در اصفهان رونمایی و صدها روان‌شناس و دانشجوی روان‌شناسی را در این راستا آموزش دهیم.
                </p>
                <p className="mb-0">
                  در حوزه آموزشی توانسته‌ایم با ایجاد بزرگترین اتاق آیینه یک طرفه اصفهان، برای سوپرویژن‌های تخصصی محیطی منحصربفرد طراحی کنیم تا دانشجویان روان‌شناسی بتوانند به صورت کاملاً حرفه‌ای از آزموزش‌های عملی بهره‌مند شوند.
                </p>
              </Col>
              <Col lg={6}>
                <div className="content-image-wrapper">
                  <img 
                    src={getImagePath('IMG_20251002_163910_364.jpg')}
                    onError={handleImageError}
                    alt="نوآوری‌ها و دستاوردهای مرکز مشاوره سرمد" 
                    className="content-image"
                    loading="lazy"
                  />
                </div>
              </Col>
            </Row>
          </div>
          
          {/* Educational Programs */}
          <div className="collaboration-section">
            <div className="text-center mb-4">
              <i className="fas fa-graduation-cap activity-icon"></i>
              <h3>برنامه‌های آموزشی عمومی</h3>
            </div>
            <Row className="align-items-center g-4">
              <Col lg={6} className="order-lg-2">
                <p className="mb-3">
                  در این میان از آموزش‌های روان‌شناسی کاربردی و علمی برای عموم جامعه غافل نبوده و ده‌ها دوره علمی عمومی برگزار نموده‌ایم:
                </p>
                <div className="collaboration-tags">
                  <span className="collaboration-tag">فرزندپروری</span>
                  <span className="collaboration-tag">مهارت‌های زندگی</span>
                  <span className="collaboration-tag">مهارت‌های زندگی مشترک</span>
                  <span className="collaboration-tag">آموزش پیش از ازدواج</span>
                  <span className="collaboration-tag">مهارت تنظیم هیجان</span>
                  <span className="collaboration-tag">توانمندسازی کودکان</span>
                </div>
              </Col>
              <Col lg={6} className="order-lg-1">
                <div className="content-image-wrapper">
                  <img 
                    src={getImagePath('photo_2024-10-08_17-24-42.jpg')}
                    onError={handleImageError}
                    alt="برنامه‌های آموزشی عمومی مرکز مشاوره سرمد" 
                    className="content-image"
                    loading="lazy"
                  />
                </div>
              </Col>
            </Row>
          </div>
        </Container>
      </section>

      {/* Professional Courses Section */}
      <section className="py-5">
        <Container>
          <h2 className="section-title">دوره‌های تخصصی برگزار شده</h2>
          
          {/* Image before courses list */}
          <Row className="mb-4">
            <Col>
              <div className="content-image-wrapper">
                <img 
                  src={getImagePath('photo_2025-05-05_13-26-18.jpg')}
                  onError={handleImageError} 
                  alt="دوره‌های تخصصی مرکز مشاوره سرمد" 
                  className="content-image-wide"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
          
          <div className="courses-section">
            <Row>
              <Col lg={6}>
                <div className="course-item">
                  <h5><i className="fas fa-child me-2 text-primary"></i>تربیت درمانگر کودک (مقدماتی - دوره بلند مدت)</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-user-graduate me-2 text-primary"></i>تربیت درمانگر کودک (پیشرفته - دوره بلند مدت)</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-brain me-2 text-primary"></i>تربیت درمانگر شناختی رفتاری (دوره بلند مدت)</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-mind-share me-2 text-primary"></i>تربیت درمانگر طرح‌واره درمانی (دوره بلند مدت)</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-clipboard-list me-2 text-primary"></i>رونمایی و آموزش تخصصی اجرا و تفسیر آزمون MMPI-2RF</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-cat me-2 text-primary"></i>رونمایی و آموزش تخصصی اجرا و تفسیر آزمون CAT-S</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-file-alt me-2 text-primary"></i>رونمایی و آموزش تخصصی اجرا و تفسیر آزمون MCMI-4</h5>
                </div>
              </Col>
              <Col lg={6}>
                <div className="course-item">
                  <h5><i className="fas fa-calculator me-2 text-primary"></i>آموزش تخصصی اجرا و تفسیر مقیاس هوش استفورد-بینه</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-puzzle-piece me-2 text-primary"></i>آموزش تخصصی اجرا و تفسیر وکسلر۴ و پیشرفته</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-image me-2 text-primary"></i>آموزش تخصصی اجرا و تفسیر آزمون TAT</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-users me-2 text-primary"></i>دوره تربیت مربی مهارت‌های زندگی کودکان</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-user-friends me-2 text-primary"></i>دوره تربیت مهارت زندگی نوجوانان</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-eye me-2 text-primary"></i>رونمایی و آموزش تخصصی اجرا و تفسیر تست هافبک</h5>
                </div>
                <div className="course-item">
                  <h5><i className="fas fa-memory me-2 text-primary"></i>آموزش تخصصی درمان حافظه فعال</h5>
                </div>
              </Col>
            </Row>
            
            <Row className="mt-3">
              <Col lg={6}>
                <div className="course-item">
                  <h5><i className="fas fa-running me-2 text-primary"></i>آموزش تخصصی و تربیت درمانگر اختلال بیش‌فعالی و نقص توجه</h5>
                </div>
              </Col>
              <Col lg={6}>
                <div className="course-item">
                  <h5><i className="fas fa-book-reader me-2 text-primary"></i>آموزش تخصصی و تربیت درمانگر اختلالات یادگیری</h5>
                </div>
              </Col>
            </Row>
          </div>
        </Container>
      </section>

      {/* Collaborations Section */}
      <section className="py-5 bg-light">
        <Container>
          <h2 className="section-title">همکاری‌ها و شراکت‌ها</h2>
          
          <div className="collaboration-section">
            <div className="text-center mb-4">
              <i className="fas fa-handshake activity-icon"></i>
              <h3>سازمان‌ها و مؤسسات همکار</h3>
            </div>
            <Row className="align-items-center g-4 mb-4">
              <Col lg={6}>
                <p className="mb-3">
                  در این سال‌ها با بسیاری از سازمان‌های دولتی و خصوصی، شرکت‌های تجاری، کارخانه‌ها،‌ مدارس، مهدکودک‌ها، خانه‌های کودک و خلاقیت همکاری داشته‌ایم.
                </p>
                <p className="mb-0">
                  در این راستا توانسته‌ایم از استخدام تا توانمندسازی کارمندان و همچنین آموزش و مشاوره به خانواده‌ها و اعضای آنها با این مجموعه‌ها همکاری داشته باشیم‌.
                </p>
              </Col>
              <Col lg={6}>
                <div className="content-image-wrapper">
                  <img 
                    src={getImagePath('20240725_165904.jpg')}
                    onError={handleImageError}
                    alt="همکاری‌های مرکز مشاوره سرمد" 
                    className="content-image"
                    loading="lazy"
                  />
                </div>
              </Col>
            </Row>
            
            <div className="collaboration-tags">
              <span className="collaboration-tag">سازمان‌های دولتی</span>
              <span className="collaboration-tag">شرکت‌های خصوصی</span>
              <span className="collaboration-tag">کارخانه‌ها</span>
              <span className="collaboration-tag">مدارس</span>
              <span className="collaboration-tag">مهدکودک‌ها</span>
              <span className="collaboration-tag">خانه‌های کودک و خلاقیت</span>
            </div>
          </div>
        </Container>
      </section>

      {/* Image Gallery Section */}
      <section className="py-5">
        <Container>
          <h2 className="section-title">گالری تصاویر</h2>
          <Row className="g-4">
            <Col md={4}>
              <div className="gallery-image-wrapper">
                <img 
                  src={getImagePath('IMG_20250811_112847_556.jpg')}
                  onError={handleImageError}
                  alt="فعالیت‌های مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="gallery-image-wrapper">
                <img 
                  src={getImagePath('IMG_20250811_112847_826.jpg')}
                  onError={handleImageError}
                  alt="کارگاه‌های آموزشی مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="gallery-image-wrapper">
                <img 
                  src={getImagePath('IMG_20250811_112847_901.jpg')}
                  onError={handleImageError}
                  alt="نشست‌های تخصصی مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="gallery-image-wrapper">
                <img 
                  src={getImagePath('IMG_20251002_163910_364.jpg')}
                  onError={handleImageError}
                  alt="دوره‌های آموزشی مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="gallery-image-wrapper">
                <img 
                  src={getImagePath('photo_2024-10-08_17-24-42.jpg')}
                  onError={handleImageError} 
                  alt="فعالیت‌های پژوهشی مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Quote Section */}
      <section className="quote-section">
        <Container>
          <div className="quote-text">
            "امیدواریم در این مسیر بتوانیم همچنان حرفه‌ای باقی بمانیم و در راستای اعتلای رشته روان‌شناسی علمی در کشور گام برداریم‌."
          </div>
          <p className="mt-3 mb-0"><strong>- مرکز مشاوره و خدمات روانشناسی سرمد</strong></p>
        </Container>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <Container>
          <h2 className="section-title">آمار و ارقام</h2>
          <Row>
            <Col md={3}>
              <div className="stat-item">
                <span className="stat-number">15+</span>
                <div className="stat-label">سال تجربه</div>
              </div>
            </Col>
            <Col md={3}>
              <div className="stat-item">
                <span className="stat-number">1000+</span>
                <div className="stat-label">مراجع درمان شده</div>
              </div>
            </Col>
            <Col md={3}>
              <div className="stat-item">
                <span className="stat-number">50+</span>
                <div className="stat-label">دوره تخصصی برگزار شده</div>
              </div>
            </Col>
            <Col md={3}>
              <div className="stat-item">
                <span className="stat-number">500+</span>
                <div className="stat-label">متخصص آموزش دیده</div>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Contact CTA */}
      <section className="py-5">
        <Container>
          <div className="collaboration-section text-center">
            <h3 className="mb-3">برای اطلاعات بیشتر و همکاری</h3>
            <p className="mb-4">
              با ما در تماس باشید تا بتوانیم در راستای اعتلای روانشناسی همکاری داشته باشیم
            </p>
            <div className="d-flex flex-wrap justify-content-center gap-3">
              <Link to="/coach" className="btn btn-primary btn-lg">
                <i className="fas fa-envelope me-2"></i>ارتباط با ما
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <style>{`
        .institute-hero {
          background: linear-gradient(135deg, var(--primary-color) 0%, #3498db 100%);
          color: white;
          padding: 4rem 0;
          position: relative;
          overflow: hidden;
        }
        
        .institute-hero::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.1);
        }
        
        .institute-content {
          position: relative;
          z-index: 2;
        }
        
        .institute-logo-large {
          width: 200px;
          height: 200px;
          object-fit: contain;
          background: rgba(255,255,255,0.95);
          border-radius: 20px;
          padding: 20px;
          box-shadow: 0 15px 35px rgba(0,0,0,0.3);
          margin-bottom: 2rem;
          border: 3px solid rgba(255,255,255,0.9);
        }
        
        .timeline-section {
          background: white;
          border-radius: 15px;
          padding: 2rem;
          box-shadow: 0 10px 30px rgba(0,0,0,0.1);
          margin-bottom: 2rem;
          transition: transform 0.3s ease;
        }
        
        .timeline-section:hover {
          transform: translateY(-5px);
        }
        
        .timeline-year {
          font-size: 1.8rem;
          font-weight: bold;
          color: var(--primary-color);
          margin-bottom: 1rem;
          display: flex;
          align-items: center;
        }
        
        .timeline-year::before {
          content: '';
          width: 20px;
          height: 20px;
          background: var(--primary-color);
          border-radius: 50%;
          margin-left: 1rem;
          box-shadow: 0 0 0 4px rgba(44, 90, 160, 0.2);
        }
        
        .activity-icon {
          font-size: 2.5rem;
          color: var(--primary-color);
          margin-bottom: 1rem;
        }
        
        .activities-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin: 3rem 0;
        }
        
        .activity-card {
          background: white;
          border-radius: 15px;
          padding: 2rem;
          box-shadow: 0 10px 30px rgba(0,0,0,0.1);
          border-left: 4px solid var(--primary-color);
          transition: transform 0.3s ease;
        }
        
        .activity-card:hover {
          transform: translateY(-5px);
        }
        
        .courses-section {
          background: var(--light-gray);
          border-radius: 15px;
          padding: 2rem;
          margin: 3rem 0;
        }
        
        .course-item {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          margin-bottom: 1rem;
          box-shadow: 0 5px 15px rgba(0,0,0,0.08);
          transition: transform 0.3s ease;
        }
        
        .course-item:hover {
          transform: translateX(10px);
        }
        
        .quote-section {
          background: var(--primary-color);
          color: white;
          padding: 3rem 0;
          text-align: center;
          margin: 3rem 0;
          border-radius: 15px;
        }
        
        .quote-text {
          font-size: 1.3rem;
          font-style: italic;
          line-height: 1.8;
          max-width: 800px;
          margin: 0 auto;
        }
        
        .collaboration-section {
          background: white;
          border-radius: 15px;
          padding: 2rem;
          box-shadow: 0 10px 30px rgba(0,0,0,0.1);
          margin: 3rem 0;
        }
        
        .collaboration-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin: 1rem 0;
        }
        
        .collaboration-tag {
          background: var(--primary-color);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-size: 0.9rem;
          font-weight: 500;
        }
        
        .stats-section {
          background: var(--light-gray);
          border-radius: 15px;
          padding: 3rem 2rem;
          margin: 3rem 0;
          text-align: center;
        }
        
        .stat-item {
          text-align: center;
          margin-bottom: 2rem;
        }
        
        .stat-number {
          font-size: 3rem;
          font-weight: bold;
          color: var(--primary-color);
          display: block;
        }
        
        .stat-label {
          font-size: 1.1rem;
          color: var(--text-color);
          margin-top: 0.5rem;
        }
        
        .content-image-wrapper {
          position: relative;
          overflow: hidden;
          border-radius: 15px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.15);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          background: #f8f9fa;
          padding: 0;
        }
        
        .content-image-wrapper:hover {
          transform: translateY(-5px);
          box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .content-image {
          width: 100%;
          height: auto;
          display: block;
          object-fit: cover;
          border-radius: 15px;
          transition: transform 0.5s ease;
        }
        
        .content-image-wrapper:hover .content-image {
          transform: scale(1.05);
        }
        
        .content-image-wide {
          width: 100%;
          height: auto;
          max-height: 500px;
          object-fit: cover;
          border-radius: 15px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.15);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .content-image-wide:hover {
          transform: translateY(-5px);
          box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .gallery-image-wrapper {
          position: relative;
          overflow: hidden;
          border-radius: 15px;
          box-shadow: 0 8px 25px rgba(0,0,0,0.12);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          background: #f8f9fa;
          aspect-ratio: 4/3;
        }
        
        .gallery-image-wrapper:hover {
          transform: translateY(-8px);
          box-shadow: 0 12px 35px rgba(0,0,0,0.18);
        }
        
        .gallery-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          border-radius: 15px;
          transition: transform 0.5s ease;
        }
        
        .gallery-image-wrapper:hover .gallery-image {
          transform: scale(1.1);
        }
        
        .section-title {
          font-size: 2.5rem;
          font-weight: bold;
          color: var(--primary-color);
          text-align: center;
          margin-bottom: 3rem;
          position: relative;
          padding-bottom: 1rem;
        }
        
        .section-title::after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 100px;
          height: 4px;
          background: linear-gradient(90deg, var(--primary-color), #3498db);
          border-radius: 2px;
        }
        
        @media (max-width: 768px) {
          .institute-logo-large {
            width: 150px;
            height: 150px;
          }
          
          .institute-hero {
            padding: 2rem 0;
          }
          
          .timeline-year {
            font-size: 1.5rem;
          }
          
          .stat-number {
            font-size: 2rem;
          }
          
          .section-title {
            font-size: 2rem;
            margin-bottom: 2rem;
          }
          
          .content-image-wrapper,
          .gallery-image-wrapper {
            margin-bottom: 1.5rem;
          }
          
          .content-image-wide {
            max-height: 300px;
          }
        }
      `}</style>
    </>
  );
};

export default AboutInstitute;
