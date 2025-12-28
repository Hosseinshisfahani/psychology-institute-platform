import React from 'react';
import { Container, Row, Col, Card, Button, Badge, Alert } from 'react-bootstrap';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import axios from 'axios';
import CourseCard from '../../components/Courses/CourseCard';
import { Course } from '../../types/Course';

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
  phone_number?: string;
  email?: string;
}

const TherapistProfile: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Fetch therapist data
  const { data: therapist, isLoading, error } = useQuery<Therapist>({
    queryKey: ['therapist', id],
    queryFn: async () => {
      const response = await axios.get(`/api/appointments/therapists/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });

  // Fetch therapist's courses
  const { data: coursesData, isLoading: coursesLoading } = useQuery<{ results?: Course[]; count?: number } | Course[]>({
    queryKey: ['therapist-courses', id],
    queryFn: async () => {
      const response = await axios.get('/api/courses/', {
        params: { instructor: id }
      });
      return response.data;
    },
    enabled: !!id && !!therapist,
  });

  const courses: Course[] = Array.isArray(coursesData) 
    ? coursesData 
    : (coursesData?.results || []);

  if (isLoading) {
    return (
      <Container className="py-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
            <span className="visually-hidden">در حال بارگذاری...</span>
          </div>
          <p className="text-muted mt-3">در حال بارگذاری پروفایل درمانگر...</p>
        </div>
      </Container>
    );
  }

  if (error || !therapist) {
    return (
      <Container className="py-5">
        <Alert variant="danger" className="text-center">
          <h4>خطا در بارگذاری پروفایل</h4>
          <p>درمانگر مورد نظر یافت نشد یا خطایی رخ داده است.</p>
          <Button variant="outline-primary" onClick={() => navigate('/therapists')}>
            بازگشت به لیست درمانگران
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>{therapist.name} - پروفایل درمانگر</title>
        <meta name="description" content={`پروفایل ${therapist.name} - ${therapist.specialization}`} />
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
              <div className="d-flex align-items-center mb-4">
                <Button 
                  variant="outline-light" 
                  size="sm"
                  onClick={() => navigate('/therapists')}
                  className="me-3"
                >
                  <i className="fas fa-arrow-right me-2"></i>
                  بازگشت
                </Button>
                <h1 className="display-5 fw-bold mb-0">
                  <i className="fas fa-brain me-3"></i>
                  {therapist.name}
                </h1>
              </div>
              <p className="lead mb-4">
                {therapist.specialization}
              </p>
              <div className="d-flex flex-wrap gap-3">
                <Link to="/appointment/booking" className="btn btn-light btn-lg">
                  <i className="fas fa-calendar-check me-2"></i>
                  رزرو نوبت
                </Link>
              </div>
            </Col>
            <Col lg={4} className="text-center">
              {therapist.profile_image ? (
                <img
                  src={therapist.profile_image}
                  alt={therapist.name}
                  style={{
                    width: '250px',
                    height: '250px',
                    maxWidth: '100%',
                    borderRadius: '50%',
                    objectFit: 'cover',
                    objectPosition: 'center',
                    border: '8px solid rgba(255,255,255,0.3)',
                    boxShadow: '0 15px 40px rgba(0,0,0,0.2)',
                  }}
                  loading="lazy"
                />
              ) : (
                <div
                  style={{
                    width: '250px',
                    height: '250px',
                    maxWidth: '100%',
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto',
                    border: '8px solid rgba(255,255,255,0.3)',
                    boxShadow: '0 15px 40px rgba(0,0,0,0.2)',
                  }}
                >
                  <i className="fas fa-head-side-virus" style={{ fontSize: '6rem', color: 'white' }}></i>
                </div>
              )}
            </Col>
          </Row>
        </Container>
      </section>

      {/* Profile Details */}
      <section className="py-5">
        <Container>
          <Row className="g-4">
            {/* Main Info Card */}
            <Col lg={8}>
              <Card className="h-100" style={{ borderRadius: '18px', border: 'none', boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
                <Card.Body style={{ padding: '2.5rem' }}>
                  <div className="d-flex align-items-center mb-4">
                    <h2 className="mb-0 me-3">{therapist.name}</h2>
                    {therapist.is_verified && (
                      <Badge 
                        bg="success" 
                        style={{
                          fontSize: '0.9rem',
                          padding: '0.5rem 0.75rem',
                          borderRadius: '20px'
                        }}
                      >
                        <i className="fas fa-check-circle me-1"></i>
                        تأیید شده
                      </Badge>
                    )}
                  </div>

                  <div className="mb-4">
                    <Badge 
                      bg="primary" 
                      style={{ 
                        fontSize: '1rem', 
                        padding: '0.6rem 1rem', 
                        borderRadius: '10px',
                        marginBottom: '1rem',
                        display: 'inline-block'
                      }}
                    >
                      <i className="fas fa-graduation-cap me-2"></i>
                      {therapist.specialization}
                    </Badge>
                  </div>

                  {therapist.bio && (
                    <div className="mb-4">
                      <h5 className="mb-3">
                        <i className="fas fa-info-circle me-2 text-primary"></i>
                        درباره درمانگر
                      </h5>
                      <p className="text-muted" style={{ lineHeight: '1.8', fontSize: '1.05rem' }}>
                        {therapist.bio}
                      </p>
                    </div>
                  )}

                  <div className="row g-3">
                    <div className="col-md-6">
                      <div className="d-flex align-items-center mb-3">
                        <div 
                          className="d-flex align-items-center justify-content-center me-3"
                          style={{
                            width: '50px',
                            height: '50px',
                            background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                            borderRadius: '12px',
                            color: 'white'
                          }}
                        >
                          <i className="fas fa-clock"></i>
                        </div>
                        <div>
                          <h6 className="mb-1">سال‌های تجربه</h6>
                          <p className="text-muted mb-0">{therapist.experience_years} سال</p>
                        </div>
                      </div>
                    </div>

                    <div className="col-md-6">
                      <div className="d-flex align-items-center mb-3">
                        <div 
                          className="d-flex align-items-center justify-content-center me-3"
                          style={{
                            width: '50px',
                            height: '50px',
                            background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                            borderRadius: '12px',
                            color: 'white'
                          }}
                        >
                          <i className="fas fa-dollar-sign"></i>
                        </div>
                        <div>
                          <h6 className="mb-1">نرخ ساعتی</h6>
                          <p className="text-muted mb-0">{therapist.hourly_rate.toLocaleString()} تومان</p>
                        </div>
                      </div>
                    </div>

                    {therapist.license_number && (
                      <div className="col-md-6">
                        <div className="d-flex align-items-center mb-3">
                          <div 
                            className="d-flex align-items-center justify-content-center me-3"
                            style={{
                              width: '50px',
                              height: '50px',
                              background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                              borderRadius: '12px',
                              color: 'white'
                            }}
                          >
                            <i className="fas fa-certificate"></i>
                          </div>
                          <div>
                            <h6 className="mb-1">شماره پروانه</h6>
                            <p className="text-muted mb-0">{therapist.license_number}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="col-md-6">
                      <div className="d-flex align-items-center mb-3">
                        <div 
                          className="d-flex align-items-center justify-content-center me-3"
                          style={{
                            width: '50px',
                            height: '50px',
                            background: therapist.is_available 
                              ? 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'
                              : 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)',
                            borderRadius: '12px',
                            color: 'white'
                          }}
                        >
                          <i className={`fas ${therapist.is_available ? 'fa-check' : 'fa-times'}`}></i>
                        </div>
                        <div>
                          <h6 className="mb-1">وضعیت</h6>
                          <p className="text-muted mb-0">
                            {therapist.is_available ? 'در دسترس' : 'غیرفعال'}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>

            {/* Contact & Actions Card */}
            <Col lg={4}>
              <Card className="h-100" style={{ borderRadius: '18px', border: 'none', boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
                <Card.Body style={{ padding: '2.5rem' }}>
                  <h4 className="mb-4">
                    <i className="fas fa-phone me-2 text-primary"></i>
                    اطلاعات تماس
                  </h4>

                  {therapist.phone_number && (
                    <div className="mb-3">
                      <div className="d-flex align-items-center">
                        <i className="fas fa-phone text-primary me-3" style={{ width: '20px' }}></i>
                        <span>{therapist.phone_number}</span>
                      </div>
                    </div>
                  )}

                  {therapist.email && (
                    <div className="mb-4">
                      <div className="d-flex align-items-center">
                        <i className="fas fa-envelope text-primary me-3" style={{ width: '20px' }}></i>
                        <span>{therapist.email}</span>
                      </div>
                    </div>
                  )}

                  <div className="d-grid gap-3 mt-4">
                    <Link to="/appointment/booking" className="btn btn-primary btn-lg">
                      <i className="fas fa-calendar-check me-2"></i>
                      رزرو نوبت
                    </Link>
                  </div>

                  {!therapist.is_available && (
                    <Alert variant="warning" className="mt-3">
                      <i className="fas fa-exclamation-triangle me-2"></i>
                      این درمانگر در حال حاضر در دسترس نیست
                    </Alert>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Courses Section */}
      {(coursesLoading || courses.length > 0) && (
        <section className="py-5" style={{ background: '#f8f9fa' }}>
          <Container>
            <div className="mb-4">
              <h2 className="fw-bold mb-3">
                <i className="fas fa-graduation-cap me-2 text-primary"></i>
                دوره‌های آموزشی
              </h2>
              <p className="text-muted">
                دوره‌های آموزشی ارائه شده توسط {therapist.name}
              </p>
            </div>
            
            {coursesLoading ? (
              <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">در حال بارگذاری...</span>
                </div>
              </div>
            ) : courses.length > 0 ? (
              <Row className="g-4">
                {courses.map((course) => (
                  <Col key={course.id} xs={12} sm={6} lg={4} xl={3}>
                    <CourseCard course={course} />
                  </Col>
                ))}
              </Row>
            ) : (
              <div className="text-center py-5">
                <p className="text-muted">این درمانگر در حال حاضر دوره آموزشی‌ای ارائه نداده است.</p>
              </div>
            )}
          </Container>
        </section>
      )}
    </>
  );
};

export default TherapistProfile;
