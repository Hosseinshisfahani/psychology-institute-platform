import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Row, Col } from 'react-bootstrap';
import { useI18n } from '../../contexts/I18nContext';

const Footer: React.FC = () => {
  const { t } = useI18n();

  return (
    <footer className="footer">
      <Container>
        <Row>
          <Col lg={4} className="mb-4">
            <h5>{t('home.title')}</h5>
            <p className="text-muted">
              ارائه خدمات روانشناسی و مشاوره آنلاین با بالاترین کیفیت و تخصص
            </p>
            <div className="mt-4 text-center founder-section">
              <Link to="/about-founder" className="text-decoration-none">
                <img 
                  src="/images/IMG_20250709_190605_376.JPG" 
                  alt="مدیرعامل و بنیان‌گذار" 
                  className="rounded-circle shadow founder-image"
                  loading="lazy"
                  style={{ cursor: 'pointer' }}
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    const fallback = e.currentTarget.nextElementSibling?.querySelector('.fallback-icon') as HTMLElement;
                    if (fallback) fallback.style.display = 'block';
                  }}
                />
                <div className="mt-3 founder-info">
                  <div className="fallback-icon" style={{ display: 'none' }}>
                    <i className="fas fa-user-circle" style={{ fontSize: '120px', color: 'rgba(255,255,255,0.3)' }}></i>
                  </div>
                  <h6 className="text-white mb-1">مدیرعامل و بنیان‌گذار</h6>
                  <small className="text-muted">مرکز مشاوره و خدمات روانشناسی سرمد</small>
                </div>
              </Link>
            </div>
          </Col>
          
          <Col lg={2} className="mb-4">
            <h6>خدمات</h6>
            <ul className="list-unstyled">
              <li>
                <Link to="/tests" className="text-muted text-decoration-none">
                  {t('nav.tests')}
                </Link>
              </li>
              <li>
                <Link to="/courses" className="text-muted text-decoration-none">
                  {t('nav.courses')}
                </Link>
              </li>
            </ul>
          </Col>
          
          <Col lg={2} className="mb-4">
            <h6>دسترسی سریع</h6>
            <ul className="list-unstyled">
              <li>
                <Link to="/" className="text-muted text-decoration-none">
                  {t('nav.home')}
                </Link>
              </li>
              <li>
                <Link to="/blog" className="text-muted text-decoration-none">
                  {t('nav.blog')}
                </Link>
              </li>
                <li>
                  <Link to="/about/institute" className="text-muted text-decoration-none">
                    درباره مؤسسه
                  </Link>
                </li>
                <li>
                  <Link to="/about/founder" className="text-muted text-decoration-none">
                    درباره بنیان‌گذار
                  </Link>
                </li>
            </ul>
          </Col>
          
          <Col lg={4} className="mb-4">
            <h6>تماس با ما</h6>
            <p className="text-muted">
              <i className="fas fa-map-marker-alt me-2"></i>
              اصفهان، میدان احمدآباد، ابتدای خیابان ولیعصر، جنب بانک مسکن، ساختمان پزشکی، طبقه اول
            </p>
            <p className="text-muted">
              <i className="fas fa-phone me-2"></i>
              ۰۳۱-۳۲۲۹۶۳۱۲ | ۰۳۱-۳۲۲۹۲۷۹۷
            </p>
            <p className="text-muted">
              <i className="fab fa-whatsapp me-2"></i>
              ۰۹۳۸۳۸۲۱۱۰۰ | ۰۹۰۵۳۰۰۰۲۱۳ | ۰۹۱۹۰۹۱۹۹۵۰
            </p>
            <p className="text-muted">
              <i className="fas fa-envelope me-2"></i>
              info@sarmadclinic.ir
            </p>
          </Col>
        </Row>
        
        <hr className="my-4" />
        
        <Row className="align-items-center">
          <Col md={6}>
            <p className="text-muted mb-0">
              &copy; 2024 مرکز مشاوره و خدمات روانشناسی سرمد. تمامی حقوق محفوظ است.
            </p>
            <p className="text-muted mb-0 mt-2">
              ساخته شده با ❤️ توسط{' '}
              <a 
                href="https://t.me/py_isfahani" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-muted text-decoration-none"
                style={{ fontWeight: '500' }}
              >
                حسین
              </a>
            </p>
          </Col>
          <Col md={6} className="text-md-end">
            <a 
              href="https://t.me/sarmadclinic" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-muted me-3" 
              title="تلگرام"
            >
              <i className="fab fa-telegram"></i>
            </a>
            <a 
              href="https://instagram.com/sarmadclinic" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-muted me-3" 
              title="اینستاگرام"
            >
              <i className="fab fa-instagram"></i>
            </a>
            <a 
              href="https://wa.me/989383821100" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-muted me-3" 
              title="واتساپ"
            >
              <i className="fab fa-whatsapp"></i>
            </a>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;
