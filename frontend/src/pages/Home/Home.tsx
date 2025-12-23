import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, InputGroup } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';
import axios from 'axios';
import './Home.css';

interface Post {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  featured_image?: string;
  category: {
    name: string;
  };
  author_name: string;
  view_count: number;
  created_at_persian: string;
}

interface Workshop {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  instructor_name: string;
  start_date_persian: string;
  total_hours: number;
  price: string;
  discount_price: string | null;
  current_price: string;
  discount_percentage: number;
  thumbnail: string | null;
  available_seats: number;
  is_full: boolean;
}

interface Package {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  total_courses: number;
  total_hours: number;
  price: string;
  discount_price: string | null;
  current_price: string;
  discount_percentage: number;
  savings_percentage: number;
  thumbnail: string | null;
  is_featured: boolean;
}


const Home: React.FC = () => {
  const { t } = useI18n();
  const [newsletterEmail, setNewsletterEmail] = useState('');

  // Fetch latest posts
  const { data: posts = [], isLoading: postsLoading } = useQuery({
    queryKey: ['latest-posts'],
    queryFn: async () => {
      const response = await axios.get('/api/blog/posts/?limit=6');
      return response.data.results || [];
    },
  });

  // Fetch latest workshops
  const { data: workshops = [], isLoading: workshopsLoading } = useQuery<Workshop[]>({
    queryKey: ['featured-workshops'],
    queryFn: async () => {
      const response = await axios.get('/api/workshops/?limit=3');
      // Handle paginated response from Django REST Framework
      const data = response.data.results || response.data;
      return Array.isArray(data) ? data.slice(0, 3) : [];
    },
  });

  // Fetch featured packages
  const { data: packages = [], isLoading: packagesLoading } = useQuery<Package[]>({
    queryKey: ['featured-packages'],
    queryFn: async () => {
      const response = await axios.get('/api/packages/?featured=true&limit=3');
      // Handle paginated response from Django REST Framework
      const data = response.data.results || response.data;
      return Array.isArray(data) ? data.slice(0, 3) : [];
    },
  });

  const packageCount = packages.length;
  const totalPackageCourses = packages.reduce((sum, pkg) => sum + (pkg.total_courses || 0), 0);
  const totalPackageHours = packages.reduce((sum, pkg) => sum + (pkg.total_hours || 0), 0);
  const maxPackageSavings = packages.reduce(
    (max, pkg) => Math.max(max, pkg.savings_percentage ?? pkg.discount_percentage ?? 0),
    0
  );

  const packageHighlightItems = [
    {
      icon: 'fa-layer-group',
      text:
        packageCount > 0
          ? `${packageCount.toLocaleString('fa-IR')} بسته فعال آماده استفاده`
          : 'بسته‌های انتخاب‌شده بر اساس نیازهای پرتکرار',
    },
    {
      icon: 'fa-book-open',
      text:
        totalPackageCourses > 0
          ? `${totalPackageCourses.toLocaleString('fa-IR')} دوره و کارگاه تکمیلی`
          : 'ترکیب دوره‌ها و تمرین‌های کاربردی',
    },
    {
      icon: 'fa-clock',
      text:
        totalPackageHours > 0
          ? `${totalPackageHours.toLocaleString('fa-IR')} ساعت محتوای ویدئویی منظم`
          : 'دسترسی به ویدئوها و فایل‌های کمکی هر زمان که بخواهید',
    },
  ];

  if (maxPackageSavings > 0) {
    packageHighlightItems.push({
      icon: 'fa-piggy-bank',
      text: `صرفه‌جویی تا ${maxPackageSavings}% نسبت به خرید تکی`,
    });
  }

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newsletterEmail) return;

    try {
      await axios.post('/api/blog/newsletter/subscribe/', {
        email: newsletterEmail,
      });
      alert('با موفقیت در خبرنامه عضو شدید!');
      setNewsletterEmail('');
    } catch (error) {
      console.error('Newsletter subscription error:', error);
      alert('خطا در عضویت در خبرنامه');
    }
  };

  return (
    <>
      <Helmet>
        <title>{t('home.title')}</title>
        <meta name="description" content={t('home.subtitle')} />
      </Helmet>

      {/* Hero Section */}
      <section className="hero-section">
        <Container>
          <Row className="align-items-center">
            <Col lg={6} className="hero-content">
              <h1 className="hero-title">{t('home.title')}</h1>
              <p className="hero-subtitle">{t('home.subtitle')}</p>
              <div className="hero-buttons-container">
                <Link to="/tests" className="hero-btn hero-btn-primary">
                  <i className="fas fa-brain"></i>
                  {t('home.cta.tests')}
                </Link>
                <Link to="/therapists" className="hero-btn hero-btn-primary">
                  <i className="fas fa-user-md"></i>
                  درمانگران
                </Link>
                <Link to="/workshops" className="hero-btn hero-btn-primary">
                  <i className="fas fa-chalkboard-teacher"></i>
                  کارگاه‌ها
                </Link>
                <Link to="/packages" className="hero-btn hero-btn-primary">
                  <i className="fas fa-box-open"></i>
                  پکیج‌ها
                </Link>
              </div>
            </Col>
            <Col lg={6} className="text-center">
              <Link to="/about-institute">
                <div className="hero-logo-container">
                  <img 
                    src="/images/1744027219152.png" 
                    alt={t('home.title')} 
                    className="hero-logo-image"
                    loading="eager"
                  />
                </div>
              </Link>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Features Section */}
      <section style={{ padding: '6rem 0', background: 'linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%)' }}>
        <Container>
          <div className="text-center mb-5" style={{ position: 'relative' }}>
            <h2 
              className="section-title" 
              style={{ 
                fontSize: '2.75rem', 
                fontWeight: 700, 
                marginBottom: '1rem',
                color: '#1a1a1a',
                letterSpacing: '-0.5px'
              }}
            >
              {t('home.services.title')}
            </h2>
            <div 
              style={{
                width: '80px',
                height: '4px',
                background: 'linear-gradient(90deg, #2c5aa0 0%, #3498db 100%)',
                borderRadius: '2px',
                margin: '0 auto 1.5rem',
              }}
            />
            <p 
              className="text-muted lead" 
              style={{ 
                maxWidth: '700px', 
                margin: '0 auto', 
                fontSize: '1.2rem',
                lineHeight: '1.8',
                color: '#6c757d'
              }}
            >
              خدمات جامع روانشناسی برای رشد و بهبود شما
            </p>
          </div>
          
          <Row className="g-4 justify-content-center">
            {/* Sessions - Blue Theme */}
            <Col lg={4} md={6}>
              <Card 
                className="text-center h-100 service-card" 
                style={{ 
                  border: 'none',
                  borderRadius: '24px',
                  background: '#ffffff',
                  boxShadow: '0 4px 20px rgba(52, 152, 219, 0.1)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  overflow: 'hidden',
                  position: 'relative',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-15px)';
                  e.currentTarget.style.boxShadow = '0 25px 60px rgba(52, 152, 219, 0.25)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1.1) rotate(5deg)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(52, 152, 219, 0.1)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                  }
                }}
              >
                <Card.Body style={{ padding: '3rem 2.5rem' }}>
                  <div 
                    className="service-icon" 
                    style={{ 
                      width: '100px',
                      height: '100px',
                      margin: '0 auto 2rem',
                      background: 'linear-gradient(135deg, #3498db 0%, #5dade2 100%)',
                      borderRadius: '24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: '0 8px 24px rgba(52, 152, 219, 0.3)',
                    }}
                  >
                    <i className="fas fa-calendar-check" style={{ fontSize: '2.75rem', color: 'white' }}></i>
                  </div>
                  <h5 
                    className="card-title mb-3" 
                    style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: 700,
                      color: '#1a1a1a',
                      lineHeight: '1.4'
                    }}
                  >
                    {t('home.services.sessions')}
                  </h5>
                  <p 
                    className="card-text text-muted mb-4" 
                    style={{ 
                      fontSize: '1rem', 
                      lineHeight: '1.8',
                      color: '#6c757d',
                      minHeight: '54px'
                    }}
                  >
                    {t('home.services.sessions.desc')}
                  </p>
                  <Link 
                    to="/therapists" 
                    className="btn service-btn"
                    style={{ 
                      borderRadius: '14px', 
                      padding: '0.875rem 2.25rem', 
                      fontWeight: 600,
                      fontSize: '1rem',
                      border: 'none',
                      background: 'linear-gradient(135deg, #3498db 0%, #5dade2 100%)',
                      color: 'white',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 12px rgba(52, 152, 219, 0.35)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateX(-5px)';
                      e.currentTarget.style.boxShadow = '0 6px 18px rgba(52, 152, 219, 0.45)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateX(0)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(52, 152, 219, 0.35)';
                    }}
                  >
                    <i className="fas fa-arrow-left ms-2"></i>
                    رزرو جلسه
                  </Link>
                </Card.Body>
              </Card>
            </Col>

            {/* Packages - Blue Theme */}
            <Col lg={4} md={6}>
              <Card 
                className="text-center h-100 service-card" 
                style={{ 
                  border: 'none',
                  borderRadius: '24px',
                  background: '#ffffff',
                  boxShadow: '0 4px 20px rgba(41, 128, 185, 0.1)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  overflow: 'hidden',
                  position: 'relative',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-15px)';
                  e.currentTarget.style.boxShadow = '0 25px 60px rgba(41, 128, 185, 0.25)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1.1) rotate(-5deg)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(41, 128, 185, 0.1)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                  }
                }}
              >
                <Card.Body style={{ padding: '3rem 2.5rem' }}>
                  <div 
                    className="service-icon" 
                    style={{ 
                      width: '100px',
                      height: '100px',
                      margin: '0 auto 2rem',
                      background: 'linear-gradient(135deg, #2980b9 0%, #3498db 100%)',
                      borderRadius: '24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: '0 8px 24px rgba(41, 128, 185, 0.3)',
                    }}
                  >
                    <i className="fas fa-box-open" style={{ fontSize: '2.75rem', color: 'white' }}></i>
                  </div>
                  <div style={{ marginBottom: '0.75rem' }}>
                    <span 
                      className="badge" 
                      style={{ 
                        background: 'linear-gradient(135deg, #87ceeb 0%, #b0e0e6 100%)',
                        color: '#1a1a1a',
                        fontSize: '0.85rem',
                        padding: '0.5rem 1rem',
                        borderRadius: '20px',
                        fontWeight: 600,
                        boxShadow: '0 2px 8px rgba(135, 206, 235, 0.3)',
                      }}
                    >
                      ویژه
                    </span>
                  </div>
                  <h5 
                    className="card-title mb-3" 
                    style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: 700,
                      color: '#1a1a1a',
                      lineHeight: '1.4'
                    }}
                  >
                    بسته‌های آموزشی
                  </h5>
                  <p 
                    className="card-text text-muted mb-4" 
                    style={{ 
                      fontSize: '1rem', 
                      lineHeight: '1.8',
                      color: '#6c757d',
                      minHeight: '54px'
                    }}
                  >
                    دسترسی به مجموعه بسته‌های آموزشی ضبط شده با تخفیف
                  </p>
                  <Link 
                    to="/packages" 
                    className="btn service-btn"
                    style={{ 
                      borderRadius: '14px', 
                      padding: '0.875rem 2.25rem', 
                      fontWeight: 600,
                      fontSize: '1rem',
                      border: 'none',
                      background: 'linear-gradient(135deg, #2980b9 0%, #3498db 100%)',
                      color: 'white',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 12px rgba(41, 128, 185, 0.35)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateX(-5px)';
                      e.currentTarget.style.boxShadow = '0 6px 18px rgba(41, 128, 185, 0.45)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateX(0)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(41, 128, 185, 0.35)';
                    }}
                  >
                    <i className="fas fa-arrow-left ms-2"></i>
                    مشاهده بسته‌ها
                  </Link>
                </Card.Body>
              </Card>
            </Col>

            {/* Tests - Blue Theme */}
            <Col lg={4} md={6}>
              <Card 
                className="text-center h-100 service-card" 
                style={{ 
                  border: 'none',
                  borderRadius: '24px',
                  background: '#ffffff',
                  boxShadow: '0 4px 20px rgba(91, 143, 212, 0.1)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  overflow: 'hidden',
                  position: 'relative',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-15px)';
                  e.currentTarget.style.boxShadow = '0 25px 60px rgba(91, 143, 212, 0.25)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1.1) rotate(5deg)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(91, 143, 212, 0.1)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                  }
                }}
              >
                <Card.Body style={{ padding: '3rem 2.5rem' }}>
                  <div 
                    className="service-icon" 
                    style={{ 
                      width: '100px',
                      height: '100px',
                      margin: '0 auto 2rem',
                      background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                      borderRadius: '24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: '0 8px 24px rgba(91, 143, 212, 0.3)',
                    }}
                  >
                    <i className="fas fa-brain" style={{ fontSize: '2.75rem', color: 'white' }}></i>
                  </div>
                  <h5 
                    className="card-title mb-3" 
                    style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: 700,
                      color: '#1a1a1a',
                      lineHeight: '1.4'
                    }}
                  >
                    {t('home.services.tests')}
                  </h5>
                  <p 
                    className="card-text text-muted mb-4" 
                    style={{ 
                      fontSize: '1rem', 
                      lineHeight: '1.8',
                      color: '#6c757d',
                      minHeight: '54px'
                    }}
                  >
                    {t('home.services.tests.desc')}
                  </p>
                  <Link 
                    to="/tests" 
                    className="btn service-btn"
                    style={{ 
                      borderRadius: '14px', 
                      padding: '0.875rem 2.25rem', 
                      fontWeight: 600,
                      fontSize: '1rem',
                      border: 'none',
                      background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                      color: 'white',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 12px rgba(91, 143, 212, 0.35)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateX(-5px)';
                      e.currentTarget.style.boxShadow = '0 6px 18px rgba(91, 143, 212, 0.45)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateX(0)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(91, 143, 212, 0.35)';
                    }}
                  >
                    <i className="fas fa-arrow-left ms-2"></i>
                    مشاهده تست‌ها
                  </Link>
                </Card.Body>
              </Card>
            </Col>

            {/* Articles - Blue Theme */}
            <Col lg={6} md={6}>
              <Card 
                className="text-center h-100 service-card" 
                style={{ 
                  border: 'none',
                  borderRadius: '24px',
                  background: '#ffffff',
                  boxShadow: '0 4px 20px rgba(44, 90, 160, 0.1)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  overflow: 'hidden',
                  position: 'relative',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-15px)';
                  e.currentTarget.style.boxShadow = '0 25px 60px rgba(44, 90, 160, 0.25)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1.1) rotate(-5deg)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(44, 90, 160, 0.1)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                  }
                }}
              >
                <Card.Body style={{ padding: '3rem 2.5rem' }}>
                  <div 
                    className="service-icon" 
                    style={{ 
                      width: '100px',
                      height: '100px',
                      margin: '0 auto 2rem',
                      background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                      borderRadius: '24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: '0 8px 24px rgba(44, 90, 160, 0.3)',
                    }}
                  >
                    <i className="fas fa-newspaper" style={{ fontSize: '2.75rem', color: 'white' }}></i>
                  </div>
                  <h5 
                    className="card-title mb-3" 
                    style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: 700,
                      color: '#1a1a1a',
                      lineHeight: '1.4'
                    }}
                  >
                    {t('home.services.articles')}
                  </h5>
                  <p 
                    className="card-text text-muted mb-4" 
                    style={{ 
                      fontSize: '1rem', 
                      lineHeight: '1.8',
                      color: '#6c757d',
                      minHeight: '54px'
                    }}
                  >
                    {t('home.services.articles.desc')}
                  </p>
                  <Link 
                    to="/blog" 
                    className="btn service-btn"
                    style={{ 
                      borderRadius: '14px', 
                      padding: '0.875rem 2.25rem', 
                      fontWeight: 600,
                      fontSize: '1rem',
                      border: 'none',
                      background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                      color: 'white',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 12px rgba(44, 90, 160, 0.35)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateX(-5px)';
                      e.currentTarget.style.boxShadow = '0 6px 18px rgba(44, 90, 160, 0.45)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateX(0)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(44, 90, 160, 0.35)';
                    }}
                  >
                    <i className="fas fa-arrow-left ms-2"></i>
                    مطالعه مقالات
                  </Link>
                </Card.Body>
              </Card>
            </Col>

            {/* Workshops - Blue Theme */}
            <Col lg={6} md={6}>
              <Card 
                className="text-center h-100 service-card" 
                style={{ 
                  border: 'none',
                  borderRadius: '24px',
                  background: '#ffffff',
                  boxShadow: '0 4px 20px rgba(44, 90, 160, 0.1)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  overflow: 'hidden',
                  position: 'relative',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-15px)';
                  e.currentTarget.style.boxShadow = '0 25px 60px rgba(44, 90, 160, 0.25)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1.1) rotate(-5deg)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(44, 90, 160, 0.1)';
                  const icon = e.currentTarget.querySelector('.service-icon') as HTMLElement;
                  if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                  }
                }}
              >
                <Card.Body style={{ padding: '3rem 2.5rem' }}>
                  <div 
                    className="service-icon" 
                    style={{ 
                      width: '100px',
                      height: '100px',
                      margin: '0 auto 2rem',
                      background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                      borderRadius: '24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: '0 8px 24px rgba(44, 90, 160, 0.3)',
                    }}
                  >
                    <i className="fas fa-chalkboard-teacher" style={{ fontSize: '2.75rem', color: 'white' }}></i>
                  </div>
                  <h5 
                    className="card-title mb-3" 
                    style={{ 
                      fontSize: '1.5rem', 
                      fontWeight: 700,
                      color: '#1a1a1a',
                      lineHeight: '1.4'
                    }}
                  >
                    کارگاه‌های آموزشی
                  </h5>
                  <p 
                    className="card-text text-muted mb-4" 
                    style={{ 
                      fontSize: '1rem', 
                      lineHeight: '1.8',
                      color: '#6c757d',
                      minHeight: '54px'
                    }}
                  >
                    در کارگاه‌های تعاملی شرکت کرده و به‌صورت زنده یاد بگیرید
                  </p>
                  <Link 
                    to="/workshops" 
                    className="btn service-btn"
                    style={{ 
                      borderRadius: '14px', 
                      padding: '0.875rem 2.25rem', 
                      fontWeight: 600,
                      fontSize: '1rem',
                      border: 'none',
                      background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                      color: 'white',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 4px 12px rgba(44, 90, 160, 0.35)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateX(-5px)';
                      e.currentTarget.style.boxShadow = '0 6px 18px rgba(44, 90, 160, 0.45)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateX(0)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(44, 90, 160, 0.35)';
                    }}
                  >
                    <i className="fas fa-arrow-left ms-2"></i>
                    مشاهده کارگاه‌ها
                  </Link>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Workshops Section */}
      <section style={{ 
        padding: '6rem 0', 
        background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 50%, #5dade2 100%)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Decorative background elements */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%), radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
          pointerEvents: 'none'
        }}></div>
        <Container style={{ position: 'relative', zIndex: 1 }}>
          <div className="text-center mb-5">
            <div style={{
              display: 'inline-block',
              padding: '0.5rem 1.5rem',
              background: 'rgba(255, 255, 255, 0.95)',
              borderRadius: '50px',
              color: '#2c5aa0',
              fontSize: '0.9rem',
              fontWeight: 600,
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
              marginBottom: '1.5rem'
            }}>
              <i className="fas fa-chalkboard-teacher me-2"></i>
              کارگاه‌های تعاملی
            </div>
            <h2 style={{ 
              fontSize: '3rem', 
              fontWeight: 800, 
              marginBottom: '1rem',
              color: 'white',
              lineHeight: '1.2',
              textShadow: '0 2px 10px rgba(0, 0, 0, 0.2)'
            }}>
              کارگاه‌های آموزشی
            </h2>
            <p className="lead" style={{ 
              fontSize: '1.2rem', 
              maxWidth: '700px', 
              margin: '0 auto',
              color: 'rgba(255, 255, 255, 0.95)',
              lineHeight: '1.8',
              textShadow: '0 1px 5px rgba(0, 0, 0, 0.1)'
            }}>
              در کارگاه‌های تعاملی ما شرکت کرده و به‌صورت زنده یاد بگیرید
            </p>
          </div>
          
          {workshopsLoading ? (
            <div className="text-center" style={{ padding: '5rem 0' }}>
              <div className="spinner-border" role="status" style={{ width: '3rem', height: '3rem', borderColor: 'rgba(255, 255, 255, 0.3)', borderTopColor: 'white' }}>
                <span className="visually-hidden">در حال بارگذاری...</span>
              </div>
              <p className="mt-3" style={{ fontSize: '1.05rem', color: 'rgba(255, 255, 255, 0.95)' }}>در حال بارگذاری کارگاه‌ها...</p>
            </div>
          ) : workshops.length > 0 ? (
            <>
              <Row className="g-4">
                {workshops.map((workshop) => (
                  <Col key={workshop.id} md={6} lg={4}>
                    <Card 
                      className="h-100"
                      style={{
                        border: '2px solid rgba(255, 255, 255, 0.3)',
                        borderRadius: '24px',
                        overflow: 'hidden',
                        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                        cursor: 'pointer',
                        background: 'linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%)',
                        boxShadow: '0 15px 40px rgba(0, 0, 0, 0.2), 0 5px 15px rgba(44, 90, 160, 0.15)',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-12px)';
                        e.currentTarget.style.boxShadow = '0 25px 60px rgba(0, 0, 0, 0.3), 0 10px 25px rgba(44, 90, 160, 0.25)';
                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.5)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 15px 40px rgba(0, 0, 0, 0.2), 0 5px 15px rgba(44, 90, 160, 0.15)';
                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                      }}
                    >
                      {workshop.thumbnail && (
                        <div style={{ 
                          overflow: 'hidden', 
                          position: 'relative',
                          height: '240px',
                          background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)'
                        }}>
                          <Card.Img
                            variant="top"
                            src={workshop.thumbnail}
                            alt={workshop.title}
                            loading="lazy"
                            style={{ 
                              height: '100%', 
                              width: '100%',
                              objectFit: 'cover', 
                              transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                          />
                          <div style={{
                            position: 'absolute',
                            top: '1rem',
                            left: '1rem',
                            background: 'rgba(255, 255, 255, 0.95)',
                            padding: '0.5rem 1rem',
                            borderRadius: '20px',
                            fontSize: '0.85rem',
                            fontWeight: 600,
                            color: '#2c5aa0',
                            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                          }}>
                            <i className="fas fa-users me-1"></i>
                            {workshop.available_seats > 0 ? `${workshop.available_seats} جای خالی` : 'تکمیل شده'}
                          </div>
                        </div>
                      )}
                      <Card.Body className="d-flex flex-column" style={{ padding: '2rem' }}>
                        <Card.Title className="mb-3" style={{ 
                          fontSize: '1.35rem', 
                          fontWeight: 700, 
                          lineHeight: '1.4',
                          color: '#2c3e50',
                          minHeight: '3.8rem'
                        }}>
                          {workshop.title}
                        </Card.Title>
                        <Card.Text className="mb-4" style={{ 
                          fontSize: '1rem', 
                          lineHeight: '1.7',
                          color: '#6c757d',
                          flex: '1'
                        }}>
                          {workshop.short_description}
                        </Card.Text>
                        
                        <div className="mb-4" style={{ flex: '1' }}>
                          <div className="d-flex align-items-center mb-3" style={{ fontSize: '0.95rem' }}>
                            <div style={{
                              width: '40px',
                              height: '40px',
                              borderRadius: '12px',
                              background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              marginLeft: '0.75rem'
                            }}>
                              <i className="fas fa-user" style={{ color: 'white', fontSize: '0.9rem' }}></i>
                          </div>
                            <span style={{ color: '#495057', fontWeight: 500 }}>{workshop.instructor_name}</span>
                          </div>
                          <div className="d-flex align-items-center mb-3" style={{ fontSize: '0.95rem' }}>
                            <div style={{
                              width: '40px',
                              height: '40px',
                              borderRadius: '12px',
                              background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              marginLeft: '0.75rem'
                            }}>
                              <i className="fas fa-calendar" style={{ color: 'white', fontSize: '0.9rem' }}></i>
                            </div>
                            <span style={{ color: '#495057', fontWeight: 500 }}>شروع: {workshop.start_date_persian}</span>
                          </div>
                          <div className="d-flex align-items-center" style={{ fontSize: '0.95rem' }}>
                            <div style={{
                              width: '40px',
                              height: '40px',
                              borderRadius: '12px',
                              background: 'linear-gradient(135deg, #3498db 0%, #5dade2 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              marginLeft: '0.75rem'
                            }}>
                              <i className="fas fa-clock" style={{ color: 'white', fontSize: '0.9rem' }}></i>
                            </div>
                            <span style={{ color: '#495057', fontWeight: 500 }}>{workshop.total_hours} ساعت</span>
                          </div>
                        </div>

                        <div className="mt-auto">
                          <div 
                            className="mb-3" 
                            style={{ 
                              padding: '1.25rem', 
                              background: 'linear-gradient(135deg, #e8f4fd 0%, #d6e9fc 100%)', 
                              borderRadius: '16px',
                              border: '2px solid rgba(44, 90, 160, 0.2)'
                            }}
                          >
                            {workshop.discount_price ? (
                              <div>
                                <div className="mb-2">
                                  <span className="text-decoration-line-through" style={{ 
                                    fontSize: '0.9rem',
                                    color: '#adb5bd',
                                    fontWeight: 500
                                  }}>
                                    {parseInt(workshop.price).toLocaleString()} تومان
                                  </span>
                                  <span style={{
                                    marginRight: '0.5rem',
                                    padding: '0.25rem 0.75rem',
                                    background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                                    color: 'white',
                                    borderRadius: '12px',
                                    fontSize: '0.75rem',
                                    fontWeight: 600
                                  }}>
                                    {workshop.discount_percentage}% تخفیف
                                  </span>
                                </div>
                                <div style={{ 
                                  fontSize: '1.5rem', 
                                  fontWeight: 800,
                                  background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                                  WebkitBackgroundClip: 'text',
                                  WebkitTextFillColor: 'transparent',
                                  backgroundClip: 'text'
                                }}>
                                  {parseInt(workshop.current_price).toLocaleString()} تومان
                                </div>
                              </div>
                            ) : (
                              <div style={{ 
                                fontSize: '1.5rem', 
                                fontWeight: 800,
                                color: '#2c5aa0'
                              }}>
                                {parseInt(workshop.price).toLocaleString()} تومان
                              </div>
                            )}
                          </div>
                          <Link to={`/workshops/${workshop.slug}`} style={{ textDecoration: 'none' }}>
                            <button 
                              className="btn w-100"
                              style={{ 
                                borderRadius: '14px', 
                                padding: '0.875rem', 
                                fontWeight: 700,
                                fontSize: '1rem',
                                background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                                border: 'none',
                                color: 'white',
                                boxShadow: '0 8px 20px rgba(44, 90, 160, 0.3)',
                                transition: 'all 0.3s ease',
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-2px)';
                                e.currentTarget.style.boxShadow = '0 12px 30px rgba(44, 90, 160, 0.4)';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)';
                                e.currentTarget.style.boxShadow = '0 8px 20px rgba(44, 90, 160, 0.3)';
                              }}
                            >
                              <i className="fas fa-arrow-left me-2"></i>
                              مشاهده جزئیات
                            </button>
                          </Link>
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
              <div className="text-center mt-5">
                <Link to="/workshops" style={{ textDecoration: 'none' }}>
                  <button 
                    className="btn btn-lg"
                    style={{ 
                      borderRadius: '16px', 
                      padding: '1.125rem 3rem', 
                      fontWeight: 700,
                      fontSize: '1.1rem',
                      border: '2px solid white',
                      color: 'white',
                      background: 'transparent',
                      transition: 'all 0.3s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-3px)';
                      e.currentTarget.style.boxShadow = '0 10px 30px rgba(255, 255, 255, 0.3)';
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                      e.currentTarget.style.color = 'white';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = 'none';
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.color = 'white';
                    }}
                  >
                    <i className="fas fa-chalkboard-teacher me-2"></i>
                    مشاهده همه کارگاه‌ها
                  </button>
                </Link>
              </div>
            </>
          ) : (
            <Card style={{ 
              borderRadius: '24px', 
              border: '2px solid rgba(255, 255, 255, 0.3)', 
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 255, 0.95) 100%)',
              boxShadow: '0 15px 40px rgba(0, 0, 0, 0.2), 0 5px 15px rgba(44, 90, 160, 0.15)',
              backdropFilter: 'blur(10px)'
            }}>
              <Card.Body className="text-center" style={{ padding: '5rem 2rem' }}>
                <div 
                  style={{ 
                    width: '140px',
                    height: '140px',
                    margin: '0 auto 2rem',
                    background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 10px 30px rgba(44, 90, 160, 0.4)'
                  }}
                >
                  <i className="fas fa-chalkboard-teacher" style={{ fontSize: '4rem', color: 'white' }}></i>
                </div>
                <h5 style={{ 
                  fontSize: '1.75rem', 
                  fontWeight: 700, 
                  marginBottom: '1rem', 
                  color: '#2c3e50' 
                }}>
                  به زودی کارگاه‌های جدید
                </h5>
                <p style={{ 
                  fontSize: '1.1rem', 
                  maxWidth: '500px', 
                  margin: '0 auto',
                  color: '#495057',
                  lineHeight: '1.8'
                }}>
                  در حال حاضر کارگاهی برگزار نمی‌شود، به زودی کارگاه‌های جدید اضافه خواهند شد
                </p>
              </Card.Body>
            </Card>
          )}
        </Container>
      </section>

      {/* Packages Section */}
      <section style={{ 
        padding: '6rem 0', 
        background: 'linear-gradient(135deg, #f8f9fa 0%, #ffffff 50%, #f8f9fa 100%)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Decorative background elements */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 10% 20%, rgba(91, 143, 212, 0.05) 0%, transparent 50%), radial-gradient(circle at 90% 80%, rgba(52, 152, 219, 0.05) 0%, transparent 50%)',
          pointerEvents: 'none'
        }}></div>
        <Container style={{ position: 'relative', zIndex: 1 }}>
          <div
            className="text-center mb-5 mx-auto"
            style={{ maxWidth: '720px' }}
          >
            <div style={{
              display: 'inline-block',
              padding: '0.5rem 1.5rem',
              background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
              borderRadius: '50px',
              color: 'white',
              fontSize: '0.9rem',
              fontWeight: 600,
              boxShadow: '0 4px 15px rgba(91, 143, 212, 0.3)',
              marginBottom: '1.5rem'
            }}>
              <i className="fas fa-box-open me-2"></i>
              بسته‌های ویژه
            </div>
            <h2 style={{ 
              fontSize: '3rem', 
              fontWeight: 800, 
              marginBottom: '1rem',
              color: '#2c3e50',
              lineHeight: '1.2'
            }}>
              بسته‌های آموزشی
            </h2>
            <p className="lead" style={{ 
              fontSize: '1.2rem', 
              maxWidth: '700px', 
              margin: '0 auto',
              color: '#6c757d',
              lineHeight: '1.8'
            }}>
              با خرید بسته‌های ویژه تا 50% صرفه‌جویی کنید
            </p>
          </div>
          
          {packagesLoading ? (
            <div className="text-center" style={{ padding: '5rem 0' }}>
              <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
                <span className="visually-hidden">در حال بارگذاری...</span>
              </div>
              <p className="text-muted mt-3" style={{ fontSize: '1.05rem' }}>در حال بارگذاری بسته‌ها...</p>
            </div>
          ) : packages.length > 0 ? (
            <Row className="align-items-stretch g-5 flex-column flex-lg-row">
              <Col
                lg={7}
                className={`order-2 order-lg-1`}
              >
                <Row
                  className={`g-4 ${packageCount <= 2 ? 'justify-content-center' : ''}`}
                >
                  {packages.map((pkg) => {
                    const isSinglePackage = packageCount === 1;
                    const isDoublePackage = packageCount === 2;
                    return (
                      <Col
                        key={pkg.id}
                        xs={12}
                        md={isSinglePackage ? 10 : 6}
                        lg={isSinglePackage ? 10 : isDoublePackage ? 6 : 6}
                        xl={isSinglePackage ? 9 : isDoublePackage ? 5 : 4}
                        className={`d-flex ${isSinglePackage ? 'justify-content-center' : ''}`}
                      >
                        <Card 
                          className="h-100"
                          style={{
                            border: 'none',
                            borderRadius: '24px',
                            overflow: 'hidden',
                            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                            cursor: 'pointer',
                            background: 'white',
                            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
                            width: '100%',
                            maxWidth: isSinglePackage ? '420px' : '100%',
                            margin: '0 auto',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-12px)';
                            e.currentTarget.style.boxShadow = '0 20px 50px rgba(91, 143, 212, 0.25)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
                          }}
                        >
                          {pkg.thumbnail ? (
                            <div style={{ 
                              overflow: 'hidden', 
                              position: 'relative',
                              height: '240px',
                              background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)'
                            }}>
                              <Card.Img
                                variant="top"
                                src={pkg.thumbnail}
                                alt={pkg.title}
                                loading="lazy"
                                style={{ 
                                  height: '100%', 
                                  width: '100%',
                                  objectFit: 'cover', 
                                  transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                              />
                              {pkg.is_featured && (
                                <div style={{
                                  position: 'absolute',
                                  top: '1rem',
                                  left: '1rem',
                                  background: 'linear-gradient(135deg, #2980b9 0%, #3498db 100%)',
                                  padding: '0.5rem 1rem',
                                  borderRadius: '20px',
                                  fontSize: '0.85rem',
                                  fontWeight: 600,
                                  color: 'white',
                                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
                                }}>
                                  <i className="fas fa-star me-1"></i>
                                  پیشنهاد ویژه
                                </div>
                              )}
                            </div>
                          ) : (
                            <div style={{ 
                              height: '240px',
                              background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              position: 'relative'
                            }}>
                              <i className="fas fa-box-open" style={{ fontSize: '4rem', color: 'rgba(255, 255, 255, 0.8)' }}></i>
                              {pkg.is_featured && (
                                <div style={{
                                  position: 'absolute',
                                  top: '1rem',
                                  left: '1rem',
                                  background: 'linear-gradient(135deg, #2980b9 0%, #3498db 100%)',
                                  padding: '0.5rem 1rem',
                                  borderRadius: '20px',
                                  fontSize: '0.85rem',
                                  fontWeight: 600,
                                  color: 'white',
                                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
                                }}>
                                  <i className="fas fa-star me-1"></i>
                                  پیشنهاد ویژه
                                </div>
                              )}
                            </div>
                          )}
                          <Card.Body className="d-flex flex-column" style={{ padding: '2rem' }}>
                            <Card.Title className="mb-3" style={{ 
                              fontSize: '1.35rem', 
                              fontWeight: 700, 
                              lineHeight: '1.4',
                              color: '#2c3e50',
                              minHeight: '3.8rem'
                            }}>
                              {pkg.title}
                            </Card.Title>
                            <Card.Text className="mb-4" style={{ 
                              fontSize: '1rem', 
                              lineHeight: '1.7',
                              color: '#6c757d',
                              flex: '1'
                            }}>
                              {pkg.short_description}
                            </Card.Text>
                            
                            <div className="mb-4" style={{ flex: '1' }}>
                              <div className="d-flex align-items-center mb-3" style={{ fontSize: '0.95rem' }}>
                                <div style={{
                                  width: '40px',
                                  height: '40px',
                                  borderRadius: '12px',
                                  background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  marginLeft: '0.75rem'
                                }}>
                                  <i className="fas fa-book" style={{ color: 'white', fontSize: '0.9rem' }}></i>
                                </div>
                                <span style={{ color: '#495057', fontWeight: 500 }}>{pkg.total_courses || 0} دوره آموزشی</span>
                              </div>
                              {pkg.total_hours > 0 && (
                                <div className="d-flex align-items-center mb-3" style={{ fontSize: '0.95rem' }}>
                                  <div style={{
                                    width: '40px',
                                    height: '40px',
                                    borderRadius: '12px',
                                    background: 'linear-gradient(135deg, #3498db 0%, #5dade2 100%)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    marginLeft: '0.75rem'
                                  }}>
                                    <i className="fas fa-clock" style={{ color: 'white', fontSize: '0.9rem' }}></i>
                                  </div>
                                  <span style={{ color: '#495057', fontWeight: 500 }}>{pkg.total_hours} ساعت محتوا</span>
                                </div>
                              )}
                              {pkg.savings_percentage > 0 && (
                                <div 
                                  style={{ 
                                    background: 'linear-gradient(135deg, #d6e8f5 0%, #c8dff0 100%)',
                                    padding: '0.75rem 1rem',
                                    borderRadius: '12px',
                                    fontSize: '0.9rem',
                                    fontWeight: 600,
                                    color: '#1e4d72',
                                    border: '2px solid #c8dff0',
                                    marginBottom: '0.5rem',
                                  }}
                                >
                                  <i className="fas fa-percentage me-1"></i>
                                  {pkg.savings_percentage}% صرفه‌جویی
                                </div>
                              )}
                            </div>

                            <div className="mt-auto">
                              <div 
                                className="mb-3" 
                                style={{ 
                                  padding: '1.25rem', 
                                  background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)', 
                                  borderRadius: '16px',
                                  border: '2px solid #e9ecef'
                                }}
                              >
                                {pkg.discount_price ? (
                                  <div>
                                    <div className="mb-2">
                                      <span className="text-decoration-line-through" style={{ 
                                        fontSize: '0.9rem',
                                        color: '#adb5bd',
                                        fontWeight: 500
                                      }}>
                                        {parseInt(pkg.price).toLocaleString()} تومان
                                      </span>
                                      <span style={{
                                        marginRight: '0.5rem',
                                        padding: '0.25rem 0.75rem',
                                        background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                                        color: 'white',
                                        borderRadius: '12px',
                                        fontSize: '0.75rem',
                                        fontWeight: 600
                                      }}>
                                        {pkg.discount_percentage}% تخفیف
                                      </span>
                                    </div>
                                    <div style={{ 
                                      fontSize: '1.5rem', 
                                      fontWeight: 800,
                                      background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                                      WebkitBackgroundClip: 'text',
                                      WebkitTextFillColor: 'transparent',
                                      backgroundClip: 'text'
                                    }}>
                                      {parseInt(pkg.current_price).toLocaleString()} تومان
                                    </div>
                                  </div>
                                ) : (
                                  <div style={{ 
                                    fontSize: '1.5rem', 
                                    fontWeight: 800,
                                    color: '#2c5aa0'
                                  }}>
                                    {parseInt(pkg.price).toLocaleString()} تومان
                                  </div>
                                )}
                              </div>
                              <Link to={`/packages/${pkg.slug}`} style={{ textDecoration: 'none' }}>
                                <button 
                                  className="btn w-100"
                                  style={{ 
                                    borderRadius: '14px', 
                                    padding: '0.875rem', 
                                    fontWeight: 700,
                                    fontSize: '1rem',
                                    background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                                    border: 'none',
                                    color: 'white',
                                    boxShadow: '0 8px 20px rgba(91, 143, 212, 0.3)',
                                    transition: 'all 0.3s ease',
                                  }}
                                  onMouseEnter={(e) => {
                                    e.currentTarget.style.transform = 'translateY(-2px)';
                                    e.currentTarget.style.boxShadow = '0 12px 30px rgba(91, 143, 212, 0.4)';
                                  }}
                                  onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    e.currentTarget.style.boxShadow = '0 8px 20px rgba(91, 143, 212, 0.3)';
                                  }}
                                >
                                  <i className="fas fa-arrow-left me-2"></i>
                                  مشاهده بسته
                                </button>
                              </Link>
                            </div>
                          </Card.Body>
                        </Card>
                      </Col>
                    );
                  })}
                </Row>
                <div className="text-center mt-5">
                  <Link to="/packages" style={{ textDecoration: 'none' }}>
                    <button 
                      className="btn btn-lg"
                      style={{ 
                        borderRadius: '16px', 
                        padding: '1.125rem 3rem', 
                        fontWeight: 700,
                        fontSize: '1.1rem',
                        border: '2px solid #5b8fd4',
                        color: '#5b8fd4',
                        background: 'transparent',
                        transition: 'all 0.3s ease',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-3px)';
                        e.currentTarget.style.boxShadow = '0 10px 30px rgba(91, 143, 212, 0.3)';
                        e.currentTarget.style.background = '#5b8fd4';
                        e.currentTarget.style.color = 'white';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = 'none';
                        e.currentTarget.style.background = 'transparent';
                        e.currentTarget.style.color = '#5b8fd4';
                      }}
                    >
                      <i className="fas fa-box-open me-2"></i>
                      مشاهده همه بسته‌ها
                    </button>
                  </Link>
                </div>
              </Col>
              <Col lg={5} className="order-1 order-lg-2">
                <div
                  style={{
                    position: 'relative',
                    borderRadius: '28px',
                    background: 'linear-gradient(180deg, rgba(91, 143, 212, 0.12) 0%, rgba(255, 255, 255, 0.95) 100%)',
                    boxShadow: '0 25px 60px rgba(91, 143, 212, 0.18)',
                    padding: '2.5rem 2.25rem',
                    overflow: 'hidden',
                    border: '1px solid rgba(91, 143, 212, 0.15)',
                    height: '100%',
                  }}
                >
                  <div
                    style={{
                      position: 'absolute',
                      top: '-60px',
                      left: '-60px',
                      width: '200px',
                      height: '200px',
                      background: 'radial-gradient(circle, rgba(91, 143, 212, 0.35) 0%, rgba(91, 143, 212, 0) 65%)'
                    }}
                  ></div>
                  <div
                    style={{
                      position: 'absolute',
                      bottom: '-80px',
                      right: '-80px',
                      width: '240px',
                      height: '240px',
                      background: 'radial-gradient(circle, rgba(122, 163, 224, 0.3) 0%, rgba(122, 163, 224, 0) 70%)'
                    }}
                  ></div>
                  <div style={{ position: 'relative', zIndex: 1 }}>
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.45rem 1.25rem',
                        borderRadius: '999px',
                        background: 'rgba(91, 143, 212, 0.15)',
                        color: '#1f2a44',
                        fontWeight: 600,
                        fontSize: '0.9rem',
                        marginBottom: '1.5rem'
                      }}
                    >
                      <i className="fas fa-magic"></i>
                      چرا بسته‌های آموزشی؟
                    </div>
                    <h3
                      style={{
                        fontSize: '2rem',
                        fontWeight: 800,
                        marginBottom: '1rem',
                        color: '#1f2a44',
                        lineHeight: '1.5'
                      }}
                    >
                      مسیر یادگیری منسجم برای رسیدن به نتیجه
                    </h3>
                    <p
                      style={{
                        fontSize: '1rem',
                        color: '#4a5875',
                        lineHeight: '1.8',
                        marginBottom: '2rem'
                      }}
                    >
                      بسته‌ها مجموعه‌ای گلچین‌شده از دوره‌ها و تمرین‌های مکمل هستند تا بدون سردرگمی، گام‌به‌گام پیش بروید و سریع‌تر به هدف آموزشی خود برسید.
                    </p>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: '1rem' }}>
                      {packageHighlightItems.map((item) => (
                        <li
                          key={item.text}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            background: 'rgba(91, 143, 212, 0.08)',
                            borderRadius: '14px',
                            padding: '0.85rem 1rem',
                            color: '#1f2a44',
                            fontWeight: 500,
                          }}
                        >
                          <span
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              width: '38px',
                              height: '38px',
                              borderRadius: '12px',
                              background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                              color: 'white',
                              flexShrink: 0,
                              boxShadow: '0 8px 18px rgba(91, 143, 212, 0.3)',
                            }}
                          >
                            <i className={`fas ${item.icon}`} style={{ fontSize: '1rem' }}></i>
                          </span>
                          <span>{item.text}</span>
                        </li>
                      ))}
                    </ul>
                    <div className="d-flex flex-wrap gap-3 mt-4">
                      <Link 
                        to="/packages" 
                        className="btn"
                        style={{ 
                          borderRadius: '14px', 
                          padding: '0.85rem 1.75rem', 
                          fontWeight: 700,
                          fontSize: '1rem',
                          background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                          border: 'none',
                          color: 'white',
                          boxShadow: '0 12px 25px rgba(91, 143, 212, 0.3)',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.transform = 'translateY(-2px)';
                          e.currentTarget.style.boxShadow = '0 18px 35px rgba(91, 143, 212, 0.4)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = 'translateY(0)';
                          e.currentTarget.style.boxShadow = '0 12px 25px rgba(91, 143, 212, 0.3)';
                        }}
                      >
                        <i className="fas fa-box-open ms-2"></i>
                        شروع انتخاب بسته
                      </Link>
                      <Link 
                        to="/courses" 
                        className="btn"
                        style={{ 
                          borderRadius: '14px', 
                          padding: '0.85rem 1.75rem', 
                          fontWeight: 700,
                          fontSize: '1rem',
                          background: 'rgba(91, 143, 212, 0.08)',
                          border: '1px solid rgba(91, 143, 212, 0.2)',
                          color: '#1f2a44',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = 'rgba(91, 143, 212, 0.16)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'rgba(91, 143, 212, 0.08)';
                        }}
                      >
                        <i className="fas fa-clipboard-check ms-2"></i>
                        مقایسه دوره‌ها
                      </Link>
                    </div>
                  </div>
                </div>
              </Col>
            </Row>
          ) : (
            <Card style={{ 
              borderRadius: '24px', 
              border: 'none', 
              background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
              boxShadow: '0 10px 30px rgba(0, 0, 0, 0.08)'
            }}>
              <Card.Body className="text-center" style={{ padding: '5rem 2rem' }}>
                <div 
                  style={{ 
                    width: '140px',
                    height: '140px',
                    margin: '0 auto 2rem',
                    background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 10px 30px rgba(91, 143, 212, 0.3)'
                  }}
                >
                  <i className="fas fa-box-open" style={{ fontSize: '4rem', color: 'white' }}></i>
                </div>
                <h5 style={{ 
                  fontSize: '1.75rem', 
                  fontWeight: 700, 
                  marginBottom: '1rem', 
                  color: '#2c3e50' 
                }}>
                  به زودی بسته‌های جدید
                </h5>
                <p style={{ 
                  fontSize: '1.1rem', 
                  maxWidth: '500px', 
                  margin: '0 auto',
                  color: '#6c757d',
                  lineHeight: '1.8'
                }}>
                  در حال حاضر بسته‌ای موجود نیست، به زودی بسته‌های جدید اضافه خواهند شد
                </p>
              </Card.Body>
            </Card>
          )}
        </Container>
      </section>

      {/* Professional Experience Section */}
      <section className="professional-experience-section" style={{ 
        padding: '6rem 0', 
        background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 50%, #5dade2 100%)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Decorative background pattern */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 0%, transparent 50%)',
          pointerEvents: 'none'
        }}></div>
        <Container style={{ position: 'relative', zIndex: 1 }}>
          {/* Section Header */}
          <Row className="mb-5">
            <Col lg={8} className="mx-auto text-center">
              <div className="section-badge mb-3" style={{
                display: 'inline-block',
                padding: '0.5rem 1.5rem',
                background: 'rgba(255, 255, 255, 0.95)',
                borderRadius: '50px',
                color: '#2c5aa0',
                fontSize: '0.9rem',
                fontWeight: 600,
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)'
              }}>
                  <i className="fas fa-star me-2"></i>
                  چرا ما را انتخاب کنید؟
                </div>
              <h2 className="mb-4" style={{
                fontSize: '3rem',
                fontWeight: 800,
                color: 'white',
                lineHeight: '1.2',
                textShadow: '0 2px 10px rgba(0, 0, 0, 0.2)'
              }}>
                تجربه‌ای متفاوت در{' '}
                <span style={{
                  color: '#fff',
                  textShadow: '0 2px 20px rgba(255, 255, 255, 0.5)'
                }}>روانشناسی</span>
                </h2>
              <p className="lead" style={{ 
                fontSize: '1.2rem', 
                lineHeight: '1.8', 
                maxWidth: '600px', 
                margin: '0 auto',
                color: 'rgba(255, 255, 255, 0.95)',
                textShadow: '0 1px 5px rgba(0, 0, 0, 0.1)'
              }}>
                  با تیمی از متخصصان مجرب و روش‌های نوین درمان، 
                مسیر رشد و بهبود شخصی شما را هموار می‌کنیم
              </p>
            </Col>
          </Row>

          {/* Main Features Grid */}
          <Row className="g-4 mb-5">
            <Col md={6} lg={4}>
              <Link to="/tests" className="text-decoration-none">
                <Card className="h-100 feature-service-card" style={{
                  border: 'none',
                  borderRadius: '20px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  cursor: 'pointer',
                  background: 'linear-gradient(135deg, #ffffff 0%, #e8f4fd 100%)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
                }}>
                  <Card.Body style={{ padding: '2rem' }}>
                    <div className="feature-icon-wrapper mb-3" style={{
                      width: '70px',
                      height: '70px',
                      borderRadius: '18px',
                      background: 'linear-gradient(135deg, #2980b9 0%, #3498db 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 20px rgba(41, 128, 185, 0.4)'
                    }}>
                      <i className="fas fa-brain" style={{ fontSize: '2rem', color: 'white' }}></i>
                    </div>
                    <h5 className="mb-3" style={{ fontWeight: 700, color: '#1a1a1a' }}>تست‌های روانشناسی</h5>
                    <p className="mb-0" style={{ lineHeight: '1.7', color: '#4a4a4a' }}>
                      تست‌های معتبر و علمی برای شناخت بهتر خود و بهبود سلامت روان
                    </p>
                  </Card.Body>
                </Card>
              </Link>
            </Col>

            <Col md={6} lg={4}>
              <Link to="/courses" className="text-decoration-none">
                <Card className="h-100 feature-service-card" style={{
                  border: 'none',
                  borderRadius: '20px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  cursor: 'pointer',
                  background: 'linear-gradient(135deg, #ffffff 0%, #e8f4fd 100%)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
                }}>
                  <Card.Body style={{ padding: '2rem' }}>
                    <div className="feature-icon-wrapper mb-3" style={{
                      width: '70px',
                      height: '70px',
                      borderRadius: '18px',
                      background: 'linear-gradient(135deg, #3498db 0%, #5dade2 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 20px rgba(52, 152, 219, 0.4)'
                    }}>
                      <i className="fas fa-graduation-cap" style={{ fontSize: '2rem', color: 'white' }}></i>
                    </div>
                    <h5 className="mb-3" style={{ fontWeight: 700, color: '#1a1a1a' }}>دوره‌های آموزشی</h5>
                    <p className="mb-0" style={{ lineHeight: '1.7', color: '#4a4a4a' }}>
                      دوره‌های تخصصی روانشناسی و مشاوره برای رشد شخصی و حرفه‌ای
                    </p>
                  </Card.Body>
                </Card>
              </Link>
            </Col>

            <Col md={6} lg={4}>
              <Link to="/workshops" className="text-decoration-none">
                <Card className="h-100 feature-service-card" style={{
                  border: 'none',
                  borderRadius: '20px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  cursor: 'pointer',
                  background: 'linear-gradient(135deg, #ffffff 0%, #e8f4fd 100%)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
                }}>
                  <Card.Body style={{ padding: '2rem' }}>
                    <div className="feature-icon-wrapper mb-3" style={{
                      width: '70px',
                      height: '70px',
                      borderRadius: '18px',
                      background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 20px rgba(44, 90, 160, 0.4)'
                    }}>
                      <i className="fas fa-chalkboard-teacher" style={{ fontSize: '2rem', color: 'white' }}></i>
                  </div>
                    <h5 className="mb-3" style={{ fontWeight: 700, color: '#1a1a1a' }}>کارگاه‌های تخصصی</h5>
                    <p className="mb-0" style={{ lineHeight: '1.7', color: '#4a4a4a' }}>
                      کارگاه‌های تعاملی و کاربردی برای یادگیری عملی مهارت‌های روانشناسی
                    </p>
                  </Card.Body>
                </Card>
              </Link>
            </Col>

            <Col md={6} lg={4}>
              <Link to="/packages" className="text-decoration-none">
                <Card className="h-100 feature-service-card" style={{
                  border: 'none',
                  borderRadius: '20px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  cursor: 'pointer',
                  background: 'linear-gradient(135deg, #ffffff 0%, #e8f4fd 100%)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
                }}>
                  <Card.Body style={{ padding: '2rem' }}>
                    <div className="feature-icon-wrapper mb-3" style={{
                      width: '70px',
                      height: '70px',
                      borderRadius: '18px',
                      background: 'linear-gradient(135deg, #5b8fd4 0%, #7aa3e0 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 20px rgba(91, 143, 212, 0.4)'
                    }}>
                      <i className="fas fa-box-open" style={{ fontSize: '2rem', color: 'white' }}></i>
                    </div>
                    <h5 className="mb-3" style={{ fontWeight: 700, color: '#1a1a1a' }}>پکیج های آموزشی</h5>
                    <p className="mb-0" style={{ lineHeight: '1.7', color: '#4a4a4a' }}>
                      بسته‌های جامع و مقرون به صرفه برای دسترسی به تمام خدمات
                    </p>
                  </Card.Body>
                </Card>
              </Link>
            </Col>

            <Col md={6} lg={4}>
              <Link to="/therapists" className="text-decoration-none">
                <Card className="h-100 feature-service-card" style={{
                  border: 'none',
                  borderRadius: '20px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  cursor: 'pointer',
                  background: 'linear-gradient(135deg, #ffffff 0%, #e8f4fd 100%)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
                }}>
                  <Card.Body style={{ padding: '2rem' }}>
                    <div className="feature-icon-wrapper mb-3" style={{
                      width: '70px',
                      height: '70px',
                      borderRadius: '18px',
                      background: 'linear-gradient(135deg, #3498db 0%, #5dade2 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 20px rgba(52, 152, 219, 0.4)'
                    }}>
                      <i className="fas fa-user-md" style={{ fontSize: '2rem', color: 'white' }}></i>
                    </div>
                    <h5 className="mb-3" style={{ fontWeight: 700, color: '#1a1a1a' }}>درمانگران متخصص</h5>
                    <p className="mb-0" style={{ lineHeight: '1.7', color: '#4a4a4a' }}>
                      تیمی از بهترین روانشناسان و مشاوران مجرب کشور در خدمت شما
                    </p>
                  </Card.Body>
                </Card>
              </Link>
            </Col>

            <Col md={6} lg={4}>
              <Link to="/blog" className="text-decoration-none">
                <Card className="h-100 feature-service-card" style={{
                  border: 'none',
                  borderRadius: '20px',
                  overflow: 'hidden',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                  cursor: 'pointer',
                  background: 'linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.boxShadow = '0 20px 50px rgba(0, 0, 0, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
                }}>
                  <Card.Body style={{ padding: '2rem' }}>
                    <div className="feature-icon-wrapper mb-3" style={{
                      width: '70px',
                      height: '70px',
                      borderRadius: '18px',
                      background: 'linear-gradient(135deg, #0984e3 0%, #74b9ff 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 20px rgba(9, 132, 227, 0.4)'
                    }}>
                      <i className="fas fa-newspaper" style={{ fontSize: '2rem', color: 'white' }}></i>
                    </div>
                    <h5 className="mb-3" style={{ fontWeight: 700, color: '#1a1a1a' }}>مقالات تخصصی</h5>
                    <p className="mb-0" style={{ lineHeight: '1.7', color: '#4a4a4a' }}>
                      آخرین مقالات و مطالب روانشناسی از متخصصان برجسته
                    </p>
                  </Card.Body>
                </Card>
              </Link>
            </Col>
          </Row>

          {/* CTA Buttons */}
          <Row>
            <Col className="text-center">
              <div className="d-flex flex-wrap justify-content-center gap-3">
                <Link to="/therapists" className="btn btn-lg px-5 py-3" style={{
                  borderRadius: '15px',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  background: 'white',
                  color: '#2c5aa0',
                  border: 'none',
                  boxShadow: '0 8px 25px rgba(0, 0, 0, 0.3)',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-3px)';
                  e.currentTarget.style.boxShadow = '0 12px 35px rgba(0, 0, 0, 0.4)';
                  e.currentTarget.style.background = '#f8f9fa';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.3)';
                  e.currentTarget.style.background = 'white';
                }}>
                    <i className="fas fa-calendar-check me-2"></i>
                  رزرو نوبت مشاوره
                  </Link>
                <Link to="/tests" className="btn btn-lg px-5 py-3" style={{
                  borderRadius: '15px',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderWidth: '2px',
                  borderColor: 'white',
                  color: 'white',
                  background: 'transparent',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-3px)';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                  e.currentTarget.style.borderColor = 'white';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = 'white';
                }}>
                    <i className="fas fa-brain me-2"></i>
                  تست روانشناسی رایگان
                  </Link>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Latest Posts Section */}
      <section style={{ 
        padding: '6rem 0', 
        background: 'linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%)',
        position: 'relative'
      }}>
        <Container>
          {/* Section Header */}
          <div className="mb-5">
            <div className="d-flex align-items-center">
              <div 
                style={{
                  width: '60px',
                  height: '60px',
                  borderRadius: '16px',
                  background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginLeft: '1rem',
                  boxShadow: '0 8px 20px rgba(44, 90, 160, 0.25)'
                }}
              >
                <i className="fas fa-newspaper" style={{ fontSize: '1.75rem', color: 'white' }}></i>
              </div>
              <div>
                <h2 style={{ 
                  fontSize: '2.75rem', 
                  fontWeight: 800, 
                  marginBottom: '0.5rem',
                  color: '#1a1a1a',
                  lineHeight: '1.2'
                }}>
                  {t('home.latest_posts')}
                </h2>
                <p style={{ 
                  fontSize: '1.1rem', 
                  color: '#6c757d',
                  margin: 0,
                  lineHeight: '1.6'
                }}>
                  آخرین مقالات و مطالب روانشناسی
                </p>
              </div>
            </div>
          </div>

          {/* Articles and Newsletter Side by Side */}
          <Row className="align-items-start">
            {/* Articles Section */}
            <Col lg={8}>
              {postsLoading ? (
                <div className="text-center" style={{ padding: '4rem 0' }}>
                  <div 
                    className="spinner-border" 
                    role="status" 
                    style={{ 
                      width: '3rem', 
                      height: '3rem',
                      borderWidth: '4px',
                      borderColor: '#2c5aa0',
                      borderRightColor: 'transparent'
                    }}
                  >
                    <span className="visually-hidden">{t('common.loading')}</span>
                  </div>
                  <p className="text-muted mt-3" style={{ fontSize: '1.05rem' }}>در حال بارگذاری مقالات...</p>
                </div>
              ) : (
                <>
                  <Row className="g-4">
                    {Array.isArray(posts) && posts.map((post: Post) => (
                      <Col md={6} key={post.id}>
                        <Card 
                          className="h-100"
                          style={{
                            border: '2px solid #2c5aa0',
                            borderRadius: '20px',
                            overflow: 'hidden',
                            transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                            cursor: 'pointer',
                            background: '#ffffff',
                            boxShadow: '0 4px 20px rgba(44, 90, 160, 0.1)',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-10px)';
                            e.currentTarget.style.boxShadow = '0 20px 50px rgba(44, 90, 160, 0.2)';
                            e.currentTarget.style.borderColor = '#3498db';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 4px 20px rgba(44, 90, 160, 0.1)';
                            e.currentTarget.style.borderColor = '#2c5aa0';
                          }}
                        >
                          {post.featured_image && (
                            <div style={{ 
                              overflow: 'hidden', 
                              position: 'relative',
                              height: '240px',
                              background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)'
                            }}>
                              <Card.Img 
                                variant="top" 
                                src={post.featured_image} 
                                alt={post.title}
                                loading="lazy"
                                style={{ 
                                  height: '100%', 
                                  width: '100%',
                                  objectFit: 'cover', 
                                  transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)' 
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                                onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                              />
                            </div>
                          )}
                          <Card.Body style={{ padding: '2rem' }}>
                            <div className="d-flex align-items-center justify-content-between mb-3">
                              <span 
                                className="badge" 
                                style={{ 
                                  fontSize: '0.85rem', 
                                  padding: '0.5rem 1rem', 
                                  borderRadius: '20px',
                                  background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                                  color: 'white',
                                  fontWeight: 600,
                                  boxShadow: '0 4px 12px rgba(44, 90, 160, 0.25)'
                                }}
                              >
                                {post.category.name}
                              </span>
                              <small style={{ 
                                fontSize: '0.85rem',
                                color: '#6c757d',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.25rem'
                              }}>
                                <i className="fas fa-calendar" style={{ color: '#adb5bd' }}></i>
                                {post.created_at_persian}
                              </small>
                            </div>
                            <Card.Title style={{ 
                              fontSize: '1.35rem', 
                              fontWeight: 700, 
                              lineHeight: '1.5', 
                              marginBottom: '1rem',
                              color: '#1a1a1a',
                              minHeight: '4rem'
                            }}>
                              <Link 
                                to={`/blog/post/${post.slug}`} 
                                className="text-decoration-none"
                                style={{ 
                                  color: '#1a1a1a',
                                  transition: 'color 0.3s ease',
                                  display: 'block'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.color = '#2c5aa0'}
                                onMouseLeave={(e) => e.currentTarget.style.color = '#1a1a1a'}
                              >
                                {post.title}
                              </Link>
                            </Card.Title>
                            <Card.Text style={{ 
                              fontSize: '0.95rem', 
                              lineHeight: '1.8', 
                              marginBottom: '1.5rem',
                              color: '#6c757d',
                              minHeight: '3.5rem'
                            }}>
                              {post.excerpt}
                            </Card.Text>
                            <div 
                              className="d-flex justify-content-between align-items-center" 
                              style={{ 
                                paddingTop: '1.25rem', 
                                borderTop: '2px solid #f0f0f0',
                                marginTop: 'auto'
                              }}
                            >
                              <small style={{ 
                                fontSize: '0.85rem',
                                color: '#6c757d',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.4rem'
                              }}>
                                <i className="fas fa-user" style={{ color: '#adb5bd' }}></i>
                                {post.author_name}
                              </small>
                              <small style={{ 
                                fontSize: '0.85rem',
                                color: '#6c757d',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.4rem'
                              }}>
                                <i className="fas fa-eye" style={{ color: '#adb5bd' }}></i>
                                {post.view_count.toLocaleString()}
                              </small>
                            </div>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </>
              )}
            </Col>
            
            {/* Newsletter Signup */}
            <Col lg={4}>
              <Card 
                style={{
                  border: '2px solid #2c5aa0',
                  borderRadius: '20px',
                  background: 'white',
                  color: '#2c3e50',
                  boxShadow: '0 10px 30px rgba(44, 90, 160, 0.15)',
                  position: 'sticky',
                  top: '2rem'
                }}
              >
                <Card.Body className="text-center" style={{ padding: '2.5rem 2rem' }}>
                  <div 
                    style={{ 
                      width: '80px',
                      height: '80px',
                      margin: '0 auto 1.5rem',
                      background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: '0 8px 20px rgba(44, 90, 160, 0.3)',
                    }}
                  >
                    <i className="fas fa-envelope" style={{ fontSize: '2rem', color: 'white' }}></i>
                  </div>
                  <h5 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem', color: '#2c3e50' }}>
                    {t('home.newsletter.title')}
                  </h5>
                  <p style={{ fontSize: '0.95rem', marginBottom: '2rem', color: '#6c757d', lineHeight: '1.6' }}>
                    {t('home.newsletter.desc')}
                  </p>
                  <Form onSubmit={handleNewsletterSubmit}>
                    <InputGroup className="mb-3">
                      <Form.Control
                        type="email"
                        placeholder={t('home.newsletter.placeholder')}
                        value={newsletterEmail}
                        onChange={(e) => setNewsletterEmail(e.target.value)}
                        required
                        style={{
                          borderRadius: '10px 0 0 10px',
                          border: '1px solid #dee2e6',
                          padding: '0.75rem 1rem',
                          fontSize: '0.95rem',
                          backgroundColor: '#f8f9fa',
                        }}
                      />
                      <Button 
                        variant="light" 
                        type="submit"
                        style={{
                          borderRadius: '0 10px 10px 0',
                          border: 'none',
                          padding: '0.75rem 1.5rem',
                          fontWeight: 600,
                          color: '#2c5aa0',
                          transition: 'all 0.3s ease',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = '#f8f9fa';
                          e.currentTarget.style.transform = 'scale(1.02)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'white';
                          e.currentTarget.style.transform = 'scale(1)';
                        }}
                      >
                        <i className="fas fa-paper-plane ms-1"></i>
                        {t('home.newsletter.subscribe')}
                      </Button>
                    </InputGroup>
                  </Form>
                </Card.Body>
              </Card>
              
              {/* View All Articles Button */}
              <div className="text-center mt-4">
                <Link to="/blog" style={{ textDecoration: 'none' }}>
                  <button 
                    className="btn btn-lg w-100"
                    style={{ 
                      borderRadius: '14px', 
                      padding: '1rem 2.5rem', 
                      fontWeight: 700,
                      fontSize: '1.05rem',
                      background: 'white',
                      border: '2px solid #2c5aa0',
                      color: '#2c5aa0',
                      boxShadow: '0 8px 25px rgba(44, 90, 160, 0.15)',
                      transition: 'all 0.3s ease',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-3px)';
                      e.currentTarget.style.background = 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)';
                      e.currentTarget.style.color = 'white';
                      e.currentTarget.style.boxShadow = '0 12px 35px rgba(44, 90, 160, 0.4)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.background = 'white';
                      e.currentTarget.style.color = '#2c5aa0';
                      e.currentTarget.style.boxShadow = '0 8px 25px rgba(44, 90, 160, 0.15)';
                    }}
                  >
                    <i className="fas fa-newspaper"></i>
                    مشاهده همه مقالات
                  </button>
                </Link>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
    </>
  );
};

export default Home;
