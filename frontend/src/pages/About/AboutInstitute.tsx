import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

const AboutInstitute: React.FC = () => {
  // Helper function to get image path (handles space in directory name and Persian characters)
  const getImagePath = (filename: string): string => {
    // URL encode the space in directory name and the filename
    // Use encodeURIComponent to properly handle Persian characters
    const encodedFilename = encodeURIComponent(filename).replace(/'/g, '%27');
    return `/images/about%20institue/${encodedFilename}`;
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

      {/* Hero Section with Background Image */}
      <section className="institute-hero">
        <div className="hero-overlay"></div>
        <Container className="institute-content">
          <Row className="align-items-center">
            <Col lg={4} className="text-center mb-4 mb-lg-0">
              <div className="hero-logo-container">
                <img 
                  src="/images/1744027219152.png" 
                  alt="مرکز مشاوره و خدمات روانشناسی سرمد" 
                  className="institute-logo-large"
                  loading="eager"
                />
              </div>
            </Col>
            <Col lg={8}>
              <h1 className="display-3 mb-3 fw-bold">مرکز مشاوره و خدمات روانشناسی سرمد</h1>
              <h3 className="mb-4 fw-normal">بیش از ۱۵ سال تجربه در ارائه خدمات روانشناسی</h3>
              <p className="lead mb-0">
                از سال ۱۳۸۸ با مؤسسه علمی پژوهشی روان‌شناسی فعالیت خودمان را آغاز کردیم و در طول این سال‌ها توانسته‌ایم خدمات متنوع و با کیفیتی را ارائه دهیم.
              </p>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Introduction Image Gallery - Enhanced */}
      <section className="py-5 intro-gallery-section">
        <Container>
          <Row className="g-4">
            <Col md={4}>
              <div className="intro-image-card">
                <div className="image-overlay-text">
                  <h5>فعالیت‌های حرفه‌ای</h5>
                </div>
                <img 
                  src={getImagePath('20240725_165904.jpg')}
                  onError={handleImageError}
                  alt="فعالیت‌های مرکز مشاوره سرمد" 
                  className="intro-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="intro-image-card">
                <div className="image-overlay-text">
                  <h5>کارگاه‌های آموزشی</h5>
                </div>
                <img 
                  src={getImagePath('20240726_095433.jpg')}
                  onError={handleImageError} 
                  alt="کارگاه‌های آموزشی مرکز مشاوره سرمد" 
                  className="intro-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="intro-image-card">
                <div className="image-overlay-text">
                  <h5>نشست‌های تخصصی</h5>
                </div>
                <img 
                  src={getImagePath('3_20250125_115351_0002.png')}
                  onError={handleImageError}
                  alt="نشست‌های تخصصی مرکز مشاوره سرمد" 
                  className="intro-image"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Timeline Section - Enhanced with More Images */}
      <section className="py-5 timeline-main-section">
        <Container>
          <h2 className="section-title">تاریخچه مؤسسه</h2>
          
          {/* 1388 Start - Enhanced */}
          <div className="timeline-section enhanced">
            <div className="timeline-header">
              <div className="timeline-year">۱۳۸۸ - آغاز فعالیت</div>
              <div className="timeline-line"></div>
            </div>
            <Row className="align-items-center g-4">
              <Col lg={6}>
                <div className="timeline-content">
                  <p className="timeline-description mb-4">
                    از سال ۱۳۸۸ با مؤسسه علمی پژوهشی روان‌شناسی فعالیت خودمان را آغاز کردیم.
                  </p>
                  <div className="activities-grid-enhanced">
                    <div className="activity-card-enhanced">
                      <div className="activity-image-wrapper">
                        <img 
                          src={getImagePath('4_20250125_115351_0003.png')}
                          onError={handleImageError}
                          alt="کارگاه‌های تخصصی" 
                          className="activity-image"
                          loading="lazy"
                        />
                      </div>
                      <div className="activity-content">
                        <i className="fas fa-chalkboard-teacher activity-icon-small"></i>
                        <h5>کارگاه‌های تخصصی و عمومی</h5>
                        <p className="text-muted mb-0">برگزاری دوره‌های آموزشی متنوع برای متخصصان و عموم</p>
                      </div>
                    </div>
                    <div className="activity-card-enhanced">
                      <div className="activity-image-wrapper">
                        <img 
                          src={getImagePath('5_20250125_115351_0004.png')}
                          onError={handleImageError}
                          alt="پژوهش‌های علمی" 
                          className="activity-image"
                          loading="lazy"
                        />
                      </div>
                      <div className="activity-content">
                        <i className="fas fa-microscope activity-icon-small"></i>
                        <h5>پژوهش‌های علمی</h5>
                        <p className="text-muted mb-0">اجرای پروژه‌های تحقیقاتی در حوزه روانشناسی</p>
                      </div>
                    </div>
                    <div className="activity-card-enhanced">
                      <div className="activity-image-wrapper">
                        <img 
                          src={getImagePath('6_20250125_115351_0005.png')}
                          onError={handleImageError}
                          alt="نشست‌های تخصصی" 
                          className="activity-image"
                          loading="lazy"
                        />
                      </div>
                      <div className="activity-content">
                        <i className="fas fa-users activity-icon-small"></i>
                        <h5>نشست‌های تخصصی</h5>
                        <p className="text-muted mb-0">برگزاری جلسات علمی و تبادل نظر متخصصان</p>
                      </div>
                    </div>
                  </div>
                </div>
              </Col>
              <Col lg={6}>
                <div className="timeline-image-container">
                  <div className="content-image-wrapper enhanced">
                    <img 
                      src={getImagePath('IMG_20250811_112847_556.jpg')}
                      onError={handleImageError}
                      alt="آغاز فعالیت مؤسسه در سال ۱۳۸۸" 
                      className="content-image"
                      loading="lazy"
                    />
                  </div>
                  <div className="image-caption">
                    <p className="mb-0">آغاز فعالیت مؤسسه علمی پژوهشی</p>
                  </div>
                </div>
              </Col>
            </Row>
          </div>
          
          {/* 1389 Collaboration - Enhanced */}
          <div className="timeline-section enhanced">
            <div className="timeline-header">
              <div className="timeline-year">۱۳۸۹ - همکاری با دانشگاه تهران</div>
              <div className="timeline-line"></div>
            </div>
            <Row className="align-items-center g-4">
              <Col lg={6} className="order-lg-2">
                <div className="timeline-content">
                  <p className="timeline-description mb-4">
                    با همکاری مؤسسه روان‌شناسی دانشگاه تهران از سال ۱۳۸۹، آزمون‌های خاص روان‌شناختی را برای برخی پژوهشگران فراهم کردیم تا توانسته باشیم در راستای اجرای پژوهش‌های علمی قدمی جدی برداشته باشیم.
                  </p>
                  <div className="activity-card-enhanced featured">
                    <div className="activity-image-wrapper">
                      <img 
                        src={getImagePath('Copy_of_کارگاه_وکسلر_۵_با_حضور_جناب_آقای_دکتر_کامکاری_و_سرکار_خانم.png')}
                        onError={handleImageError}
                        alt="بانک آزمون‌های روان‌شناختی" 
                        className="activity-image"
                        loading="lazy"
                      />
                    </div>
                    <div className="activity-content">
                      <i className="fas fa-database activity-icon-small"></i>
                      <h5>بزرگترین بانک آزمون‌های روان‌شناختی</h5>
                      <p className="text-muted mb-0">ایجاد مجموعه‌ای جامع از ابزارهای تشخیصی و ارزیابی روانشناختی</p>
                    </div>
                  </div>
                </div>
              </Col>
              <Col lg={6} className="order-lg-1">
                <div className="timeline-image-container">
                  <div className="content-image-wrapper enhanced">
                    <img 
                      src={getImagePath('Copy_of_Copy_of_کارگاه_وکسلر_۵_با_حضور_جناب_آقای_دکتر_کامکاری_و.jpg')}
                      onError={handleImageError}
                      alt="همکاری با دانشگاه تهران - کارگاه وکسلر" 
                      className="content-image"
                      loading="lazy"
                    />
                  </div>
                  <div className="image-caption">
                    <p className="mb-0">کارگاه وکسلر ۵ با حضور دکتر کامکاری</p>
                  </div>
                </div>
              </Col>
            </Row>
          </div>
          
          {/* 1396 Center Establishment - Enhanced */}
          <div className="timeline-section enhanced">
            <div className="timeline-header">
              <div className="timeline-year">۱۳۹۶ - تأسیس مرکز مشاوره سرمد</div>
              <div className="timeline-line"></div>
            </div>
            <Row className="align-items-center g-4">
              <Col lg={6}>
                <div className="timeline-content">
                  <p className="timeline-description mb-3">
                    از سال ۱۳۹۶، مرکز مشاوره و خدمات روان‌شناختی سرمد را تحت نظارت سازمان بهزیستی تأسیس کردیم تا بتوانیم در عرصه خدمات مشاوره و درمانی نیز فعالیت داشته باشیم.
                  </p>
                  <p className="timeline-description mb-0">
                    در این راستا توانستیم با همکاری با درمانگران حرفه‌ای و متخصص به هزاران نفر از مراجعان و درمان‌جویان کمک شایانی انجام دهیم.
                  </p>
                </div>
              </Col>
              <Col lg={6}>
                <div className="timeline-image-container">
                  <div className="content-image-wrapper enhanced">
                    <img 
                      src={getImagePath('IMG_20250811_112847_901.jpg')}
                      onError={handleImageError}
                      alt="تأسیس مرکز مشاوره سرمد" 
                      className="content-image"
                      loading="lazy"
                    />
                  </div>
                  <div className="image-caption">
                    <p className="mb-0">مرکز مشاوره و خدمات روان‌شناختی سرمد</p>
                  </div>
                </div>
              </Col>
            </Row>
          </div>
        </Container>
      </section>

      {/* Achievements Section - Enhanced with More Images */}
      <section className="py-5 bg-light achievements-section">
        <Container>
          <h2 className="section-title">دستاوردها و افتخارات</h2>
          
          <div className="collaboration-section enhanced">
            <div className="text-center mb-5">
              <i className="fas fa-award activity-icon-large"></i>
              <h3 className="mt-3">نوآوری‌ها و اولین‌ها</h3>
            </div>
            <Row className="align-items-center g-4 mb-4">
              <Col lg={6}>
                <div className="achievement-content">
                  <p className="mb-3">
                    مفتخر هستیم که توانسته‌ایم ابزارهای علمی روان‌شناختی را برای اولین بار در اصفهان رونمایی و صدها روان‌شناس و دانشجوی روان‌شناسی را در این راستا آموزش دهیم.
                  </p>
                  <p className="mb-0">
                    در حوزه آموزشی توانسته‌ایم با ایجاد بزرگترین اتاق آیینه یک طرفه اصفهان، برای سوپرویژن‌های تخصصی محیطی منحصربفرد طراحی کنیم تا دانشجویان روان‌شناسی بتوانند به صورت کاملاً حرفه‌ای از آموزش‌های عملی بهره‌مند شوند.
                  </p>
                </div>
              </Col>
              <Col lg={6}>
                <Row className="g-3">
                  <Col md={6}>
                    <div className="achievement-image-card">
                      <img 
                        src={getImagePath('IMG_20251002_163910_364.jpg')}
                        onError={handleImageError}
                        alt="نوآوری‌ها و دستاوردهای مرکز مشاوره سرمد" 
                        className="achievement-image"
                        loading="lazy"
                      />
                    </div>
                  </Col>
                  <Col md={6}>
                    <div className="achievement-image-card">
                      <img 
                        src={getImagePath('8_20250125_115351_0007.png')}
                        onError={handleImageError}
                        alt="اتاق آیینه یک طرفه" 
                        className="achievement-image"
                        loading="lazy"
                      />
                    </div>
                  </Col>
                </Row>
              </Col>
            </Row>
          </div>
          
          {/* Educational Programs - Enhanced */}
          <div className="collaboration-section enhanced mt-5">
            <div className="text-center mb-5">
              <i className="fas fa-graduation-cap activity-icon-large"></i>
              <h3 className="mt-3">برنامه‌های آموزشی عمومی</h3>
            </div>
            <Row className="align-items-center g-4">
              <Col lg={6} className="order-lg-2">
                <div className="achievement-content">
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
                </div>
              </Col>
              <Col lg={6} className="order-lg-1">
                <div className="achievement-image-card large">
                  <img 
                    src={getImagePath('photo_2024-10-08_17-24-42.jpg')}
                    onError={handleImageError}
                    alt="برنامه‌های آموزشی عمومی مرکز مشاوره سرمد" 
                    className="achievement-image"
                    loading="lazy"
                  />
                </div>
              </Col>
            </Row>
          </div>
        </Container>
      </section>

      {/* Professional Courses Section - Enhanced with Images */}
      <section className="py-5 courses-main-section">
        <Container>
          <h2 className="section-title">دوره‌های تخصصی برگزار شده</h2>
          
          {/* Image Gallery before courses */}
          <Row className="mb-5 g-3">
            <Col md={6}>
              <div className="course-header-image">
                <img 
                  src={getImagePath('photo_2025-05-05_13-26-18.jpg')}
                  onError={handleImageError} 
                  alt="دوره‌های تخصصی مرکز مشاوره سرمد" 
                  className="course-header-img"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={6}>
              <div className="course-header-image">
                <img 
                  src={getImagePath('9_20250125_115352_0008.png')}
                  onError={handleImageError} 
                  alt="کارگاه‌های تخصصی" 
                  className="course-header-img"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
          
          <div className="courses-section enhanced">
            <Row>
              <Col lg={6}>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-child"></i>
                  </div>
                  <div className="course-content">
                    <h5>تربیت درمانگر کودک (مقدماتی - دوره بلند مدت)</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-user-graduate"></i>
                  </div>
                  <div className="course-content">
                    <h5>تربیت درمانگر کودک (پیشرفته - دوره بلند مدت)</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-brain"></i>
                  </div>
                  <div className="course-content">
                    <h5>تربیت درمانگر شناختی رفتاری (دوره بلند مدت)</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-mind-share"></i>
                  </div>
                  <div className="course-content">
                    <h5>تربیت درمانگر طرح‌واره درمانی (دوره بلند مدت)</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-clipboard-list"></i>
                  </div>
                  <div className="course-content">
                    <h5>رونمایی و آموزش تخصصی اجرا و تفسیر آزمون MMPI-2RF</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-cat"></i>
                  </div>
                  <div className="course-content">
                    <h5>رونمایی و آموزش تخصصی اجرا و تفسیر آزمون CAT-S</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-file-alt"></i>
                  </div>
                  <div className="course-content">
                    <h5>رونمایی و آموزش تخصصی اجرا و تفسیر آزمون MCMI-4</h5>
                  </div>
                </div>
              </Col>
              <Col lg={6}>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-calculator"></i>
                  </div>
                  <div className="course-content">
                    <h5>آموزش تخصصی اجرا و تفسیر مقیاس هوش استفورد-بینه</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-puzzle-piece"></i>
                  </div>
                  <div className="course-content">
                    <h5>آموزش تخصصی اجرا و تفسیر وکسلر۴ و پیشرفته</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-image"></i>
                  </div>
                  <div className="course-content">
                    <h5>آموزش تخصصی اجرا و تفسیر آزمون TAT</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-users"></i>
                  </div>
                  <div className="course-content">
                    <h5>دوره تربیت مربی مهارت‌های زندگی کودکان</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-user-friends"></i>
                  </div>
                  <div className="course-content">
                    <h5>دوره تربیت مهارت زندگی نوجوانان</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-eye"></i>
                  </div>
                  <div className="course-content">
                    <h5>رونمایی و آموزش تخصصی اجرا و تفسیر تست هافبک</h5>
                  </div>
                </div>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-memory"></i>
                  </div>
                  <div className="course-content">
                    <h5>آموزش تخصصی درمان حافظه فعال</h5>
                  </div>
                </div>
              </Col>
            </Row>
            
            <Row className="mt-4">
              <Col lg={6}>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-running"></i>
                  </div>
                  <div className="course-content">
                    <h5>آموزش تخصصی و تربیت درمانگر اختلال بیش‌فعالی و نقص توجه</h5>
                  </div>
                </div>
              </Col>
              <Col lg={6}>
                <div className="course-item-enhanced">
                  <div className="course-icon-wrapper">
                    <i className="fas fa-book-reader"></i>
                  </div>
                  <div className="course-content">
                    <h5>آموزش تخصصی و تربیت درمانگر اختلالات یادگیری</h5>
                  </div>
                </div>
              </Col>
            </Row>
          </div>
        </Container>
      </section>

      {/* Collaborations Section - Enhanced */}
      <section className="py-5 bg-light collaborations-main-section">
        <Container>
          <h2 className="section-title">همکاری‌ها و شراکت‌ها</h2>
          
          <div className="collaboration-section enhanced">
            <div className="text-center mb-5">
              <i className="fas fa-handshake activity-icon-large"></i>
              <h3 className="mt-3">سازمان‌ها و مؤسسات همکار</h3>
            </div>
            <Row className="align-items-center g-4 mb-4">
              <Col lg={6}>
                <div className="achievement-content">
                  <p className="mb-3">
                    در این سال‌ها با بسیاری از سازمان‌های دولتی و خصوصی، شرکت‌های تجاری، کارخانه‌ها،‌ مدارس، مهدکودک‌ها، خانه‌های کودک و خلاقیت همکاری داشته‌ایم.
                  </p>
                  <p className="mb-0">
                    در این راستا توانسته‌ایم از استخدام تا توانمندسازی کارمندان و همچنین آموزش و مشاوره به خانواده‌ها و اعضای آنها با این مجموعه‌ها همکاری داشته باشیم‌.
                  </p>
                </div>
              </Col>
              <Col lg={6}>
                <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '300px' }}>
                  <div className="collaboration-image-card" style={{ maxWidth: '400px', width: '100%', minHeight: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'white' }}>
                    <img 
                      src="/images/tehran-university-logo.png"
                      onError={handleImageError}
                      alt="دانشگاه تهران" 
                      style={{ 
                        maxWidth: '100%', 
                        maxHeight: '100%', 
                        objectFit: 'contain', 
                        padding: '2rem',
                        width: 'auto',
                        height: 'auto'
                      }}
                      loading="lazy"
                    />
                  </div>
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

      {/* Enhanced Image Gallery Section */}
      <section className="py-5 gallery-main-section">
        <Container>
          <h2 className="section-title">گالری تصاویر</h2>
          <Row className="g-4">
            <Col md={4}>
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>فعالیت‌های حرفه‌ای</span>
                </div>
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
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>کارگاه‌های آموزشی</span>
                </div>
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
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>نشست‌های تخصصی</span>
                </div>
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
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>دوره‌های آموزشی</span>
                </div>
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
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>فعالیت‌های پژوهشی</span>
                </div>
                <img 
                  src={getImagePath('photo_2024-10-08_17-24-42.jpg')}
                  onError={handleImageError} 
                  alt="فعالیت‌های پژوهشی مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>کارگاه‌های تخصصی</span>
                </div>
                <img 
                  src={getImagePath('11_20250125_115352_0010.png')}
                  onError={handleImageError}
                  alt="فعالیت‌های مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>آموزش‌های عملی</span>
                </div>
                <img 
                  src={getImagePath('12_20250125_115352_0011.png')}
                  onError={handleImageError}
                  alt="کارگاه‌های آموزشی مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>نشست‌های علمی</span>
                </div>
                <img 
                  src={getImagePath('13_20250125_115352_0012.png')}
                  onError={handleImageError}
                  alt="نشست‌های تخصصی مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={4}>
              <div className="gallery-image-wrapper enhanced">
                <div className="gallery-overlay">
                  <span>دوره‌های تخصصی</span>
                </div>
                <img 
                  src={getImagePath('14_20250125_115352_0013.png')}
                  onError={handleImageError}
                  alt="دوره‌های آموزشی مرکز مشاوره سرمد" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Quote Section - Enhanced */}
      <section className="quote-section enhanced">
        <Container>
          <div className="quote-icon-wrapper">
            <i className="fas fa-quote-right"></i>
          </div>
          <div className="quote-text">
            "امیدواریم در این مسیر بتوانیم همچنان حرفه‌ای باقی بمانیم و در راستای اعتلای رشته روان‌شناسی علمی در کشور گام برداریم‌."
          </div>
          <p className="mt-4 mb-0 quote-author"><strong>- مرکز مشاوره و خدمات روانشناسی سرمد</strong></p>
        </Container>
      </section>

      {/* Stats Section - Enhanced */}
      <section className="stats-section enhanced">
        <Container>
          <h2 className="section-title">آمار و ارقام</h2>
          <Row>
            <Col md={3} className="mb-4 mb-md-0">
              <div className="stat-item-enhanced">
                <div className="stat-icon-wrapper">
                  <i className="fas fa-calendar-alt"></i>
                </div>
                <span className="stat-number">15+</span>
                <div className="stat-label">سال تجربه</div>
              </div>
            </Col>
            <Col md={3} className="mb-4 mb-md-0">
              <div className="stat-item-enhanced">
                <div className="stat-icon-wrapper">
                  <i className="fas fa-users"></i>
                </div>
                <span className="stat-number">1000+</span>
                <div className="stat-label">مراجع درمان شده</div>
              </div>
            </Col>
            <Col md={3} className="mb-4 mb-md-0">
              <div className="stat-item-enhanced">
                <div className="stat-icon-wrapper">
                  <i className="fas fa-graduation-cap"></i>
                </div>
                <span className="stat-number">50+</span>
                <div className="stat-label">دوره تخصصی برگزار شده</div>
              </div>
            </Col>
            <Col md={3}>
              <div className="stat-item-enhanced">
                <div className="stat-icon-wrapper">
                  <i className="fas fa-user-md"></i>
                </div>
                <span className="stat-number">500+</span>
                <div className="stat-label">متخصص آموزش دیده</div>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Contact CTA - Enhanced */}
      <section className="py-5 contact-cta-section">
        <Container>
          <div className="collaboration-section enhanced text-center">
            <div className="cta-icon-wrapper mb-4">
              <i className="fas fa-envelope-open-text"></i>
            </div>
            <h3 className="mb-3">برای اطلاعات بیشتر و همکاری</h3>
            <p className="mb-4">
              با ما در تماس باشید تا بتوانیم در راستای اعتلای روانشناسی همکاری داشته باشیم
            </p>
            <div className="d-flex flex-wrap justify-content-center gap-3">
              <Link to="/coach" className="btn btn-primary btn-lg cta-button">
                <i className="fas fa-envelope me-2"></i>ارتباط با ما
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <style>{`
        /* Hero Section Enhanced */
        .institute-hero {
          background: linear-gradient(135deg, var(--primary-color) 0%, #2c5aa0 50%, #3498db 100%);
          color: white;
          padding: 5rem 0;
          position: relative;
          overflow: hidden;
        }
        
        .hero-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.15);
          z-index: 1;
        }
        
        .institute-content {
          position: relative;
          z-index: 2;
        }
        
        .hero-logo-container {
          position: relative;
          display: inline-block;
        }
        
        .institute-logo-large {
          width: 220px;
          height: 220px;
          object-fit: contain;
          background: rgba(255,255,255,0.98);
          border-radius: 25px;
          padding: 25px;
          box-shadow: 0 20px 50px rgba(0,0,0,0.4);
          border: 4px solid rgba(255,255,255,0.95);
          transition: transform 0.3s ease;
        }
        
        .institute-logo-large:hover {
          transform: scale(1.05);
        }
        
        /* Introduction Gallery Enhanced */
        .intro-gallery-section {
          background: linear-gradient(to bottom, #f8f9fa 0%, #ffffff 100%);
        }
        
        .intro-image-card {
          position: relative;
          overflow: hidden;
          border-radius: 20px;
          box-shadow: 0 15px 40px rgba(0,0,0,0.15);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          height: 300px;
        }
        
        .intro-image-card:hover {
          transform: translateY(-10px);
          box-shadow: 0 20px 50px rgba(0,0,0,0.25);
        }
        
        .intro-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s ease;
        }
        
        .intro-image-card:hover .intro-image {
          transform: scale(1.1);
        }
        
        .image-overlay-text {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
          color: white;
          padding: 2rem 1.5rem 1rem;
          z-index: 2;
        }
        
        .image-overlay-text h5 {
          margin: 0;
          font-weight: 600;
        }
        
        /* Timeline Section Enhanced */
        .timeline-main-section {
          background: #ffffff;
        }
        
        .timeline-section.enhanced {
          background: white;
          border-radius: 20px;
          padding: 3rem;
          box-shadow: 0 15px 40px rgba(0,0,0,0.1);
          margin-bottom: 3rem;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          border: 1px solid rgba(44, 90, 160, 0.1);
        }
        
        .timeline-section.enhanced:hover {
          transform: translateY(-8px);
          box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        }
        
        .timeline-header {
          display: flex;
          align-items: center;
          margin-bottom: 2rem;
          gap: 1rem;
        }
        
        .timeline-year {
          font-size: 2rem;
          font-weight: bold;
          color: var(--primary-color);
          white-space: nowrap;
        }
        
        .timeline-line {
          flex: 1;
          height: 3px;
          background: linear-gradient(90deg, var(--primary-color), transparent);
          border-radius: 2px;
        }
        
        .timeline-content {
          padding: 1rem 0;
        }
        
        .timeline-description {
          font-size: 1.1rem;
          line-height: 1.9;
          color: #333;
        }
        
        .timeline-image-container {
          position: relative;
        }
        
        .content-image-wrapper.enhanced {
          position: relative;
          overflow: hidden;
          border-radius: 20px;
          box-shadow: 0 15px 40px rgba(0,0,0,0.2);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          background: #f8f9fa;
        }
        
        .content-image-wrapper.enhanced:hover {
          transform: translateY(-8px);
          box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }
        
        .content-image {
          width: 100%;
          height: auto;
          display: block;
          object-fit: cover;
          border-radius: 20px;
          transition: transform 0.5s ease;
        }
        
        .content-image-wrapper.enhanced:hover .content-image {
          transform: scale(1.08);
        }
        
        .image-caption {
          margin-top: 1rem;
          text-align: center;
          color: #666;
          font-style: italic;
        }
        
        /* Activities Grid Enhanced */
        .activities-grid-enhanced {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1.5rem;
          margin-top: 2rem;
        }
        
        .activity-card-enhanced {
          background: white;
          border-radius: 15px;
          padding: 0;
          box-shadow: 0 8px 25px rgba(0,0,0,0.1);
          border: 1px solid rgba(44, 90, 160, 0.1);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          overflow: hidden;
        }
        
        .activity-card-enhanced:hover {
          transform: translateY(-8px);
          box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        
        .activity-card-enhanced.featured {
          border: 2px solid var(--primary-color);
        }
        
        .activity-image-wrapper {
          width: 100%;
          height: 180px;
          overflow: hidden;
          background: #f8f9fa;
        }
        
        .activity-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s ease;
        }
        
        .activity-card-enhanced:hover .activity-image {
          transform: scale(1.1);
        }
        
        .activity-content {
          padding: 1.5rem;
        }
        
        .activity-icon-small {
          font-size: 1.8rem;
          color: var(--primary-color);
          margin-bottom: 0.5rem;
          display: block;
        }
        
        .activity-content h5 {
          margin-bottom: 0.5rem;
          color: #333;
        }
        
        /* Achievements Section */
        .achievements-section {
          background: linear-gradient(to bottom, #f8f9fa 0%, #ffffff 100%);
        }
        
        .activity-icon-large {
          font-size: 4rem;
          color: var(--primary-color);
          margin-bottom: 1rem;
        }
        
        .achievement-content {
          padding: 1rem 0;
        }
        
        .achievement-content p {
          font-size: 1.1rem;
          line-height: 1.9;
          color: #333;
        }
        
        .achievement-image-card {
          position: relative;
          overflow: hidden;
          border-radius: 15px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.15);
          transition: transform 0.3s ease;
          height: 250px;
        }
        
        .achievement-image-card.large {
          height: 100%;
          min-height: 400px;
        }
        
        .achievement-image-card:hover {
          transform: translateY(-5px);
        }
        
        .achievement-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s ease;
        }
        
        .achievement-image-card:hover .achievement-image {
          transform: scale(1.1);
        }
        
        /* Courses Section Enhanced */
        .courses-main-section {
          background: #ffffff;
        }
        
        .course-header-image {
          position: relative;
          overflow: hidden;
          border-radius: 20px;
          box-shadow: 0 15px 40px rgba(0,0,0,0.15);
          height: 300px;
          transition: transform 0.3s ease;
        }
        
        .course-header-image:hover {
          transform: translateY(-5px);
        }
        
        .course-header-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s ease;
        }
        
        .course-header-image:hover .course-header-img {
          transform: scale(1.1);
        }
        
        .courses-section.enhanced {
          background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
          border-radius: 20px;
          padding: 3rem;
          margin: 3rem 0;
          box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .course-item-enhanced {
          background: white;
          border-radius: 15px;
          padding: 1.5rem;
          margin-bottom: 1rem;
          box-shadow: 0 5px 20px rgba(0,0,0,0.08);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          display: flex;
          align-items: center;
          gap: 1rem;
          border-right: 4px solid var(--primary-color);
        }
        
        .course-item-enhanced:hover {
          transform: translateX(10px);
          box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        
        .course-icon-wrapper {
          width: 50px;
          height: 50px;
          background: linear-gradient(135deg, var(--primary-color), #3498db);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 1.5rem;
          flex-shrink: 0;
        }
        
        .course-content h5 {
          margin: 0;
          color: #333;
          font-size: 1rem;
        }
        
        /* Collaborations Section */
        .collaborations-main-section {
          background: linear-gradient(to bottom, #ffffff 0%, #f8f9fa 100%);
        }
        
        .collaboration-image-card {
          position: relative;
          overflow: hidden;
          border-radius: 15px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.15);
          transition: transform 0.3s ease;
          height: 250px;
        }
        
        .collaboration-image-card:hover {
          transform: translateY(-5px);
        }
        
        .collaboration-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s ease;
        }
        
        .collaboration-image-card:hover .collaboration-image {
          transform: scale(1.1);
        }
        
        /* Gallery Enhanced */
        .gallery-main-section {
          background: #ffffff;
        }
        
        .gallery-image-wrapper.enhanced {
          position: relative;
          overflow: hidden;
          border-radius: 20px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.15);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          background: #f8f9fa;
          aspect-ratio: 4/3;
        }
        
        .gallery-image-wrapper.enhanced:hover {
          transform: translateY(-10px);
          box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .gallery-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          border-radius: 20px;
          transition: transform 0.5s ease;
        }
        
        .gallery-image-wrapper.enhanced:hover .gallery-image {
          transform: scale(1.15);
        }
        
        .gallery-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(to top, rgba(44, 90, 160, 0.85), transparent);
          display: flex;
          align-items: flex-end;
          padding: 1.5rem;
          opacity: 0;
          transition: opacity 0.3s ease;
          z-index: 2;
        }
        
        .gallery-image-wrapper.enhanced:hover .gallery-overlay {
          opacity: 1;
        }
        
        .gallery-overlay span {
          color: white;
          font-weight: 600;
          font-size: 1.1rem;
        }
        
        /* Quote Section Enhanced */
        .quote-section.enhanced {
          background: linear-gradient(135deg, var(--primary-color) 0%, #2c5aa0 50%, #3498db 100%);
          color: white;
          padding: 5rem 0;
          text-align: center;
          margin: 4rem 0;
          border-radius: 0;
          position: relative;
          overflow: hidden;
        }
        
        .quote-section.enhanced::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.1);
        }
        
        .quote-icon-wrapper {
          font-size: 4rem;
          opacity: 0.3;
          margin-bottom: 2rem;
          position: relative;
          z-index: 2;
        }
        
        .quote-text {
          font-size: 1.5rem;
          font-style: italic;
          line-height: 2;
          max-width: 900px;
          margin: 0 auto;
          position: relative;
          z-index: 2;
        }
        
        .quote-author {
          position: relative;
          z-index: 2;
          font-size: 1.2rem;
        }
        
        /* Stats Section Enhanced */
        .stats-section.enhanced {
          background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
          border-radius: 20px;
          padding: 4rem 2rem;
          margin: 4rem 0;
          text-align: center;
          box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .stat-item-enhanced {
          text-align: center;
          padding: 2rem;
          background: white;
          border-radius: 15px;
          box-shadow: 0 8px 25px rgba(0,0,0,0.1);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          height: 100%;
        }
        
        .stat-item-enhanced:hover {
          transform: translateY(-10px);
          box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }
        
        .stat-icon-wrapper {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, var(--primary-color), #3498db);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1.5rem;
          color: white;
          font-size: 2rem;
        }
        
        .stat-number {
          font-size: 3.5rem;
          font-weight: bold;
          color: var(--primary-color);
          display: block;
          margin-bottom: 0.5rem;
        }
        
        .stat-label {
          font-size: 1.2rem;
          color: #666;
          margin-top: 0.5rem;
        }
        
        /* Contact CTA Enhanced */
        .contact-cta-section {
          background: linear-gradient(to bottom, #ffffff 0%, #f8f9fa 100%);
        }
        
        .cta-icon-wrapper {
          font-size: 4rem;
          color: var(--primary-color);
        }
        
        .cta-button {
          padding: 1rem 2.5rem;
          font-size: 1.1rem;
          border-radius: 50px;
          box-shadow: 0 8px 25px rgba(44, 90, 160, 0.3);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .cta-button:hover {
          transform: translateY(-3px);
          box-shadow: 0 12px 35px rgba(44, 90, 160, 0.4);
        }
        
        /* Collaboration Tags */
        .collaboration-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          margin: 2rem 0 0;
        }
        
        .collaboration-tag {
          background: linear-gradient(135deg, var(--primary-color), #3498db);
          color: white;
          padding: 0.75rem 1.5rem;
          border-radius: 25px;
          font-size: 1rem;
          font-weight: 500;
          box-shadow: 0 4px 15px rgba(44, 90, 160, 0.2);
          transition: transform 0.3s ease;
        }
        
        .collaboration-tag:hover {
          transform: translateY(-3px);
        }
        
        /* Section Title */
        .section-title {
          font-size: 2.8rem;
          font-weight: bold;
          color: var(--primary-color);
          text-align: center;
          margin-bottom: 4rem;
          position: relative;
          padding-bottom: 1.5rem;
        }
        
        .section-title::after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 120px;
          height: 5px;
          background: linear-gradient(90deg, var(--primary-color), #3498db);
          border-radius: 3px;
        }
        
        /* Responsive Design */
        @media (max-width: 992px) {
          .institute-logo-large {
            width: 180px;
            height: 180px;
          }
          
          .institute-hero {
            padding: 3rem 0;
          }
          
          .timeline-year {
            font-size: 1.6rem;
          }
          
          .stat-number {
            font-size: 2.5rem;
          }
          
          .section-title {
            font-size: 2.2rem;
            margin-bottom: 3rem;
          }
          
          .activities-grid-enhanced {
            grid-template-columns: 1fr;
          }
          
          .quote-text {
            font-size: 1.2rem;
          }
        }
        
        @media (max-width: 768px) {
          .institute-logo-large {
            width: 150px;
            height: 150px;
          }
          
          .institute-hero {
            padding: 2.5rem 0;
          }
          
          .timeline-section.enhanced {
            padding: 2rem;
          }
          
          .timeline-year {
            font-size: 1.4rem;
          }
          
          .stat-number {
            font-size: 2rem;
          }
          
          .section-title {
            font-size: 1.8rem;
            margin-bottom: 2.5rem;
          }
          
          .intro-image-card {
            height: 250px;
          }
          
          .achievement-image-card {
            height: 200px;
          }
          
          .course-header-image {
            height: 250px;
          }
          
          .quote-text {
            font-size: 1.1rem;
          }
          
          .activity-icon-large {
            font-size: 3rem;
          }
        }
      `}</style>
    </>
  );
};

export default AboutInstitute;
