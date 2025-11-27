import React from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';

const AboutFounder: React.FC = () => {
  const { t } = useI18n();

  // Helper function to get image path (handles space in directory name)
  const getImagePath = (filename: string): string => {
    // URL encode the space in directory name
    return `/images/about%20doctore/${filename}`;
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
        <title>درباره بنیان‌گذار - دکتر مجتبی امامی دوست</title>
        <meta name="description" content="آشنایی با دکتر سید مجتبی امامی دوست، صاحب امتیاز و مسئول فنی مرکز مشاوره سرمد و متخصص روانشناسی" />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "دکتر سید مجتبی امامی دوست",
            "jobTitle": "صاحب امتیاز و مسئول فنی مرکز مشاوره سرمد",
            "description": "متخصص روانشناسی با سال‌ها تجربه در زمینه شناخت درمانی، طرحواره درمانی و مشاوره تخصصی",
            "image": "/images/IMG_20250709_190605_376.JPG",
            "url": "https://sarmadclinic.ir/about-founder",
            "sameAs": [
              "https://sarmadclinic.ir"
            ],
            "worksFor": {
              "@type": "Organization",
              "name": "مرکز مشاوره و خدمات روانشناسی سرمد",
              "url": "https://sarmadclinic.ir"
            },
            "knowsAbout": [
              "روانشناسی",
              "شناخت درمانی",
              "طرحواره درمانی",
              "مشاوره تخصصی"
            ],
            "hasOccupation": {
              "@type": "Occupation",
              "name": "روانشناس و مشاور",
              "occupationLocation": {
                "@type": "Place",
                "name": "ایران"
              }
            }
          })}
        </script>
      </Helmet>

      {/* Hero Section */}
      <section className="founder-hero">
        <Container className="founder-content">
          <Row className="align-items-center justify-content-center">
            <Col lg={10} className="text-center">
              <h1 className="display-4 mb-3">دکتر سید مجتبی امامی دوست</h1>
              <h4 className="mb-4">صاحب امتیاز و مسئول فنی مرکز مشاوره سرمد</h4>
              <p className="lead">
                متخصص روانشناسی با سال‌ها تجربه در زمینه شناخت درمانی، طرحواره درمانی و مشاوره تخصصی
              </p>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Introduction Image Section */}
      <section className="py-5">
        <Container>
          <Row className="justify-content-center">
            <Col lg={10}>
              <div className="introduction-image-card">
                <img 
                  src={getImagePath('1752075396482.png')}
                  onError={handleImageError}
                  alt="دکتر سید مجتبی امامی دوست - فعالیت‌های حرفه‌ای" 
                  className="introduction-image"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Education & Credentials */}
      <section className="py-5 bg-light">
        <Container>
          <Row className="align-items-center g-4">
            <Col lg={6} className="mb-4 mb-lg-0">
              <div className="specialization-card">
                <div className="text-center mb-4">
                  <i className="fas fa-graduation-cap expertise-icon"></i>
                  <h3>تحصیلات</h3>
                </div>
                <div className="credentials-list">
                  <ul className="list-unstyled mb-0">
                    <li><strong>مدرک:</strong> دکتری روانشناسی</li>
                    <li><strong>تخصص اصلی:</strong> روانشناسی بالینی</li>
                    <li><strong>حوزه فعالیت:</strong> درمان و مشاوره</li>
                  </ul>
                </div>
              </div>
            </Col>
            
            <Col lg={6} className="mb-4 mb-lg-0">
              <div className="specialization-card">
                <div className="text-center mb-4">
                  <i className="fas fa-brain expertise-icon"></i>
                  <h3>حوزه‌های تخصصی</h3>
                </div>
                <div className="credentials-list">
                  <ul className="list-unstyled mb-0">
                    <li>شناخت درمانگر</li>
                    <li>طرحواره درمانگر</li>
                    <li>سوپروایزر طرحواره درمانی</li>
                    <li>درمان فردی و گروهی</li>
                    <li>توسعه و رشد فردی</li>
                  </ul>
                </div>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Quote Section */}
      <section className="quote-section">
        <Container>
          <div className="quote-text">
            "هدف ما در مرکز مشاوره سرمد، ارائه خدمات روانشناسی با بالاترین کیفیت و استفاده از روش‌های مبتنی بر شواهد علمی است تا به رشد و بهبود کیفیت زندگی مراجعان کمک کنیم."
          </div>
          <p className="mt-3 mb-0"><strong>- دکتر سید مجتبی امامی دوست</strong></p>
        </Container>
      </section>

      {/* Educational Activities */}
      <section className="py-5">
        <Container>
          <h2 className="section-title">سوابق آموزشی</h2>
          
          {/* Image before educational activities */}
          <Row className="mb-5">
            <Col lg={12}>
              <div className="content-image-wrapper">
                <img 
                  src={getImagePath('IMG_20251002_163910_364.jpg')}
                  onError={handleImageError}
                  alt="دکتر امامی دوست - فعالیت‌های آموزشی" 
                  className="content-image-wide"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
          
          <Row>
            <Col lg={12}>
              <div className="specialization-card">
                <div className="text-center mb-4">
                  <i className="fas fa-chalkboard-teacher expertise-icon"></i>
                  <h3>برگزار کننده دوره‌های تخصصی و عمومی</h3>
                </div>
                
                <div className="services-grid">
                  <div className="service-item">
                    <h5><i className="fas fa-user-md me-2 text-primary"></i>تربیت طرحواره درمانگر</h5>
                    <p className="text-muted mb-0">آموزش جامع روش‌های طرحواره درمانی برای متخصصان</p>
                  </div>
                  
                  <div className="service-item">
                    <h5><i className="fas fa-mind-share me-2 text-primary"></i>تربیت درمانگر شناختی رفتاری</h5>
                    <p className="text-muted mb-0">آموزش تکنیک‌های CBT و کاربرد آن در درمان</p>
                  </div>
                  
                  <div className="service-item">
                    <h5><i className="fas fa-clipboard-list me-2 text-primary"></i>آزمون‌های روان‌شناختی</h5>
                    <p className="text-muted mb-0">آموزش اجرا و تفسیر تست‌های روانشناختی</p>
                  </div>
                  
                  <div className="service-item">
                    <h5><i className="fas fa-baby me-2 text-primary"></i>فرزندپروری مبتنی بر طرحواره</h5>
                    <p className="text-muted mb-0">راهنمایی والدین برای تربیت موثر فرزندان</p>
                  </div>
                  
                  <div className="service-item">
                    <h5><i className="fas fa-heart me-2 text-primary"></i>تنظیم هیجانات</h5>
                    <p className="text-muted mb-0">آموزش مهارت‌های مدیریت و کنترل احساسات</p>
                  </div>
                  
                  <div className="service-item">
                    <h5><i className="fas fa-life-ring me-2 text-primary"></i>مهارت‌های زندگی</h5>
                    <p className="text-muted mb-0">توسعه مهارت‌های ضروری برای زندگی بهتر</p>
                  </div>
                </div>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Experience & Vision */}
      <section className="py-5">
        <Container>
          <Row className="align-items-center">
            <Col lg={6} className="mb-4 mb-lg-0">
              <div className="specialization-card">
                <div className="text-center mb-4">
                  <i className="fas fa-award expertise-icon"></i>
                  <h3>تجربه و مسئولیت‌ها</h3>
                </div>
                <div className="credentials-list">
                  <ul className="list-unstyled mb-0">
                    <li>صاحب امتیاز مرکز مشاوره سرمد</li>
                    <li>مسئول فنی مرکز مشاوره سرمد</li>
                    <li>سوپروایزر طرحواره درمانی</li>
                    <li>مدرس دوره‌های تخصصی روانشناسی</li>
                  </ul>
                </div>
              </div>
            </Col>
            
            <Col lg={6} className="mb-4 mb-lg-0">
              <div className="content-image-wrapper">
                <img 
                  src={getImagePath('IMG_20251002_163910_364.jpg')}
                  onError={handleImageError}
                  alt="دکتر سید مجتبی امامی دوست - تجربه و تخصص" 
                  className="content-image"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
          
          <Row className="mt-4">
            <Col lg={12}>
              <div className="specialization-card">
                <div className="text-center mb-4">
                  <i className="fas fa-eye expertise-icon"></i>
                  <h3>چشم‌انداز و رویکرد</h3>
                </div>
                <Row className="align-items-center">
                  <Col lg={8}>
                    <p className="mb-3">
                      دکتر امامی دوست با ترکیب دانش علمی روز و تجربه‌های عملی، رویکردی جامع و کارآمد در ارائه خدمات روانشناسی دارد.
                    </p>
                    <p className="mb-0">
                      تأکید بر استفاده از روش‌های مبتنی بر شواهد علمی و کاربرد تکنیک‌های نوین در درمان، از ویژگی‌های بارز رویکرد ایشان است.
                    </p>
                  </Col>
                  <Col lg={4} className="text-center">
                    <div className="vision-image-wrapper">
                      <img 
                        src={getImagePath('IMG_20251002_163910_364.jpg')}
                        onError={handleImageError}
                        alt="رویکرد حرفه‌ای دکتر امامی دوست" 
                        className="vision-image"
                        loading="lazy"
                      />
                    </div>
                  </Col>
                </Row>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Image Gallery Section */}
      <section className="py-5 bg-light">
        <Container>
          <h2 className="section-title">گالری تصاویر</h2>
          <Row className="g-4">
            <Col md={6}>
              <div className="gallery-image-wrapper">
                <img 
                  src={getImagePath('1752075396482.png')}
                  onError={handleImageError}
                  alt="دکتر سید مجتبی امامی دوست - فعالیت‌های حرفه‌ای" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
            <Col md={6}>
              <div className="gallery-image-wrapper">
                <img 
                  src={getImagePath('IMG_20251002_163910_364.jpg')}
                  onError={handleImageError}
                  alt="دکتر سید مجتبی امامی دوست - تخصص و تجربه" 
                  className="gallery-image"
                  loading="lazy"
                />
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Contact CTA */}
      <section className="contact-cta">
        <Container>
          <Row className="justify-content-center">
            <Col lg={8} className="text-center">
              <h3 className="mb-3">برای دریافت مشاوره تخصصی</h3>
              <p className="mb-4">
                می‌توانید با مرکز مشاوره سرمد تماس گرفته و جلسه مشاوره خود را رزرو کنید
              </p>
              <div className="d-flex flex-wrap justify-content-center gap-3">
                <Link to="/sessions" className="btn btn-primary btn-lg">
                  <i className="fas fa-calendar-check me-2"></i>رزرو جلسه مشاوره
                </Link>
                <a href="/contact" className="btn btn-outline-primary btn-lg">
                  <i className="fas fa-phone me-2"></i>تماس با ما
                </a>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      <style>{`
        .founder-hero {
          background: linear-gradient(135deg, var(--primary-color) 0%, #3498db 100%);
          color: white;
          padding: 4rem 0;
          position: relative;
          overflow: hidden;
        }
        
        .founder-hero::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.1);
        }
        
        .founder-content {
          position: relative;
          z-index: 2;
        }
        
        .founder-image-large {
          width: 220px;
          height: 220px;
          object-fit: cover;
          border: 6px solid rgba(255,255,255,0.9);
          box-shadow: 0 20px 50px rgba(0,0,0,0.3), inset 0 0 0 3px rgba(255,255,255,0.5);
          margin-bottom: 2rem;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .founder-image-large:hover {
          transform: scale(1.05);
          box-shadow: 0 25px 60px rgba(0,0,0,0.4), inset 0 0 0 3px rgba(255,255,255,0.6);
        }
        
        .specialization-card {
          background: white;
          border-radius: 15px;
          padding: 2rem;
          box-shadow: 0 10px 30px rgba(0,0,0,0.1);
          margin-bottom: 2rem;
          transition: transform 0.3s ease;
        }
        
        .specialization-card:hover {
          transform: translateY(-5px);
        }
        
        .expertise-icon {
          font-size: 2.5rem;
          color: var(--primary-color);
          margin-bottom: 1rem;
        }
        
        .credentials-list {
          background: var(--light-gray);
          border-radius: 10px;
          padding: 1.5rem;
        }
        
        .credentials-list li {
          padding: 0.5rem 0;
          border-bottom: 1px solid rgba(0,0,0,0.1);
        }
        
        .credentials-list li:last-child {
          border-bottom: none;
        }
        
        .quote-section {
          background: var(--primary-color);
          color: white;
          padding: 3rem 0;
          text-align: center;
          margin: 3rem 0;
        }
        
        .quote-text {
          font-size: 1.3rem;
          font-style: italic;
          line-height: 1.8;
          max-width: 800px;
          margin: 0 auto;
        }
        
        .services-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin: 3rem 0;
        }
        
        .service-item {
          background: white;
          border-radius: 10px;
          padding: 1.5rem;
          box-shadow: 0 5px 15px rgba(0,0,0,0.08);
          border-left: 4px solid var(--primary-color);
        }
        
        .contact-cta {
          background: var(--light-gray);
          border-radius: 15px;
          padding: 3rem 2rem;
          text-align: center;
          margin: 3rem 0;
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
        
        .introduction-image-card {
          position: relative;
          overflow: hidden;
          border-radius: 20px;
          box-shadow: 0 15px 50px rgba(0,0,0,0.2);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          background: white;
          padding: 20px;
          margin: 2rem 0;
        }
        
        .introduction-image-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 20px 60px rgba(0,0,0,0.25);
        }
        
        .introduction-image {
          width: 100%;
          height: auto;
          max-height: 600px;
          object-fit: contain;
          border-radius: 15px;
          display: block;
          transition: transform 0.5s ease;
        }
        
        .introduction-image-card:hover .introduction-image {
          transform: scale(1.02);
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
        
        .vision-image-wrapper {
          position: relative;
          overflow: hidden;
          border-radius: 15px;
          box-shadow: 0 8px 25px rgba(0,0,0,0.12);
          transition: transform 0.3s ease;
          background: #f8f9fa;
        }
        
        .vision-image-wrapper:hover {
          transform: scale(1.05);
        }
        
        .vision-image {
          width: 100%;
          height: auto;
          object-fit: cover;
          border-radius: 15px;
          display: block;
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
          .founder-image-large {
            width: 150px;
            height: 150px;
          }
          
          .founder-hero {
            padding: 2rem 0;
          }
          
          .quote-text {
            font-size: 1.1rem;
          }
          
          .section-title {
            font-size: 2rem;
            margin-bottom: 2rem;
          }
          
          .content-image-wrapper,
          .vision-image-wrapper {
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

export default AboutFounder;
