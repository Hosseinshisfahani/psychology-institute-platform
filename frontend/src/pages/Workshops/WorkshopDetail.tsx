import React, { useState } from 'react';
import { Container, Row, Col, Card, Badge, Button, ListGroup, Tab, Tabs, Alert, Spinner, Modal, Form, Table } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { workshopApi } from '../../services/workshopApi';

interface WorkshopSession {
  id: number;
  session_number: number;
  title: string;
  description: string;
  scheduled_datetime: string;
  scheduled_datetime_persian: string;
  duration_minutes: number;
  has_recording: boolean;
  can_join: boolean;
  is_completed: boolean;
}

interface WorkshopCertificate {
  id: number;
  certificate_number: string;
  status: string;
  user_name: string;
  workshop_title: string;
  workshop_slug: string;
  instructor_name: string;
  certificate_file: string | null;
  certificate_file_url: string | null;
  issued_at: string | null;
  issued_at_persian: string | null;
  verification_code: string;
  is_valid: boolean;
  created_at: string;
}

interface Workshop {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  category: {
    name: string;
  };
  instructor_name: string;
  status: string;
  difficulty: string;
  price: string;
  discount_price: string | null;
  current_price: string;
  discount_percentage: number;
  payment_type: string;
  installment_months: number;
  installment_amount: string;
  start_date_persian: string;
  end_date_persian: string;
  registration_deadline_persian: string;
  total_hours: number;
  prerequisites: string | null;
  learning_objectives: string;
  current_participants: number;
  max_participants: number;
  is_full: boolean;
  available_seats: number;
  thumbnail: string | null;
  rating: number;
  review_count: number;
  sessions: WorkshopSession[];
  registration_status: {
    is_registered: boolean;
    status?: string;
    payment_type?: string;
    progress_percentage?: number;
    has_overdue?: boolean;
    next_payment?: {
      id: number;
      installment_number: number;
      amount: string | number;
      due_date?: string;
      due_date_persian?: string;
      status?: string;
    } | null;
  };
}

const WorkshopDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [paymentType, setPaymentType] = useState('full_payment');
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewTitle, setReviewTitle] = useState('');
  const [reviewContent, setReviewContent] = useState('');
  const [instructorRating, setInstructorRating] = useState(5);
  const [contentRating, setContentRating] = useState(5);
  const [interactionRating, setInteractionRating] = useState(5);

  const { data: workshop, isLoading } = useQuery<Workshop>({
    queryKey: ['workshop', slug],
    queryFn: async () => {
      const response = await axios.get(`/api/workshops/${slug}/`);
      return response.data;
    },
  });

  // Installments data (only for registered users with installment payment)
  const { data: installmentsData } = useQuery<{ plan: { total_amount: number; number_of_installments: number; installment_amount: number; total_paid: number; remaining_amount: number; is_fully_paid: boolean }, payments: Array<{ id: number; installment_number: number; amount: number; due_date: string; due_date_persian: string; status: string; paid_at?: string }>}>({
    queryKey: ['workshop-installments', slug],
    queryFn: async () => {
      const res = await axios.get(`/api/workshops/${slug}/installments/`);
      return res.data;
    },
    enabled: !!workshop && workshop.registration_status?.is_registered && workshop.registration_status?.payment_type === 'installment'
  });

  // Certificate data (only for registered users)
  const { data: certificate, isLoading: certificateLoading, refetch: refetchCertificate } = useQuery<WorkshopCertificate | null>({
    queryKey: ['workshop-certificate', slug],
    queryFn: async () => {
      try {
        const res = await axios.get(`/api/workshops/${slug}/certificate/`);
        return res.data;
      } catch (error: any) {
        // 404 is expected when certificate doesn't exist yet - don't throw
        if (error.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
    enabled: !!workshop && workshop.registration_status?.is_registered && workshop.registration_status?.status !== 'pending_payment',
    retry: false,
  });

  const registerMutation = useMutation({
    mutationFn: async (data: { payment_type: string }) => {
      const response = await axios.post(`/api/workshops/${slug}/register/`, data);
      return response.data;
    },
    onSuccess: (data) => {
      // Close modal
      setShowRegisterModal(false);
      
      // Redirect to cart for review before payment
      if (data.success && data.redirect_url) {
        // Navigate to cart page
        navigate(data.redirect_url);
      } else {
        // Fallback: navigate to cart
        navigate('/payment/cart');
      }
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در ثبت‌نام');
    },
  });

  const completePaymentMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/workshops/${slug}/complete-payment/`);
      return response.data;
    },
    onSuccess: (data) => {
      // Redirect to payment gateway
      if (data.payment_url) {
        window.location.href = data.payment_url;
      } else {
        alert('خطا در ایجاد درخواست پرداخت');
      }
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در تکمیل پرداخت');
    },
  });

  // Join session mutation
  const joinSessionMutation = useMutation({
    mutationFn: async (sessionId: number) => {
      return await workshopApi.getSessionAccess(sessionId);
    },
    onSuccess: (data) => {
      if (data.meeting_link) {
        window.open(data.meeting_link, '_blank', 'noopener,noreferrer');
      } else {
        alert('لینک جلسه در دسترس نیست');
      }
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در اتصال به جلسه');
    },
  });

  // Generate certificate mutation
  const generateCertificateMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/workshops/${slug}/certificate/generate/`);
      return response.data;
    },
    onSuccess: (data) => {
      alert(data.message || 'گواهینامه با موفقیت صادر شد');
      refetchCertificate();
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در تولید گواهینامه');
    },
  });

  // Download certificate
  const handleDownloadCertificate = () => {
    if (certificate?.certificate_file_url) {
      window.open(certificate.certificate_file_url, '_blank');
    } else if (certificate?.id) {
      window.open(`/api/workshops/certificates/${certificate.id}/download/`, '_blank');
    }
  };

  // Fetch reviews
  const { data: reviews = [], refetch: refetchReviews } = useQuery({
    queryKey: ['workshop-reviews', slug],
    queryFn: async () => {
      const response = await axios.get(`/api/workshops/${slug}/reviews/`);
      return response.data;
    },
    enabled: !!slug,
  });

  // Create review mutation
  const createReviewMutation = useMutation({
    mutationFn: async (data: {
      rating: number;
      title: string;
      content: string;
      instructor_rating: number;
      content_rating: number;
      interaction_rating: number;
    }) => {
      const response = await axios.post(`/api/workshops/${slug}/review/`, data);
      return response.data;
    },
    onSuccess: () => {
      setReviewRating(5);
      setReviewTitle('');
      setReviewContent('');
      setInstructorRating(5);
      setContentRating(5);
      setInteractionRating(5);
      refetchReviews();
      alert('نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده خواهد شد.');
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در ثبت نظر');
    },
  });

  const handleSubmitReview = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (!reviewTitle.trim() || !reviewContent.trim()) {
      alert('لطفاً عنوان و متن نظر را وارد کنید');
      return;
    }
    createReviewMutation.mutate({
      rating: reviewRating,
      title: reviewTitle,
      content: reviewContent,
      instructor_rating: instructorRating,
      content_rating: contentRating,
      interaction_rating: interactionRating,
    });
  };

  const renderStarRating = (value: number, onChange: (value: number) => void, label: string) => {
    return (
      <div className="mb-3">
        <label className="form-label">{label}</label>
        <div className="d-flex align-items-center gap-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className="btn btn-link p-0 border-0"
              onClick={() => onChange(star)}
              style={{ fontSize: '1.5rem', color: star <= value ? '#ffc107' : '#ccc' }}
            >
              <i className="fas fa-star"></i>
            </button>
          ))}
          <span className="text-muted ms-2">({value} از 5)</span>
        </div>
      </div>
    );
  };

  const handleRegister = () => {
    if (!user) {
      navigate('/login');
      return;
    }
    setShowRegisterModal(true);
  };

  const handleConfirmRegister = () => {
    registerMutation.mutate({ payment_type: paymentType });
  };

  if (isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3 text-muted">در حال بارگذاری...</p>
      </Container>
    );
  }

  if (!workshop) {
    return (
      <Container className="py-5">
        <Alert variant="danger">کارگاه مورد نظر یافت نشد</Alert>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>{workshop.title} - کارگاه‌های آموزشی</title>
        <meta name="description" content={workshop.short_description} />
      </Helmet>

      <Container className="py-5">
        <Row>
          {/* Main Content */}
          <Col lg={8}>
            {/* Hero Section */}
            {workshop.thumbnail && (
              <Card className="mb-4">
                <Card.Img
                  variant="top"
                  src={workshop.thumbnail}
                  alt={workshop.title}
                  loading="lazy"
                  style={{ height: '400px', objectFit: 'cover' }}
                />
              </Card>
            )}

            <Card className="mb-4">
              <Card.Body>
                <div className="mb-3">
                  <Badge bg="info" className="ms-2">{workshop.category.name}</Badge>
                  <Badge bg={workshop.difficulty === 'beginner' ? 'success' : workshop.difficulty === 'intermediate' ? 'warning' : 'danger'}>
                    {workshop.difficulty === 'beginner' && 'مقدماتی'}
                    {workshop.difficulty === 'intermediate' && 'متوسط'}
                    {workshop.difficulty === 'advanced' && 'پیشرفته'}
                  </Badge>
                </div>

                <h1 className="mb-3">{workshop.title}</h1>
                <p className="text-muted lead">{workshop.short_description}</p>

                <div className="d-flex align-items-center flex-wrap gap-4 mb-4">
                  <div className="d-inline-flex align-items-center gap-2">
                    <i className="fas fa-user text-primary" aria-hidden="true"></i>
                    <span>{workshop.instructor_name}</span>
                  </div>
                  <div className="d-inline-flex align-items-center gap-2">
                    <i className="fas fa-users text-primary" aria-hidden="true"></i>
                    <span>{workshop.current_participants} شرکت‌کننده</span>
                  </div>
                  <div className="d-inline-flex align-items-center gap-2">
                    <i className="fas fa-star text-warning" aria-hidden="true"></i>
                    <span>{workshop.rating.toFixed(1)} ({workshop.review_count} نظر)</span>
                  </div>
                </div>

                {workshop.registration_status.is_registered && (
                  workshop.registration_status.status === 'pending_payment' ? (
                    <Alert variant="warning">
                      <i className="fas fa-exclamation-triangle ms-2"></i>
                      شما در این کارگاه ثبت‌نام کرده‌اید اما پرداخت شما تکمیل نشده است. لطفاً پرداخت را تکمیل کنید.
                    </Alert>
                  ) : (
                    <>
                      <Alert variant="success" className="mb-2">
                        <i className="fas fa-check-circle ms-2"></i>
                        شما در این کارگاه ثبت‌نام کرده‌اید
                        {workshop.registration_status.progress_percentage !== undefined && (
                          <span> - پیشرفت: {workshop.registration_status.progress_percentage.toFixed(0)}%</span>
                        )}
                      </Alert>
                      <Alert variant="info" className="mb-0">
                        <i className="fas fa-info-circle ms-2" aria-hidden="true"></i>
                        لینک جلسات در حال برگزاری در جدول جلسات قابل مشاهده خواهد بود
                        <br />
                        و ویدیو جلسات ضبط شده نیز در اختیار شما قرار خواهد گرفت
                      </Alert>
                    </>
                  )
                )}
              </Card.Body>
            </Card>

            {/* Tabs */}
            <Card>
              <Card.Body>
                <Tabs defaultActiveKey="description" className="mb-3">
                  <Tab eventKey="description" title="توضیحات">
                    <div dangerouslySetInnerHTML={{ __html: workshop.description }} />
                    
                    {workshop.prerequisites && (
                      <>
                        <h5 className="mt-4 mb-3">پیش‌نیازها</h5>
                        <div dangerouslySetInnerHTML={{ __html: workshop.prerequisites }} />
                      </>
                    )}

                    <h5 className="mt-4 mb-3">اهداف یادگیری</h5>
                    <div dangerouslySetInnerHTML={{ __html: workshop.learning_objectives }} />
                  </Tab>

                  <Tab eventKey="sessions" title={`جلسات (${workshop.sessions.length})`}>
                    <ListGroup variant="flush">
                      {workshop.sessions.map((session) => (
                        <ListGroup.Item key={session.id}>
                          <div className="d-flex justify-content-between align-items-start">
                            <div className="flex-grow-1">
                              <h6 className="mb-2">
                                جلسه {session.session_number}: {session.title}
                                {session.is_completed && (
                                  <Badge bg="success" className="me-2">تمام شده</Badge>
                                )}
                              </h6>
                              {session.description && (
                                <p className="text-muted small mb-2">{session.description}</p>
                              )}
                              <div className="d-inline-flex align-items-center gap-3 small text-muted">
                                <span className="d-inline-flex align-items-center gap-2">
                                  <i className="far fa-calendar-alt" aria-hidden="true"></i>
                                  {session.scheduled_datetime_persian}
                                </span>
                                <span className="d-inline-flex align-items-center gap-2">
                                  <i className="far fa-clock" aria-hidden="true"></i>
                                  {session.duration_minutes} دقیقه
                                </span>
                              </div>
                            </div>
                            <div className="d-flex align-items-center gap-2">
                              {workshop.registration_status.is_registered && 
                               workshop.registration_status.status !== 'pending_payment' &&
                               !workshop.registration_status.has_overdue &&
                               session.can_join && (
                                <>
                                  <Badge bg="primary" className="me-2">قابل پیوستن</Badge>
                                  <Button
                                    variant="success"
                                    size="sm"
                                    onClick={() => joinSessionMutation.mutate(session.id)}
                                    disabled={joinSessionMutation.isPending}
                                  >
                                    <i className="fas fa-video me-2"></i>
                                    {joinSessionMutation.isPending ? 'در حال اتصال...' : 'ورود به جلسه'}
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  </Tab>
                  {workshop.registration_status.is_registered && workshop.registration_status.payment_type === 'installment' && (
                    <Tab eventKey="installments" title="پرداخت‌ها">
                      {workshop.registration_status.has_overdue && (
                        <Alert variant="danger">
                          قسط بعدی شما سررسید شده است و تا زمان پرداخت دسترسی شما محدود خواهد بود.
                          <Button
                            variant="outline-light"
                            size="sm"
                            className="ms-2"
                            onClick={() => completePaymentMutation.mutate()}
                            disabled={completePaymentMutation.isPending}
                          >
                            {completePaymentMutation.isPending ? 'در حال انتقال...' : 'پرداخت قسط بعدی'}
                          </Button>
                        </Alert>
                      )}
                      {!installmentsData ? (
                        <Alert variant="info">در حال بارگذاری اطلاعات اقساط...</Alert>
                      ) : (
                        <>
                          <div className="mb-3 small text-muted">
                            مبلغ هر قسط: {parseInt(String(installmentsData.plan.installment_amount)).toLocaleString()} تومان |
                            {' '}باقیمانده: {parseInt(String(installmentsData.plan.remaining_amount)).toLocaleString()} تومان
                          </div>
                          <Table responsive hover className="align-middle">
                            <thead>
                              <tr>
                                <th>قسط</th>
                                <th>مبلغ</th>
                                <th>سررسید</th>
                                <th>وضعیت</th>
                                <th>تاریخ پرداخت</th>
                              </tr>
                            </thead>
                            <tbody>
                              {installmentsData.payments.map((p) => (
                                <tr key={p.id} className={p.status === 'overdue' ? 'table-danger' : ''}>
                                  <td>{p.installment_number}</td>
                                  <td>{parseInt(String(p.amount)).toLocaleString()} تومان</td>
                                  <td>{p.due_date_persian}</td>
                                  <td>
                                    <Badge bg={p.status === 'paid' ? 'success' : p.status === 'overdue' ? 'danger' : 'warning'}>
                                      {p.status === 'paid' ? 'پرداخت شده' : p.status === 'overdue' ? 'معوق' : 'در انتظار'}
                                    </Badge>
                                  </td>
                                  <td>{p.paid_at ? new Date(p.paid_at).toLocaleDateString('fa-IR') : '-'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        </>
                      )}
                    </Tab>
                  )}
                  
                  {workshop.registration_status.is_registered && workshop.registration_status.status !== 'pending_payment' && (
                    <Tab
                      eventKey="videos"
                      title={`ویدیوها (${workshop.sessions.filter(s => s.has_recording).length})`}
                    >
                      {workshop.sessions.filter(s => s.has_recording).length === 0 ? (
                        <Alert variant="info" className="mb-0">ویدیویی برای نمایش موجود نیست</Alert>
                      ) : (
                        <div>
                          <p className="text-muted mb-3">
                            برای مشاهده ویدیوهای جلسات ضبط‌شده روی دکمه زیر کلیک کنید.
                          </p>
                          <Button
                            variant="primary"
                            onClick={() => navigate(`/workshops/${workshop.slug}/videos`)}
                          >
                            مشاهده ویدیوها
                          </Button>
                        </div>
                      )}
                    </Tab>
                  )}

                  {/* Reviews Tab */}
                  <Tab eventKey="reviews" title={`نظرات (${reviews?.length || 0})`}>
                    <div className="py-3">
                      {/* Review Form - Only for registered users */}
                      {workshop.registration_status?.is_registered && workshop.registration_status?.status !== 'pending_payment' ? (
                        <Card className="mb-4">
                          <Card.Body>
                            <h5 className="mb-3">ثبت نظر جدید</h5>
                            <div className="mb-3">
                              <label className="form-label">عنوان نظر</label>
                              <input
                                type="text"
                                className="form-control"
                                placeholder="عنوان نظر خود را وارد کنید..."
                                value={reviewTitle}
                                onChange={(e) => setReviewTitle(e.target.value)}
                                disabled={createReviewMutation.isPending}
                              />
                            </div>
                            {renderStarRating(reviewRating, setReviewRating, 'امتیاز کلی')}
                            {renderStarRating(instructorRating, setInstructorRating, 'امتیاز مدرس')}
                            {renderStarRating(contentRating, setContentRating, 'کیفیت محتوا')}
                            {renderStarRating(interactionRating, setInteractionRating, 'تعامل و پشتیبانی')}
                            <div className="mb-3">
                              <label className="form-label">متن نظر</label>
                              <textarea
                                className="form-control"
                                rows={5}
                                placeholder="نظر خود را در مورد این کارگاه بنویسید..."
                                value={reviewContent}
                                onChange={(e) => setReviewContent(e.target.value)}
                                disabled={createReviewMutation.isPending}
                              />
                            </div>
                            <Button
                              variant="primary"
                              onClick={handleSubmitReview}
                              disabled={createReviewMutation.isPending || !reviewTitle.trim() || !reviewContent.trim()}
                            >
                              {createReviewMutation.isPending ? (
                                <>
                                  <Spinner size="sm" className="me-2" />
                                  در حال ارسال...
                                </>
                              ) : (
                                <>
                                  <i className="fas fa-paper-plane me-2"></i>
                                  ارسال نظر
                                </>
                              )}
                            </Button>
                          </Card.Body>
                        </Card>
                      ) : (
                        <Alert variant="info" className="mb-4">
                          <i className="fas fa-info-circle me-2"></i>
                          فقط شرکت‌کنندگان کارگاه می‌توانند نظر بدهند.
                        </Alert>
                      )}

                      {/* Reviews List */}
                      {reviews.length > 0 ? (
                        <div>
                          <h5 className="mb-3">نظرات کاربران ({reviews.length})</h5>
                          {reviews.map((review: any) => (
                            <Card key={review.id} className="mb-3">
                              <Card.Body>
                                <div className="d-flex justify-content-between align-items-start mb-2">
                                  <div>
                                    <strong>{review.user_name}</strong>
                                    <div className="mb-2">
                                      {[...Array(5)].map((_, i) => (
                                        <i
                                          key={i}
                                          className={`fas fa-star ${i < review.rating ? 'text-warning' : 'text-muted'}`}
                                        ></i>
                                      ))}
                                    </div>
                                    {review.title && <h6 className="mb-2">{review.title}</h6>}
                                    <small className="text-muted">
                                      <i className="fas fa-clock me-1"></i>
                                      {new Date(review.created_at).toLocaleDateString('fa-IR')}
                                    </small>
                                  </div>
                                </div>
                                <p className="mb-2" style={{ whiteSpace: 'pre-wrap' }}>
                                  {review.content}
                                </p>
                                {(review.instructor_rating || review.content_rating || review.interaction_rating) && (
                                  <div className="mt-3 p-2 bg-light rounded">
                                    <small className="text-muted d-block mb-1">امتیازهای جزئی:</small>
                                    {review.instructor_rating && (
                                      <div className="small">
                                        <span>مدرس: </span>
                                        {[...Array(5)].map((_, i) => (
                                          <i
                                            key={i}
                                            className={`fas fa-star ${i < review.instructor_rating ? 'text-warning' : 'text-muted'}`}
                                            style={{ fontSize: '0.8rem' }}
                                          ></i>
                                        ))}
                                      </div>
                                    )}
                                    {review.content_rating && (
                                      <div className="small">
                                        <span>محتوا: </span>
                                        {[...Array(5)].map((_, i) => (
                                          <i
                                            key={i}
                                            className={`fas fa-star ${i < review.content_rating ? 'text-warning' : 'text-muted'}`}
                                            style={{ fontSize: '0.8rem' }}
                                          ></i>
                                        ))}
                                      </div>
                                    )}
                                    {review.interaction_rating && (
                                      <div className="small">
                                        <span>تعامل: </span>
                                        {[...Array(5)].map((_, i) => (
                                          <i
                                            key={i}
                                            className={`fas fa-star ${i < review.interaction_rating ? 'text-warning' : 'text-muted'}`}
                                            style={{ fontSize: '0.8rem' }}
                                          ></i>
                                        ))}
                                      </div>
                                    )}
                                  </div>
                                )}
                              </Card.Body>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <Alert variant="info" className="text-center">
                          هنوز نظری برای این کارگاه ثبت نشده است.
                        </Alert>
                      )}
                    </div>
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
                  {workshop.discount_price ? (
                    <>
                      <div className="text-decoration-line-through text-muted mb-2">
                        {parseInt(workshop.price).toLocaleString()} تومان
                      </div>
                      <div className="h3 text-primary mb-0">
                        {parseInt(workshop.current_price).toLocaleString()} تومان
                        <Badge bg="danger" className="me-2">{workshop.discount_percentage}%</Badge>
                      </div>
                    </>
                  ) : (
                    <div className="h3 text-primary mb-0">
                      {parseInt(workshop.price).toLocaleString()} تومان
                    </div>
                  )}
                </div>

                <ListGroup variant="flush" className="mb-4">
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="d-inline-flex align-items-center gap-2"><i className="fas fa-calendar" aria-hidden="true"></i><span>تاریخ شروع</span></span>
                    <strong>{workshop.start_date_persian}</strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="d-inline-flex align-items-center gap-2"><i className="fas fa-clock" aria-hidden="true"></i><span>مدت زمان</span></span>
                    <strong>{workshop.total_hours} ساعت</strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="d-inline-flex align-items-center gap-2"><i className="fas fa-users" aria-hidden="true"></i><span>ظرفیت</span></span>
                    <strong>
                      {workshop.is_full ? (
                        <Badge bg="danger">تکمیل</Badge>
                      ) : (
                        `${workshop.available_seats} نفر`
                      )}
                    </strong>
                  </ListGroup.Item>
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="d-inline-flex align-items-center gap-2"><i className="fas fa-credit-card" aria-hidden="true"></i><span>نوع پرداخت</span></span>
                    <strong>
                      {workshop.payment_type === 'both' && 'کامل یا قسطی'}
                      {workshop.payment_type === 'full_payment' && 'فقط کامل'}
                      {workshop.payment_type === 'installment' && 'فقط قسطی'}
                    </strong>
                  </ListGroup.Item>
                  {workshop.payment_type !== 'full_payment' && (
                    <ListGroup.Item className="d-flex justify-content-between">
                      <span className="d-inline-flex align-items-center gap-2"><i className="fas fa-money-bill" aria-hidden="true"></i><span>قسط ماهانه</span></span>
                      <strong>{parseInt(workshop.installment_amount).toLocaleString()} تومان</strong>
                    </ListGroup.Item>
                  )}
                  <ListGroup.Item className="d-flex justify-content-between">
                    <span className="d-inline-flex align-items-center gap-2"><i className="fas fa-hourglass-end" aria-hidden="true"></i><span>مهلت ثبت‌نام</span></span>
                    <strong className="text-danger">{workshop.registration_deadline_persian}</strong>
                  </ListGroup.Item>
                </ListGroup>

                <div className="d-grid gap-2">
                  {!workshop.registration_status.is_registered ? (
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={handleRegister}
                      disabled={workshop.is_full}
                    >
                      {workshop.is_full ? 'ظرفیت تکمیل شد' : 'ثبت‌نام در کارگاه'}
                    </Button>
                  ) : workshop.registration_status.status === 'pending_payment' ? (
                    <Button
                      variant="warning"
                      size="lg"
                      onClick={() => completePaymentMutation.mutate()}
                      disabled={completePaymentMutation.isPending}
                    >
                      {completePaymentMutation.isPending ? 'در حال پردازش...' : 'تکمیل پرداخت'}
                    </Button>
                  ) : (
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={() => navigate('/dashboard/my-workshops')}
                    >
                      کارگاه های من
                    </Button>
                  )}
                </div>
              </Card.Body>
            </Card>

            {/* Certificate Card */}
            {workshop.registration_status.is_registered && workshop.registration_status.status !== 'pending_payment' && (
              <Card className="mb-4" style={{ 
                border: 'none',
                borderRadius: '15px',
                boxShadow: '0 5px 15px rgba(0,0,0,0.08)',
                overflow: 'hidden'
              }}>
                <Card.Header style={{
                  background: 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)',
                  border: 'none',
                  padding: '1.25rem 1.5rem'
                }}>
                  <div className="d-flex align-items-center gap-3">
                    <div style={{
                      width: '48px',
                      height: '48px',
                      background: 'rgba(255,255,255,0.25)',
                      borderRadius: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backdropFilter: 'blur(10px)'
                    }}>
                      <i className="fas fa-certificate" style={{ fontSize: '1.5rem', color: '#fff' }}></i>
                    </div>
                    <div>
                      <h5 className="mb-0 text-white" style={{ fontWeight: '700', fontSize: '1.1rem' }}>
                        گواهینامه تکمیل دوره
                      </h5>
                      <p className="mb-0 text-white small" style={{ opacity: 0.9, fontSize: '0.85rem' }}>
                        مدرک رسمی تکمیل کارگاه آموزشی
                      </p>
                    </div>
                  </div>
                </Card.Header>
                <Card.Body style={{ padding: '1.5rem' }}>
                  {certificateLoading ? (
                    <div className="text-center py-4">
                      <Spinner animation="border" variant="warning" size="sm" />
                      <p className="mt-3 text-muted small">در حال بارگذاری اطلاعات گواهینامه...</p>
                    </div>
                  ) : certificate && certificate.status === 'issued' ? (
                    <>
                      {/* Success State */}
                      <div style={{
                        background: 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
                        borderRadius: '12px',
                        padding: '1.25rem',
                        marginBottom: '1.25rem',
                        border: '2px solid #28a745'
                      }}>
                        <div className="d-flex align-items-start gap-3 mb-3">
                          <div style={{
                            width: '40px',
                            height: '40px',
                            background: '#28a745',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                          }}>
                            <i className="fas fa-check text-white"></i>
                          </div>
                          <div className="flex-grow-1">
                            <h6 className="mb-2 text-success" style={{ fontWeight: '700', fontSize: '1rem' }}>
                              تبریک! گواهینامه شما با موفقیت صادر شد
                            </h6>
                            <div className="small text-muted mb-2">
                              <div className="mb-1">
                                <i className="fas fa-hashtag me-2"></i>
                                <strong>شماره گواهینامه:</strong> {certificate.certificate_number}
                              </div>
                              {certificate.issued_at_persian && (
                                <div>
                                  <i className="far fa-calendar-alt me-2"></i>
                                  <strong>تاریخ صدور:</strong> {certificate.issued_at_persian}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      <Button
                        variant="success"
                        size="lg"
                        onClick={handleDownloadCertificate}
                        className="w-100 mb-3 d-flex align-items-center justify-content-center gap-2"
                        style={{
                          borderRadius: '12px',
                          fontWeight: '600',
                          padding: '0.75rem',
                          background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
                          border: 'none',
                          boxShadow: '0 4px 15px rgba(40, 167, 69, 0.3)'
                        }}
                      >
                        <i className="fas fa-download"></i>
                        دانلود گواهینامه PDF
                      </Button>

                      {/* Verification Code Section */}
                      <Card style={{
                        background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                        border: '2px dashed #6c757d',
                        borderRadius: '12px'
                      }}>
                        <Card.Body className="p-3">
                          <div className="d-flex align-items-center gap-2 mb-2">
                            <i className="fas fa-shield-alt text-primary"></i>
                            <strong className="small">کد تأیید اعتبار گواهینامه:</strong>
                          </div>
                          <div className="d-flex align-items-center gap-2 mb-2">
                            <code className="bg-white p-2 rounded flex-grow-1 text-center small border" style={{
                              fontFamily: 'monospace',
                              letterSpacing: '1px',
                              fontWeight: '600',
                              color: '#2c5aa0'
                            }}>
                              {certificate.verification_code}
                            </code>
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => {
                                navigator.clipboard.writeText(certificate.verification_code);
                                alert('کد تأیید با موفقیت کپی شد');
                              }}
                              style={{ borderRadius: '8px' }}
                            >
                              <i className="fas fa-copy"></i>
                            </Button>
                          </div>
                          <p className="text-muted small mb-0" style={{ fontSize: '0.8rem', lineHeight: '1.6' }}>
                            <i className="fas fa-info-circle me-1"></i>
                            این کد منحصر به فرد را می‌توانید با کارفرمایان یا سایر افراد به اشتراک بگذارید تا آن‌ها بتوانند اعتبار گواهینامه شما را آنلاین تأیید کنند.
                          </p>
                        </Card.Body>
                      </Card>
                    </>
                  ) : (
                    <>
                      {/* Information Section */}
                      <div style={{
                        background: 'linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%)',
                        borderRadius: '12px',
                        padding: '1.25rem',
                        marginBottom: '1.25rem',
                        border: '2px solid #17a2b8'
                      }}>
                        <div className="d-flex align-items-start gap-3 mb-3">
                          <div style={{
                            width: '40px',
                            height: '40px',
                            background: '#17a2b8',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                          }}>
                            <i className="fas fa-info text-white"></i>
                          </div>
                          <div className="flex-grow-1">
                            <h6 className="mb-2 text-info" style={{ fontWeight: '700', fontSize: '1rem' }}>
                              درباره گواهینامه تکمیل دوره
                            </h6>
                            <p className="text-muted small mb-0" style={{ lineHeight: '1.7', fontSize: '0.9rem' }}>
                              گواهینامه تکمیل دوره، مدرک رسمی و قابل تأییدی است که نشان می‌دهد شما این کارگاه آموزشی را با موفقیت به پایان رسانده‌اید. این گواهینامه می‌تواند در رزومه‌ی کاری و مسیر شغلی شما مفید باشد.
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Requirements Section */}
                      <div className="mb-3">
                        <h6 className="mb-3" style={{ 
                          fontWeight: '700',
                          fontSize: '0.95rem',
                          color: '#2c3e50',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}>
                          <i className="fas fa-tasks text-primary"></i>
                          شرایط دریافت گواهینامه
                        </h6>
                        
                        <div className="d-flex flex-column gap-2">
                          {/* Requirement 1 */}
                          <div style={{
                            background: workshop.registration_status.status === 'completed' ? '#d4edda' : '#f8f9fa',
                            borderRadius: '10px',
                            padding: '0.875rem',
                            border: `2px solid ${workshop.registration_status.status === 'completed' ? '#28a745' : '#dee2e6'}`,
                            transition: 'all 0.3s ease'
                          }}>
                            <div className="d-flex align-items-center gap-2">
                              <Badge 
                                bg={workshop.registration_status.status === 'completed' ? 'success' : 'secondary'} 
                                style={{ 
                                  width: '28px',
                                  height: '28px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  borderRadius: '50%',
                                  fontSize: '0.75rem'
                                }}
                              >
                                {workshop.registration_status.status === 'completed' ? (
                                  <i className="fas fa-check"></i>
                                ) : (
                                  <i className="fas fa-clock"></i>
                                )}
                              </Badge>
                              <div className="flex-grow-1">
                                <strong className="small">وضعیت ثبت‌نام:</strong>
                                <span className={`ms-2 small ${workshop.registration_status.status === 'completed' ? 'text-success' : 'text-muted'}`}>
                                  {workshop.registration_status.status === 'completed' ? '✓ تکمیل شده' : 'در حال برگزاری'}
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Requirement 2 */}
                          <div style={{
                            background: (workshop.registration_status.progress_percentage && workshop.registration_status.progress_percentage >= 80) ? '#d4edda' : '#f8f9fa',
                            borderRadius: '10px',
                            padding: '0.875rem',
                            border: `2px solid ${(workshop.registration_status.progress_percentage && workshop.registration_status.progress_percentage >= 80) ? '#28a745' : '#dee2e6'}`,
                            transition: 'all 0.3s ease'
                          }}>
                            <div className="d-flex align-items-center gap-2 mb-2">
                              <Badge 
                                bg={(workshop.registration_status.progress_percentage && workshop.registration_status.progress_percentage >= 80) ? 'success' : 'secondary'} 
                                style={{ 
                                  width: '28px',
                                  height: '28px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  borderRadius: '50%',
                                  fontSize: '0.75rem'
                                }}
                              >
                                {(workshop.registration_status.progress_percentage && workshop.registration_status.progress_percentage >= 80) ? (
                                  <i className="fas fa-check"></i>
                                ) : (
                                  <i className="fas fa-clock"></i>
                                )}
                              </Badge>
                              <div className="flex-grow-1">
                                <strong className="small">پیشرفت دوره:</strong>
                                <span className={`ms-2 small ${(workshop.registration_status.progress_percentage && workshop.registration_status.progress_percentage >= 80) ? 'text-success' : 'text-muted'}`}>
                                  {workshop.registration_status.progress_percentage?.toFixed(0) || 0}% (حداقل 80% مورد نیاز)
                                  {(workshop.registration_status.progress_percentage && workshop.registration_status.progress_percentage >= 80) && ' ✓'}
                                </span>
                              </div>
                            </div>
                            {workshop.registration_status.progress_percentage && workshop.registration_status.progress_percentage < 80 && (
                              <div className="progress mt-2" style={{ height: '8px', borderRadius: '10px', backgroundColor: '#e9ecef' }}>
                                <div
                                  className="progress-bar"
                                  role="progressbar"
                                  style={{ 
                                    width: `${workshop.registration_status.progress_percentage}%`,
                                    background: 'linear-gradient(90deg, #17a2b8 0%, #138496 100%)',
                                    borderRadius: '10px',
                                    transition: 'width 0.6s ease'
                                  }}
                                  aria-valuenow={workshop.registration_status.progress_percentage}
                                  aria-valuemin={0}
                                  aria-valuemax={100}
                                ></div>
                              </div>
                            )}
                          </div>

                          {/* Requirement 3 */}
                          <div style={{
                            background: workshop.status === 'completed' ? '#d4edda' : '#f8f9fa',
                            borderRadius: '10px',
                            padding: '0.875rem',
                            border: `2px solid ${workshop.status === 'completed' ? '#28a745' : '#dee2e6'}`,
                            transition: 'all 0.3s ease'
                          }}>
                            <div className="d-flex align-items-center gap-2">
                              <Badge 
                                bg={workshop.status === 'completed' ? 'success' : 'secondary'} 
                                style={{ 
                                  width: '28px',
                                  height: '28px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  borderRadius: '50%',
                                  fontSize: '0.75rem'
                                }}
                              >
                                {workshop.status === 'completed' ? (
                                  <i className="fas fa-check"></i>
                                ) : (
                                  <i className="fas fa-clock"></i>
                                )}
                              </Badge>
                              <div className="flex-grow-1">
                                <strong className="small">وضعیت کارگاه:</strong>
                                <span className={`ms-2 small ${workshop.status === 'completed' ? 'text-success' : 'text-muted'}`}>
                                  {workshop.status === 'completed' ? '✓ کارگاه به پایان رسیده است' : 'کارگاه در حال برگزاری است'}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Process Explanation */}
                      <Card style={{
                        background: 'linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%)',
                        border: '1px solid #ffc107',
                        borderRadius: '12px',
                        marginBottom: '1.25rem'
                      }}>
                        <Card.Body className="p-3">
                          <h6 className="mb-3 small" style={{ fontWeight: '700', color: '#856404' }}>
                            <i className="fas fa-list-ol me-2"></i>
                            فرآیند دریافت گواهینامه:
                          </h6>
                          <ol className="mb-0 small" style={{ 
                            paddingRight: '1.25rem',
                            lineHeight: '1.8',
                            color: '#856404',
                            margin: 0
                          }}>
                            <li className="mb-2">
                              <strong>تکمیل دوره:</strong> حداقل 80% از جلسات کارگاه را با موفقیت به پایان برسانید.
                            </li>
                            <li className="mb-2">
                              <strong>پایان کارگاه:</strong> منتظر بمانید تا کارگاه به طور کامل به پایان برسد.
                            </li>
                            <li className="mb-2">
                              <strong>دریافت گواهینامه:</strong> پس از تکمیل شرایط، روی دکمه "دریافت گواهینامه" کلیک کنید.
                            </li>
                            <li>
                              <strong>دانلود و استفاده:</strong> گواهینامه شما به صورت PDF صادر می‌شود و می‌توانید آن را دانلود و استفاده کنید.
                            </li>
                          </ol>
                        </Card.Body>
                      </Card>

                      {/* Action Button */}
                      {workshop.registration_status.status === 'completed' &&
                       workshop.registration_status.progress_percentage &&
                       workshop.registration_status.progress_percentage >= 80 &&
                       workshop.status === 'completed' ? (
                        <Button
                          variant="warning"
                          size="lg"
                          onClick={() => generateCertificateMutation.mutate()}
                          disabled={generateCertificateMutation.isPending}
                          className="w-100 d-flex align-items-center justify-content-center gap-2"
                          style={{
                            borderRadius: '12px',
                            fontWeight: '700',
                            padding: '0.875rem',
                            background: 'linear-gradient(135deg, #ffc107 0%, #ff9800 100%)',
                            border: 'none',
                            boxShadow: '0 4px 15px rgba(255, 193, 7, 0.4)',
                            fontSize: '1rem'
                          }}
                        >
                          {generateCertificateMutation.isPending ? (
                            <>
                              <Spinner animation="border" size="sm" />
                              <span>در حال تولید گواهینامه...</span>
                            </>
                          ) : (
                            <>
                              <i className="fas fa-certificate"></i>
                              <span>دریافت گواهینامه</span>
                            </>
                          )}
                        </Button>
                      ) : (
                        <Alert variant="warning" className="mb-0" style={{
                          borderRadius: '12px',
                          border: '2px solid #ffc107',
                          backgroundColor: '#fff9e6'
                        }}>
                          <div className="d-flex align-items-start gap-2">
                            <i className="fas fa-exclamation-triangle mt-1" style={{ color: '#856404' }}></i>
                            <div className="small" style={{ color: '#856404', lineHeight: '1.6' }}>
                              <strong>توجه:</strong> برای دریافت گواهینامه باید تمام شرایط بالا برقرار باشند. لطفاً ادامه دهید و پس از تکمیل شرایط، دوباره مراجعه کنید.
                            </div>
                          </div>
                        </Alert>
                      )}

                      {certificate && certificate.status === 'pending' && (
                        <Alert variant="info" className="mt-3 mb-0" style={{
                          borderRadius: '12px',
                          border: '2px solid #17a2b8'
                        }}>
                          <div className="d-flex align-items-center gap-2">
                            <Spinner animation="border" size="sm" variant="info" />
                            <span className="small">گواهینامه شما در حال آماده‌سازی است. لطفاً چند لحظه صبر کنید و صفحه را رفرش کنید.</span>
                          </div>
                        </Alert>
                      )}
                    </>
                  )}
                </Card.Body>
              </Card>
            )}
          </Col>
        </Row>
      </Container>

      {/* Register Modal */}
      <Modal show={showRegisterModal} onHide={() => setShowRegisterModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>ثبت‌نام در کارگاه</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p className="mb-4">لطفاً نوع پرداخت را انتخاب کنید:</p>
          
          <Form>
            {(workshop.payment_type === 'both' || workshop.payment_type === 'full_payment') && (
              <Form.Check
                type="radio"
                id="full_payment"
                label={
                  <div>
                    <strong>پرداخت کامل</strong>
                    <div className="text-muted small">
                      {parseInt(workshop.current_price).toLocaleString()} تومان
                    </div>
                  </div>
                }
                value="full_payment"
                checked={paymentType === 'full_payment'}
                onChange={(e) => setPaymentType(e.target.value)}
                className="mb-3"
              />
            )}

            {(workshop.payment_type === 'both' || workshop.payment_type === 'installment') && (
              <Form.Check
                type="radio"
                id="installment"
                label={
                  <div>
                    <strong>پرداخت قسطی</strong>
                    <div className="text-muted small">
                      {workshop.installment_months} قسط × {parseInt(workshop.installment_amount).toLocaleString()} تومان
                    </div>
                  </div>
                }
                value="installment"
                checked={paymentType === 'installment'}
                onChange={(e) => setPaymentType(e.target.value)}
              />
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowRegisterModal(false)}>
            انصراف
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirmRegister}
            disabled={registerMutation.isPending}
          >
            {registerMutation.isPending ? 'در حال ثبت‌نام...' : 'تأیید و ثبت‌نام'}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default WorkshopDetail;

