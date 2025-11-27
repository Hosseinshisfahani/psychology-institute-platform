import React from 'react';
import { Container, Row, Col, Card, Badge, Button, ListGroup, Tab, Tabs, Alert, Spinner, ProgressBar } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { QRCodeSVG } from 'qrcode.react';

interface Course {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  instructor_name: string;
  difficulty: string;
  price: string;
  discount_price: string | null;
  current_price: string;
  duration_hours: number;
  thumbnail: string | null;
}

interface PackageDetail {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  category: {
    name: string;
  };
  price: string;
  discount_price: string | null;
  current_price: string;
  discount_percentage: number;
  is_featured: boolean;
  duration_months: number;
  language: string;
  prerequisites: string | null;
  learning_objectives: string;
  thumbnail: string | null;
  courses: Course[];
  total_courses: number;
  total_hours: number;
  original_total_price: string;
  savings_amount: string;
  savings_percentage: number;
  purchase_count: number;
  rating: number;
  review_count: number;
  purchase_status: {
    is_purchased: boolean;
    purchased_at?: string;
    is_expired?: boolean;
  };
}

const PackageDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [pendingAction, setPendingAction] = React.useState<'add' | 'redirect' | null>(null);
  const [copied, setCopied] = React.useState(false);

  const { data: packageData, isLoading } = useQuery<PackageDetail>({
    queryKey: ['package', slug],
    queryFn: async () => {
      const response = await axios.get(`/api/packages/${slug}/`);
      return response.data;
    },
  });

  const addToCartMutation = useMutation({
    mutationFn: async (variables: { redirect: boolean }) => {
      const response = await axios.post(`/api/packages/${slug}/add-to-cart/`);
      return { data: response.data, redirect: variables.redirect };
    },
    onSuccess: ({ data, redirect }) => {
      const message = data?.message || (redirect ? 'پکیج به سبد خرید شما منتقل شد.' : 'پکیج به سبد خرید اضافه شد.');
      alert(message);
      if (redirect) {
        navigate(data?.cart_url || '/payment/cart');
      }
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.error || 'خطا در افزودن به سبد خرید';
      alert(errorMessage);
      const cartUrl = error.response?.data?.cart_url;
      if (cartUrl) {
        navigate(cartUrl);
      }
    },
    onSettled: () => {
      setPendingAction(null);
    },
  });

  const ensureAuthenticated = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return false;
    }
    return true;
  };

  const handleAddToCart = () => {
    if (!ensureAuthenticated()) {
      return;
    }
    setPendingAction('add');
    addToCartMutation.mutate({ redirect: false });
  };

  const handleBuyNow = () => {
    if (!ensureAuthenticated()) {
      return;
    }
    setPendingAction('redirect');
    addToCartMutation.mutate({ redirect: true });
  };

  const isMutationPending = addToCartMutation.isPending;
  const isAddingToCart = isMutationPending && pendingAction === 'add';
  const isBuyingNow = isMutationPending && pendingAction === 'redirect';

  // Generate full URL for QR code
  const packageUrl = React.useMemo(() => {
    if (typeof window !== 'undefined' && slug) {
      return `${window.location.origin}/packages/${slug}`;
    }
    return '';
  }, [slug]);

  // Share functions
  const handleCopyLink = async () => {
    if (packageUrl) {
      try {
        await navigator.clipboard.writeText(packageUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    }
  };

  const handleShareWhatsApp = () => {
    if (packageUrl && packageData) {
      const text = `پکیج آموزشی: ${packageData.title}\n${packageUrl}`;
      window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
    }
  };

  const handleShareTelegram = () => {
    if (packageUrl && packageData) {
      const text = `پکیج آموزشی: ${packageData.title}\n${packageUrl}`;
      window.open(`https://t.me/share/url?url=${encodeURIComponent(packageUrl)}&text=${encodeURIComponent(packageData.title)}`, '_blank');
    }
  };

  const handleShareEmail = () => {
    if (packageUrl && packageData) {
      const subject = encodeURIComponent(`پکیج آموزشی: ${packageData.title}`);
      const body = encodeURIComponent(`سلام،\n\nاین پکیج آموزشی را به شما پیشنهاد می‌کنم:\n\n${packageData.title}\n${packageUrl}`);
      window.location.href = `mailto:?subject=${subject}&body=${body}`;
    }
  };


  if (isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3 text-muted">در حال بارگذاری...</p>
      </Container>
    );
  }

  if (!packageData) {
    return (
      <Container className="py-5">
        <Alert variant="danger">پکیج مورد نظر یافت نشد</Alert>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>{packageData.title} - پکیج‌های آموزشی</title>
        <meta name="description" content={packageData.short_description} />
      </Helmet>

      <Container className="py-5">
        <Row>
          {/* Main Content */}
          <Col lg={8}>
            {/* Hero Section */}
            {packageData.thumbnail && (
              <Card className="mb-4">
                <Card.Img
                  variant="top"
                  src={packageData.thumbnail}
                  style={{ height: '400px', objectFit: 'cover' }}
                />
              </Card>
            )}

            <Card className="mb-4">
              <Card.Body>
                <div className="mb-3">
                  <Badge bg="info" className="ms-2">{packageData.category.name}</Badge>
                  {packageData.is_featured && (
                    <Badge bg="warning" text="dark">
                      <i className="fas fa-star ms-3" style={{ marginLeft: '8px' }}></i>
                      ویژه
                    </Badge>
                  )}
                </div>

                <h1 className="mb-3">{packageData.title}</h1>
                <p className="text-muted lead">{packageData.short_description}</p>

                <div className="d-flex align-items-center gap-4 mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-book text-primary ms-3" style={{ marginLeft: '8px' }}></i>
                    <span>{packageData.total_courses} دوره</span>
                  </div>
                  <div className="d-flex align-items-center">
                    <i className="fas fa-clock text-primary ms-3" style={{ marginLeft: '8px' }}></i>
                    <span>{packageData.total_hours} ساعت</span>
                  </div>
                  <div className="d-flex align-items-center">
                    <i className="fas fa-star text-warning ms-3" style={{ marginLeft: '8px' }}></i>
                    <span>{packageData.rating.toFixed(1)} ({packageData.review_count} نظر)</span>
                  </div>
                  <div className="d-flex align-items-center">
                    <i className="fas fa-users text-primary ms-3" style={{ marginLeft: '8px' }}></i>
                    <span>{packageData.purchase_count} خریدار</span>
                  </div>
                </div>

                {packageData.purchase_status.is_purchased && (
                  <Alert variant="success">
                    <i className="fas fa-check-circle ms-3" style={{ marginLeft: '8px' }}></i>
                    شما این دوره را خریداری کرده‌اید
                    {packageData.purchase_status.is_expired && (
                      <span className="text-danger"> (منقضی شده)</span>
                    )}
                  </Alert>
                )}

                {packageData.savings_percentage > 0 && (
                  <Alert variant="success">
                    <h5>
                      <i className="fas fa-percentage ms-3" style={{ marginLeft: '8px' }}></i>
                      {packageData.savings_percentage}% صرفه‌جویی
                    </h5>
                    <p className="mb-0">
                      با خرید این دوره، {parseInt(packageData.savings_amount).toLocaleString()} تومان صرفه‌جویی می‌کنید
                    </p>
                  </Alert>
                )}
              </Card.Body>
            </Card>

            {/* Tabs */}
            <Card>
              <Card.Body>
                <Tabs defaultActiveKey="description" className="mb-3">
                  <Tab eventKey="description" title="توضیحات">
                    <div dangerouslySetInnerHTML={{ __html: packageData.description }} />
                    
                    {packageData.prerequisites && (
                      <>
                        <h5 className="mt-4 mb-3">پیش‌نیازها</h5>
                        <div dangerouslySetInnerHTML={{ __html: packageData.prerequisites }} />
                      </>
                    )}

                    <h5 className="mt-4 mb-3">اهداف یادگیری</h5>
                    <div dangerouslySetInnerHTML={{ __html: packageData.learning_objectives }} />
                  </Tab>

                  <Tab eventKey="courses" title={`دوره‌ها (${packageData.total_courses})`}>
                    <Row>
                      {packageData.courses.map((course) => (
                        <Col key={course.id} md={6} className="mb-3">
                          <Link 
                            to={`/courses/course/${course.slug}`}
                            style={{ textDecoration: 'none', color: 'inherit' }}
                          >
                            <Card className="h-100 hover-shadow" style={{ transition: 'all 0.3s ease', cursor: 'pointer' }}>
                              {course.thumbnail && (
                                <Card.Img
                                  variant="top"
                                  src={course.thumbnail}
                                  style={{ height: '150px', objectFit: 'cover' }}
                                />
                              )}
                              <Card.Body>
                                <Badge bg={course.difficulty === 'beginner' ? 'success' : course.difficulty === 'intermediate' ? 'warning' : 'danger'} className="mb-2">
                                  {course.difficulty === 'beginner' && 'مقدماتی'}
                                  {course.difficulty === 'intermediate' && 'متوسط'}
                                  {course.difficulty === 'advanced' && 'پیشرفته'}
                                </Badge>
                                <Card.Title className="h6">{course.title}</Card.Title>
                                <Card.Text className="text-muted small mb-2">
                                  {course.short_description}
                                </Card.Text>
                                <div className="small text-muted">
                                  <div><i className="fas fa-user ms-3" style={{ marginLeft: '8px' }}></i>{course.instructor_name}</div>
                                  <div><i className="fas fa-clock ms-3" style={{ marginLeft: '8px' }}></i>{course.duration_hours} ساعت</div>
                                </div>
                              </Card.Body>
                            </Card>
                          </Link>
                        </Col>
                      ))}
                    </Row>
                  </Tab>
                </Tabs>
              </Card.Body>
            </Card>
          </Col>

          {/* Sidebar */}
          <Col lg={4}>
            <Card className="mb-4">
              <Card.Body>
                <div className="mb-4">
                  {packageData.discount_price ? (
                    <>
                      <div className="text-decoration-line-through text-muted mb-2">
                        {parseInt(packageData.price).toLocaleString()} تومان
                      </div>
                      <div className="h3 text-primary mb-2">
                        {parseInt(packageData.current_price).toLocaleString()} تومان
                        <Badge bg="danger" className="me-2">{packageData.discount_percentage}%</Badge>
                      </div>
                    </>
                  ) : (
                    <div className="h3 text-primary mb-2">
                      {parseInt(packageData.price).toLocaleString()} تومان
                    </div>
                  )}
                  {packageData.savings_percentage > 0 && (
                    <div className="text-success small">
                      <i className="fas fa-tag ms-3" style={{ marginLeft: '8px' }}></i>
                      صرفه‌جویی {parseInt(packageData.savings_amount).toLocaleString()} تومان
                    </div>
                  )}
                </div>

                <ListGroup variant="flush" className="mb-4">
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span><i className="fas fa-book ms-3" style={{ marginLeft: '8px' }}></i>تعداد دوره‌ها</span>
                    <strong>{packageData.total_courses} دوره</strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span><i className="fas fa-clock ms-3" style={{ marginLeft: '8px' }}></i>مجموع ساعات</span>
                    <strong>{packageData.total_hours} ساعت</strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span><i className="fas fa-calendar ms-3" style={{ marginLeft: '8px' }}></i>مدت دسترسی</span>
                    <strong>{packageData.duration_months} ماه</strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span><i className="fas fa-dollar-sign ms-3" style={{ marginLeft: '8px' }}></i>قیمت کل دوره‌ها</span>
                    <strong>{parseInt(packageData.original_total_price).toLocaleString()} تومان</strong>
                  </ListGroup.Item>
                </ListGroup>

                <div className="d-grid gap-2">
                  {!packageData.purchase_status.is_purchased ? (
                    <>
                      <Button
                        variant="primary"
                        size="lg"
                        onClick={handleBuyNow}
                        disabled={isBuyingNow}
                      >
                        {isBuyingNow ? 'در حال انتقال...' : 'خرید پکیج'}
                      </Button>
                      <Button
                        variant="outline-primary"
                        size="lg"
                        onClick={handleAddToCart}
                        disabled={isAddingToCart}
                      >
                        {isAddingToCart ? 'در حال افزودن...' : 'افزودن به سبد خرید'}
                      </Button>
                    </>
                  ) : (
                    <Button
                      variant="success"
                      size="lg"
                      onClick={() => navigate('/dashboard')}
                    >
                      مشاهده دوره‌ها
                    </Button>
                  )}
                </div>
              </Card.Body>
            </Card>

            {/* QR Code Card */}
            <Card className="mb-4">
              <Card.Body className="text-center">
                <h5 className="mb-3">
                  <i className="fas fa-qrcode ms-3" style={{ marginLeft: '8px' }}></i>
                  کد QR پکیج
                </h5>
                <p className="text-muted small mb-3">
                  این کد را اسکن کنید تا به صفحه پکیج دسترسی پیدا کنید
                </p>
                {packageUrl && (
                  <div className="d-flex justify-content-center mb-3">
                    <div style={{ 
                      padding: '15px', 
                      backgroundColor: 'white', 
                      borderRadius: '8px',
                      border: '1px solid #e9ecef',
                      display: 'inline-block'
                    }}>
                      <QRCodeSVG 
                        value={packageUrl}
                        size={200}
                        level="H"
                        includeMargin={true}
                      />
                    </div>
                  </div>
                )}
              </Card.Body>
            </Card>

            {/* Share Package Card */}
            <Card className="mb-4" style={{ border: 'none', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
              <Card.Body style={{ padding: '1.5rem' }}>
                <h5 className="mb-4 text-center" style={{ fontWeight: 600, color: '#2c3e50' }}>
                  <i className="fas fa-share-alt ms-3" style={{ color: '#5a67d8' }}></i>
                  اشتراک‌گذاری پکیج
                </h5>
                
                {/* Copy Link Button */}
                <Button
                  variant={copied ? "success" : "outline-primary"}
                  onClick={handleCopyLink}
                  className="w-100 mb-3 d-flex align-items-center justify-content-center"
                  style={{ 
                    height: '48px',
                    fontSize: '1rem',
                    fontWeight: 500,
                    borderRadius: '8px',
                    transition: 'all 0.3s ease',
                    borderWidth: '2px'
                  }}
                  onMouseEnter={(e) => {
                    if (!copied) {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <i className={`fas ${copied ? 'fa-check-circle' : 'fa-copy'} ms-3`} style={{ fontSize: '1.1rem', marginLeft: '8px' }}></i>
                  {copied ? 'کپی شد!' : 'کپی لینک'}
                </Button>
                
                {/* Share Buttons Grid */}
                <div className="row g-3">
                  <div className="col-6">
                    <Button
                      onClick={handleShareWhatsApp}
                      className="w-100 d-flex align-items-center justify-content-center"
                      style={{ 
                        backgroundColor: '#25D366', 
                        color: 'white', 
                        border: 'none',
                        height: '48px',
                        fontSize: '1rem',
                        fontWeight: 500,
                        borderRadius: '8px',
                        transition: 'all 0.3s ease',
                        boxShadow: '0 2px 6px rgba(37, 211, 102, 0.3)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(37, 211, 102, 0.4)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 2px 6px rgba(37, 211, 102, 0.3)';
                      }}
                    >
                      <i className="fab fa-whatsapp ms-3" style={{ fontSize: '1.2rem', marginLeft: '8px' }}></i>
                      واتساپ
                    </Button>
                  </div>
                  <div className="col-6">
                    <Button
                      onClick={handleShareTelegram}
                      className="w-100 d-flex align-items-center justify-content-center"
                      style={{ 
                        backgroundColor: '#0088cc', 
                        color: 'white', 
                        border: 'none',
                        height: '48px',
                        fontSize: '1rem',
                        fontWeight: 500,
                        borderRadius: '8px',
                        transition: 'all 0.3s ease',
                        boxShadow: '0 2px 6px rgba(0, 136, 204, 0.3)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 136, 204, 0.4)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 2px 6px rgba(0, 136, 204, 0.3)';
                      }}
                    >
                      <i className="fab fa-telegram ms-3" style={{ fontSize: '1.2rem', marginLeft: '8px' }}></i>
                      تلگرام
                    </Button>
                  </div>
                </div>

                {/* Email Button */}
                <Button
                  variant="outline-secondary"
                  onClick={handleShareEmail}
                  className="w-100 mt-3 d-flex align-items-center justify-content-center"
                  style={{ 
                    height: '48px',
                    fontSize: '1rem',
                    fontWeight: 500,
                    borderRadius: '8px',
                    transition: 'all 0.3s ease',
                    borderWidth: '2px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                    e.currentTarget.style.borderColor = '#6c757d';
                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <i className="fas fa-envelope ms-3" style={{ fontSize: '1.1rem', marginLeft: '8px' }}></i>
                  ایمیل
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Courses Section - Before Footer */}
        {packageData.courses && packageData.courses.length > 0 && (
          <Row className="mt-5">
            <Col>
              <Card>
                <Card.Body>
                  <h3 className="mb-4">
                    <i className="fas fa-graduation-cap text-primary ms-3" style={{ marginLeft: '8px' }}></i>
                    دوره‌های این پکیج ({packageData.courses.length})
                  </h3>
                  <Row>
                    {packageData.courses.map((course) => (
                      <Col key={course.id} md={6} lg={4} className="mb-4">
                        <Link 
                          to={`/courses/course/${course.slug}`}
                          style={{ textDecoration: 'none', color: 'inherit' }}
                        >
                          <Card className="h-100 hover-shadow" style={{ 
                            transition: 'all 0.3s ease', 
                            cursor: 'pointer',
                            border: '1px solid #e9ecef'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.transform = 'translateY(-5px)';
                            e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.15)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                          }}
                          >
                            {course.thumbnail && (
                              <Card.Img
                                variant="top"
                                src={course.thumbnail}
                                style={{ height: '180px', objectFit: 'cover' }}
                              />
                            )}
                            <Card.Body>
                              <div className="d-flex justify-content-between align-items-start mb-2">
                                <Badge bg={course.difficulty === 'beginner' ? 'success' : course.difficulty === 'intermediate' ? 'warning' : 'danger'}>
                                  {course.difficulty === 'beginner' && 'مقدماتی'}
                                  {course.difficulty === 'intermediate' && 'متوسط'}
                                  {course.difficulty === 'advanced' && 'پیشرفته'}
                                </Badge>
                                {course.current_price && (
                                  <span className="text-primary fw-bold">
                                    {parseInt(course.current_price).toLocaleString()} تومان
                                  </span>
                                )}
                              </div>
                              <Card.Title className="h5 mb-2" style={{ fontSize: '1.1rem', fontWeight: 600 }}>
                                {course.title}
                              </Card.Title>
                              <Card.Text className="text-muted small mb-3" style={{ minHeight: '40px' }}>
                                {course.short_description}
                              </Card.Text>
                              <div className="d-flex align-items-center justify-content-between">
                                <div className="small text-muted">
                                  <div className="mb-1">
                                    <i className="fas fa-user ms-3" style={{ marginLeft: '8px' }}></i>
                                    {course.instructor_name}
                                  </div>
                                  <div>
                                    <i className="fas fa-clock ms-3" style={{ marginLeft: '8px' }}></i>
                                    {course.duration_hours} ساعت
                                  </div>
                                </div>
                                <span className="btn btn-outline-primary btn-sm">
                                  مشاهده دوره
                                  <i className="fas fa-arrow-left ms-3" style={{ marginLeft: '8px' }}></i>
                                </span>
                              </div>
                            </Card.Body>
                          </Card>
                        </Link>
                      </Col>
                    ))}
                  </Row>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}
      </Container>
    </>
  );
};

export default PackageDetail;

