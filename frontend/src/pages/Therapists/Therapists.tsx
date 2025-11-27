import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, InputGroup, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';
import axios from 'axios';

interface Therapist {
  id: number;
  name: string;
  specialization: string;
  experience_years: number;
  hourly_rate: number;
  profile_image?: string;
  bio?: string;
  license_number?: string;
  is_verified?: boolean;
  is_available?: boolean;
  gender?: string;
}

const Therapists: React.FC = () => {
  const { t } = useI18n();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState('');
  const [sortBy, setSortBy] = useState('name');

  // Fetch therapists data
  const { data: therapists = [], isLoading, error } = useQuery<Therapist[]>({
    queryKey: ['therapists'],
    queryFn: async () => {
      const response = await axios.get('/api/appointments/therapists/');
      return response.data;
    },
  });

  // Filter and sort therapists
  const filteredTherapists = therapists
    .filter(therapist => {
      const matchesSearch = therapist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           therapist.specialization.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesSpecialization = !selectedSpecialization || 
                                  therapist.specialization.includes(selectedSpecialization);
      return matchesSearch && matchesSpecialization;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'experience':
          return b.experience_years - a.experience_years;
        case 'rate':
          return a.hourly_rate - b.hourly_rate;
        case 'name':
        default:
          return a.name.localeCompare(b.name);
      }
    });

  // Get unique specializations for filter
  const specializations = Array.from(
    new Set(therapists.map(t => t.specialization).filter(Boolean))
  );

  if (error) {
    return (
      <Container className="py-5">
        <div className="text-center">
          <h2>خطا در بارگذاری اطلاعات</h2>
          <p>لطفاً دوباره تلاش کنید.</p>
        </div>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>تیم درمانگران - مرکز روانشناسی</title>
        <meta name="description" content="آشنایی با تیم درمانگران مجرب و متخصص مرکز روانشناسی" />
      </Helmet>

      {/* Hero Section */}
      <section 
        className="py-5" 
        style={{ 
          background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
          color: 'white'
        }}
      >
        <Container>
          <Row className="align-items-center">
            <Col lg={8}>
              <h1 className="display-4 fw-bold mb-4">
                <i className="fas fa-user-md me-3"></i>
                تیم درمانگران ما
              </h1>
              <p className="lead mb-4">
                با تیمی از متخصصان مجرب و با تجربه در زمینه‌های مختلف روانشناسی، 
                بهترین خدمات درمانی را به شما ارائه می‌دهیم.
              </p>
              <div className="d-flex flex-wrap gap-3">
                <Link to="/appointment/booking" className="btn btn-light btn-lg">
                  <i className="fas fa-calendar-check me-2"></i>
                  رزرو نوبت
                </Link>
                <Link to="/tests" className="btn btn-outline-light btn-lg">
                  <i className="fas fa-brain me-2"></i>
                  تست رایگان
                </Link>
              </div>
            </Col>
            <Col lg={4} className="text-center">
              <div 
                style={{ 
                  fontSize: '8rem', 
                  opacity: 0.3,
                  marginTop: '2rem'
                }}
              >
                <i className="fas fa-users"></i>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Search and Filter Section */}
      <section className="py-4" style={{ background: '#f8f9fa' }}>
        <Container>
          <Row className="g-3">
            <Col md={6} lg={4}>
              <InputGroup>
                <InputGroup.Text>
                  <i className="fas fa-search"></i>
                </InputGroup.Text>
                <Form.Control
                  type="text"
                  placeholder="جستجو در نام یا تخصص درمانگر..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </InputGroup>
            </Col>
            <Col md={6} lg={3}>
              <Form.Select
                value={selectedSpecialization}
                onChange={(e) => setSelectedSpecialization(e.target.value)}
              >
                <option value="">همه تخصص‌ها</option>
                {specializations.map(spec => (
                  <option key={spec} value={spec}>{spec}</option>
                ))}
              </Form.Select>
            </Col>
            <Col md={6} lg={3}>
              <Form.Select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="name">مرتب‌سازی بر اساس نام</option>
                <option value="experience">مرتب‌سازی بر اساس تجربه</option>
                <option value="rate">مرتب‌سازی بر اساس نرخ</option>
              </Form.Select>
            </Col>
            <Col md={6} lg={2}>
              <div className="d-flex align-items-center h-100">
                <small className="text-muted">
                  {filteredTherapists.length} درمانگر یافت شد
                </small>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Therapists Grid */}
      <section className="py-5">
        <Container>
          {isLoading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
                <span className="visually-hidden">در حال بارگذاری...</span>
              </div>
              <p className="text-muted mt-3">در حال بارگذاری درمانگران...</p>
            </div>
          ) : filteredTherapists.length > 0 ? (
            <Row className="g-4">
              {filteredTherapists.map((therapist) => (
                <Col key={therapist.id} md={6} lg={4} xl={3}>
                  <Card 
                    className="h-100"
                    style={{
                      border: 'none',
                      borderRadius: '18px',
                      overflow: 'hidden',
                      transition: 'all 0.4s ease',
                      cursor: 'pointer',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-10px)';
                      e.currentTarget.style.boxShadow = '0 20px 50px rgba(0,0,0,0.15)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 5px 15px rgba(0,0,0,0.08)';
                    }}
                  >
                    {/* Profile Image */}
                    <div 
                      className="text-center py-5"
                      style={{ 
                        background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                        position: 'relative'
                      }}
                    >
                      {therapist.profile_image ? (
                        <img
                          src={therapist.profile_image}
                          alt={therapist.name}
                          style={{
                            width: '180px',
                            height: '180px',
                            maxWidth: '100%',
                            borderRadius: '50%',
                            objectFit: 'cover',
                            objectPosition: 'center',
                            border: '6px solid white',
                            boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                            margin: '0 auto',
                            display: 'block',
                            transition: 'all 0.3s ease',
                            cursor: 'pointer'
                          }}
                          onError={(e) => {
                            // If image fails to load, hide it and show placeholder
                            e.currentTarget.style.display = 'none';
                            const placeholder = e.currentTarget.nextElementSibling;
                            if (placeholder) {
                              (placeholder as HTMLElement).style.display = 'flex';
                            }
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'scale(1.05)';
                            e.currentTarget.style.boxShadow = '0 12px 35px rgba(0,0,0,0.2)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'scale(1)';
                            e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
                          }}
                        />
                      ) : null}
                      <div
                        style={{
                          width: '180px',
                          height: '180px',
                          maxWidth: '100%',
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                          display: therapist.profile_image ? 'none' : 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          margin: '0 auto',
                          border: '6px solid white',
                          boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                          transition: 'all 0.3s ease'
                        }}
                      >
                        <i className="fas fa-user" style={{ fontSize: '4.5rem', color: 'white' }}></i>
                      </div>
                      
                      {therapist.is_verified && (
                        <Badge 
                          bg="success" 
                          style={{
                            position: 'absolute',
                            top: '20px',
                            right: '20px',
                            fontSize: '0.8rem',
                            padding: '0.5rem 0.75rem',
                            borderRadius: '20px'
                          }}
                        >
                          <i className="fas fa-check-circle me-1"></i>
                          تأیید شده
                        </Badge>
                      )}
                    </div>

                    <Card.Body className="d-flex flex-column" style={{ padding: '2rem 1.75rem', minHeight: '280px' }}>
                      <Card.Title className="mb-3" style={{ fontSize: '1.25rem', fontWeight: 600, lineHeight: '1.4' }}>
                        {therapist.name}
                      </Card.Title>
                      
                      <div className="mb-3" style={{ minHeight: '60px', display: 'flex', alignItems: 'center' }}>
                        <Badge 
                          bg="primary" 
                          title={therapist.specialization}
                          style={{ 
                            fontSize: '0.75rem', 
                            padding: '0.4rem 0.6rem', 
                            borderRadius: '8px',
                            marginBottom: '0.5rem',
                            display: 'inline-block',
                            maxWidth: '100%',
                            wordWrap: 'break-word',
                            whiteSpace: 'normal',
                            lineHeight: '1.4',
                            textAlign: 'center',
                            width: '100%',
                            cursor: 'help'
                          }}
                        >
                          <i className="fas fa-graduation-cap me-1"></i>
                          <span style={{ 
                            display: 'inline-block',
                            maxWidth: '100%',
                            wordBreak: 'break-word',
                            overflow: 'hidden'
                          }}>
                            {therapist.specialization}
                          </span>
                        </Badge>
                      </div>

                      <div className="mb-4" style={{ flex: '1' }}>
                        <div className="d-flex align-items-center mb-2" style={{ fontSize: '0.9rem' }}>
                          <i className="fas fa-clock text-primary me-2" style={{ width: '18px' }}></i>
                          <span>{therapist.experience_years} سال تجربه</span>
                        </div>
                        <div className="d-flex align-items-center mb-2" style={{ fontSize: '0.9rem' }}>
                          <i className="fas fa-dollar-sign text-primary me-2" style={{ width: '18px' }}></i>
                          <span>{therapist.hourly_rate.toLocaleString()} تومان/ساعت</span>
                        </div>
                        {therapist.license_number && (
                          <div className="d-flex align-items-center" style={{ fontSize: '0.9rem' }}>
                            <i className="fas fa-certificate text-primary me-2" style={{ width: '18px' }}></i>
                            <span>شماره پروانه: {therapist.license_number}</span>
                          </div>
                        )}
                      </div>

                      <div className="mt-auto">
                        <div className="d-grid gap-2">
                          <Link to={`/appointment/booking?therapist=${therapist.id}`} style={{ textDecoration: 'none' }}>
                            <Button 
                              variant="primary" 
                              className="w-100"
                              style={{ 
                                borderRadius: '10px', 
                                padding: '0.75rem', 
                                fontWeight: 600,
                                transition: 'all 0.3s ease',
                              }}
                            >
                              <i className="fas fa-calendar-check me-2"></i>
                              رزرو نوبت
                            </Button>
                          </Link>
                          <Link to={`/therapists/${therapist.id}`} style={{ textDecoration: 'none' }}>
                            <Button 
                              variant="outline-primary" 
                              size="sm"
                              style={{ borderRadius: '8px' }}
                              className="w-100"
                            >
                              <i className="fas fa-info-circle me-1"></i>
                              مشاهده پروفایل
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <Card style={{ borderRadius: '18px', border: 'none', background: '#f8f9fa' }}>
              <Card.Body className="text-center" style={{ padding: '5rem 2rem' }}>
                <div 
                  style={{ 
                    width: '120px',
                    height: '120px',
                    margin: '0 auto 2rem',
                    background: 'linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <i className="fas fa-search" style={{ fontSize: '3.5rem', color: '#6c757d' }}></i>
                </div>
                <h5 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem', color: '#495057' }}>
                  درمانگری یافت نشد
                </h5>
                <p className="text-muted" style={{ fontSize: '1.05rem', maxWidth: '500px', margin: '0 auto' }}>
                  با فیلترهای انتخابی شما درمانگری یافت نشد. لطفاً فیلترها را تغییر دهید.
                </p>
              </Card.Body>
            </Card>
          )}
        </Container>
      </section>

      {/* Call to Action Section */}
      <section 
        className="py-5" 
        style={{ 
          background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
          color: 'white'
        }}
      >
        <Container>
          <Row className="align-items-center">
            <Col lg={8}>
              <h2 className="mb-3">آماده شروع درمان هستید؟</h2>
              <p className="lead mb-4">
                با تیم متخصص ما، مسیر بهبود و رشد شخصی خود را آغاز کنید.
              </p>
            </Col>
            <Col lg={4} className="text-lg-end">
              <div className="d-flex flex-column flex-lg-row gap-3">
                <Link to="/appointment/booking" className="btn btn-light btn-lg">
                  <i className="fas fa-calendar-check me-2"></i>
                  رزرو نوبت
                </Link>
                <Link to="/tests" className="btn btn-outline-light btn-lg">
                  <i className="fas fa-brain me-2"></i>
                  تست رایگان
                </Link>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
    </>
  );
};

export default Therapists;
