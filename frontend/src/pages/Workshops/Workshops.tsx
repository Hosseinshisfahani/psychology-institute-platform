import React, { useState } from 'react';
import { Container, Row, Col, Card, Badge, Button, Form, Spinner } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface Workshop {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  category_name: string;
  instructor_name: string;
  status: string;
  difficulty: string;
  price: string;
  discount_price: string | null;
  current_price: string;
  discount_percentage: number;
  start_date: string;
  start_date_persian: string;
  total_hours: number;
  current_participants: number;
  max_participants: number;
  is_full: boolean;
  available_seats: number;
  thumbnail: string | null;
  rating: number;
  payment_type: string;
}

// Styles for animations and interactions
const filterCardStyle: React.CSSProperties = {
  transition: 'all 0.3s ease',
  cursor: 'pointer',
};

const filterCardHoverStyle: React.CSSProperties = {
  transform: 'translateY(-2px)',
  boxShadow: '0 8px 25px rgba(0,0,0,0.12)',
};

const selectStyle: React.CSSProperties = {
  transition: 'all 0.3s ease',
  borderRadius: '10px',
};

const workshopCardStyle: React.CSSProperties = {
  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
  borderRadius: '20px',
  overflow: 'hidden',
};

const workshopCardHoverStyle: React.CSSProperties = {
  transform: 'translateY(-8px)',
  boxShadow: '0 15px 40px rgba(0,0,0,0.15)',
};

const thumbnailContainerStyle: React.CSSProperties = {
  overflow: 'hidden',
  position: 'relative',
};

const thumbnailStyle: React.CSSProperties = {
  transition: 'transform 0.5s ease',
  height: '220px',
  objectFit: 'cover',
};

const badgeStyle: React.CSSProperties = {
  transition: 'all 0.2s ease',
  cursor: 'pointer',
};

const iconStyle: React.CSSProperties = {
  transition: 'all 0.3s ease',
};

const buttonStyle: React.CSSProperties = {
  transition: 'all 0.3s ease',
  borderRadius: '12px',
  fontWeight: 600,
  padding: '0.75rem 1.5rem',
};

const emptyStateIconStyle: React.CSSProperties = {
  animation: 'gentle-bounce 2s ease-in-out infinite',
};

const Workshops: React.FC = () => {
  const { t } = useI18n();
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);
  const [hoveredBadge, setHoveredBadge] = useState<string | null>(null);
  const [filterCardHovered, setFilterCardHovered] = useState(false);

  const { data: workshops, isLoading } = useQuery<Workshop[]>({
    queryKey: ['workshops', selectedCategory, selectedDifficulty],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (selectedDifficulty) params.append('difficulty', selectedDifficulty);
      
      const response = await axios.get(`/api/workshops/?${params.toString()}`);
      // Handle both array and paginated response formats
      return Array.isArray(response.data) ? response.data : response.data.results || [];
    },
  });

  const getDifficultyBadge = (difficulty: string) => {
    const badges = {
      beginner: 'success',
      intermediate: 'warning',
      advanced: 'danger',
    };
    return badges[difficulty as keyof typeof badges] || 'secondary';
  };

  const getPaymentTypeBadge = (paymentType: string) => {
    switch (paymentType) {
      case 'full_payment':
        return 'پرداخت کامل';
      case 'installment':
        return 'پرداخت قسطی';
      case 'both':
        return 'کامل یا قسطی';
      default:
        return paymentType;
    }
  };

  return (
    <>
      <Helmet>
        <title>کارگاه‌های آموزشی - {t('home.title')}</title>
        <meta name="description" content="کارگاه‌های آموزشی روان‌شناسی" />
      </Helmet>

      <style>
        {`
          @keyframes gentle-bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
          }
          
          .workshop-card-thumbnail:hover {
            transform: scale(1.1);
          }
          
          .info-icon-hover:hover {
            transform: scale(1.15);
            color: #1e3d6f !important;
          }
          
          .badge-hover:hover {
            transform: scale(1.05);
          }
          
          .btn-workshop:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(44, 90, 160, 0.3);
          }
          
          .btn-workshop:active {
            transform: translateY(0);
          }
          
          .workshop-card-animate {
            animation: fadeInUp 0.6s ease-out forwards;
            opacity: 0;
          }
          
          @keyframes fadeInUp {
            from {
              opacity: 0;
              transform: translateY(30px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
        `}
      </style>

      <Container className="py-6" style={{ paddingTop: '4rem', paddingBottom: '4rem' }}>
        {/* Header */}
        <div className="mb-6 text-center" style={{ marginBottom: '4rem' }}>
          <h1 className="mb-4" style={{ fontSize: '2.75rem', fontWeight: 700 }}>
            <i className="fas fa-chalkboard-teacher text-primary ms-3" style={{ fontSize: '2.5rem' }}></i>
            کارگاه‌های آموزشی
          </h1>
          <p className="text-muted lead" style={{ maxWidth: '600px', margin: '0 auto', fontSize: '1.15rem', lineHeight: '1.8' }}>
            در کارگاه‌های آموزشی ما شرکت کرده و مهارت‌های جدید کسب کنید
          </p>
        </div>

        {/* Filters */}
        <Card 
          className="mb-5"
          style={{
            ...filterCardStyle,
            ...(filterCardHovered ? filterCardHoverStyle : {}),
            borderRadius: '18px',
            border: 'none',
          }}
          onMouseEnter={() => setFilterCardHovered(true)}
          onMouseLeave={() => setFilterCardHovered(false)}
        >
          <Card.Body style={{ padding: '2rem' }}>
            <Row>
              <Col md={6} className="mb-3 mb-md-0">
                <Form.Group>
                  <Form.Label style={{ fontWeight: 600, marginBottom: '0.75rem', fontSize: '1.05rem' }}>
                    <i className="fas fa-folder text-primary ms-2"></i>
                    دسته‌بندی
                  </Form.Label>
                  <Form.Select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    style={selectStyle}
                  >
                    <option value="">همه دسته‌ها</option>
                    <option value="therapy">درمان</option>
                    <option value="counseling">مشاوره</option>
                    <option value="development">توسعه فردی</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group>
                  <Form.Label style={{ fontWeight: 600, marginBottom: '0.75rem', fontSize: '1.05rem' }}>
                    <i className="fas fa-chart-line text-primary ms-2"></i>
                    سطح دشواری
                  </Form.Label>
                  <Form.Select
                    value={selectedDifficulty}
                    onChange={(e) => setSelectedDifficulty(e.target.value)}
                    style={selectStyle}
                  >
                    <option value="">همه سطوح</option>
                    <option value="beginner">مقدماتی</option>
                    <option value="intermediate">متوسط</option>
                    <option value="advanced">پیشرفته</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
          </Card.Body>
        </Card>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-5" style={{ minHeight: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
            <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
            <p className="mt-4 text-muted" style={{ fontSize: '1.1rem' }}>در حال بارگذاری کارگاه‌ها...</p>
          </div>
        )}

        {/* Workshops Grid */}
        {!isLoading && workshops && (
          <>
            {workshops.length === 0 ? (
              <Card style={{ borderRadius: '18px', border: 'none' }}>
                <Card.Body className="text-center" style={{ padding: '4rem 2rem' }}>
                  <i 
                    className="fas fa-inbox text-muted mb-4" 
                    style={{ ...emptyStateIconStyle, fontSize: '4rem', display: 'block' }}
                  ></i>
                  <h5 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem' }}>کارگاهی یافت نشد</h5>
                  <p className="text-muted" style={{ fontSize: '1.05rem' }}>در حال حاضر کارگاهی با این فیلترها وجود ندارد</p>
                </Card.Body>
              </Card>
            ) : (
              <Row>
                {workshops.map((workshop, index) => (
                  <Col key={workshop.id} md={6} lg={4} className="mb-5">
                    <Card 
                      className="h-100 workshop-card-animate"
                      style={{
                        ...workshopCardStyle,
                        ...(hoveredCard === workshop.id ? workshopCardHoverStyle : {}),
                        animationDelay: `${index * 0.1}s`,
                      }}
                      onMouseEnter={() => setHoveredCard(workshop.id)}
                      onMouseLeave={() => setHoveredCard(null)}
                    >
                      {workshop.thumbnail && (
                        <div style={thumbnailContainerStyle}>
                          <Card.Img
                            variant="top"
                            src={workshop.thumbnail}
                            className="workshop-card-thumbnail"
                            style={thumbnailStyle}
                          />
                          <div style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'linear-gradient(to bottom, transparent 60%, rgba(0,0,0,0.1) 100%)',
                            pointerEvents: 'none',
                          }}></div>
                        </div>
                      )}
                      <Card.Body className="d-flex flex-column" style={{ padding: '1.75rem' }}>
                        <div className="mb-3" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                          <Badge 
                            bg="info" 
                            className="badge-hover"
                            style={{
                              ...badgeStyle,
                              fontSize: '0.85rem',
                              padding: '0.5rem 0.85rem',
                              borderRadius: '8px',
                              ...(hoveredBadge === `cat-${workshop.id}` ? { transform: 'scale(1.05)' } : {}),
                            }}
                            onMouseEnter={() => setHoveredBadge(`cat-${workshop.id}`)}
                            onMouseLeave={() => setHoveredBadge(null)}
                          >
                            {workshop.category_name}
                          </Badge>
                          <Badge 
                            bg={getDifficultyBadge(workshop.difficulty)}
                            className="badge-hover"
                            style={{
                              ...badgeStyle,
                              fontSize: '0.85rem',
                              padding: '0.5rem 0.85rem',
                              borderRadius: '8px',
                              ...(hoveredBadge === `diff-${workshop.id}` ? { transform: 'scale(1.05)' } : {}),
                            }}
                            onMouseEnter={() => setHoveredBadge(`diff-${workshop.id}`)}
                            onMouseLeave={() => setHoveredBadge(null)}
                          >
                            {workshop.difficulty === 'beginner' && 'مقدماتی'}
                            {workshop.difficulty === 'intermediate' && 'متوسط'}
                            {workshop.difficulty === 'advanced' && 'پیشرفته'}
                          </Badge>
                        </div>

                        <Card.Title className="mb-3" style={{ fontSize: '1.35rem', fontWeight: 600, lineHeight: '1.4' }}>
                          {workshop.title}
                        </Card.Title>
                        <Card.Text className="text-muted mb-4" style={{ fontSize: '0.95rem', lineHeight: '1.7' }}>
                          {workshop.short_description}
                        </Card.Text>

                        <div className="mb-4" style={{ flex: '1' }}>
                          <div className="d-flex align-items-center mb-3" style={{ fontSize: '0.95rem' }}>
                            <i className="fas fa-user text-primary ms-2 info-icon-hover" style={{ ...iconStyle, width: '20px' }}></i>
                            <span>{workshop.instructor_name}</span>
                          </div>
                          <div className="d-flex align-items-center mb-3" style={{ fontSize: '0.95rem' }}>
                            <i className="fas fa-calendar text-primary ms-2 info-icon-hover" style={{ ...iconStyle, width: '20px' }}></i>
                            <span>شروع: {workshop.start_date_persian}</span>
                          </div>
                          <div className="d-flex align-items-center mb-3" style={{ fontSize: '0.95rem' }}>
                            <i className="fas fa-clock text-primary ms-2 info-icon-hover" style={{ ...iconStyle, width: '20px' }}></i>
                            <span>{workshop.total_hours} ساعت</span>
                          </div>
                          <div className="d-flex align-items-center mb-3" style={{ fontSize: '0.95rem' }}>
                            <i className="fas fa-users text-primary ms-2 info-icon-hover" style={{ ...iconStyle, width: '20px' }}></i>
                            <span>
                              {workshop.is_full ? (
                                <Badge bg="danger" style={{ fontSize: '0.8rem', padding: '0.4rem 0.7rem' }}>
                                  ظرفیت تکمیل
                                </Badge>
                              ) : (
                                `${workshop.available_seats} صندلی خالی`
                              )}
                            </span>
                          </div>
                          <div className="d-flex align-items-center" style={{ fontSize: '0.95rem' }}>
                            <i className="fas fa-credit-card text-primary ms-2 info-icon-hover" style={{ ...iconStyle, width: '20px' }}></i>
                            <span>{getPaymentTypeBadge(workshop.payment_type)}</span>
                          </div>
                        </div>

                        <div className="mt-auto">
                          <div className="mb-4" style={{ 
                            padding: '1.25rem', 
                            background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 50%)', 
                            borderRadius: '12px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.5rem'
                          }}>
                            {workshop.discount_price ? (
                              <>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                                  <span className="text-decoration-line-through text-muted" style={{ fontSize: '0.95rem' }}>
                                    {parseInt(workshop.price).toLocaleString()} تومان
                                  </span>
                                  <Badge 
                                    bg="danger" 
                                    style={{ 
                                      fontSize: '0.85rem', 
                                      padding: '0.35rem 0.7rem',
                                      fontWeight: 700
                                    }}
                                  >
                                    {workshop.discount_percentage}% تخفیف
                                  </Badge>
                                </div>
                                <div className="text-primary" style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                                  {parseInt(workshop.current_price).toLocaleString()} تومان
                                </div>
                              </>
                            ) : (
                              <div className="text-primary" style={{ fontSize: '1.5rem', fontWeight: 700 }}>
                                {parseInt(workshop.price).toLocaleString()} تومان
                              </div>
                            )}
                          </div>

                          <div className="d-grid">
                            <Link to={`/workshops/${workshop.slug}`} style={{ textDecoration: 'none' }}>
                              <Button
                                variant="primary"
                                disabled={workshop.is_full}
                                className="w-100 btn-workshop"
                                style={{
                                  ...buttonStyle,
                                  opacity: workshop.is_full ? 0.6 : 1,
                                  cursor: workshop.is_full ? 'not-allowed' : 'pointer',
                                }}
                              >
                                {workshop.is_full ? (
                                  <>
                                    <i className="fas fa-times-circle ms-2"></i>
                                    ظرفیت تکمیل
                                  </>
                                ) : (
                                  <>
                                    <i className="fas fa-arrow-left ms-2"></i>
                                    مشاهده جزئیات
                                  </>
                                )}
                              </Button>
                            </Link>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
            )}
          </>
        )}
      </Container>
    </>
  );
};

export default Workshops;

