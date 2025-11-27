import React, { useState } from 'react';
import { Container, Row, Col, Card, Badge, Button, Alert, Spinner, Tab, Tabs, ListGroup, Modal } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';
import { Link } from 'react-router-dom';
import { workshopApi, WorkshopRegistration, WorkshopSession } from '../../services/workshopApi';

const MyWorkshops: React.FC = () => {
  const { user } = useAuth();
  const { t } = useI18n();
  const [selectedWorkshop, setSelectedWorkshop] = useState<WorkshopRegistration | null>(null);
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [selectedSession, setSelectedSession] = useState<WorkshopSession | null>(null);

  // Debug: Log current user
  console.log('Current user in MyWorkshops:', user);
  console.log('User email:', user?.email);
  console.log('User ID:', user?.id);

  // Fetch user's registered workshops
  const { data: workshops, isLoading, error } = useQuery<WorkshopRegistration[]>({
    queryKey: ['user-workshops'],
    queryFn: async () => {
      try {
        const data = await workshopApi.getUserWorkshops();
        console.log('Workshops data received:', data);
        console.log('Is array:', Array.isArray(data));
        console.log('Data type:', typeof data);
        return data;
      } catch (err) {
        console.error('Error in query function:', err);
        throw err;
      }
    },
    retry: 1,
    retryDelay: 1000,
  });

  // Join session mutation
  const joinSessionMutation = useMutation({
    mutationFn: workshopApi.getSessionAccess,
    onSuccess: (data) => {
      if (data.meeting_link) {
        window.open(data.meeting_link, '_blank');
      } else {
        alert('لینک جلسه در دسترس نیست');
      }
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در اتصال به جلسه');
    },
  });

  const handleJoinSession = (session: WorkshopSession) => {
    setSelectedSession(session);
    setShowSessionModal(true);
  };

  const confirmJoinSession = () => {
    if (selectedSession) {
      joinSessionMutation.mutate(selectedSession.id);
      setShowSessionModal(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge bg="success">تکمیل شده</Badge>;
      case 'in_progress':
        return <Badge bg="primary">در حال برگزاری</Badge>;
      case 'pending_payment':
        return <Badge bg="warning">در انتظار پرداخت</Badge>;
      case 'cancelled':
        return <Badge bg="danger">لغو شده</Badge>;
      default:
        return <Badge bg="secondary">نامشخص</Badge>;
    }
  };

  const getPaymentTypeText = (paymentType: string) => {
    switch (paymentType) {
      case 'full_payment':
        return 'پرداخت کامل';
      case 'installment':
        return 'پرداخت قسطی';
      default:
        return paymentType;
    }
  };

  if (isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3 text-muted">در حال بارگذاری کارگاه‌های شما...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          خطا در بارگذاری کارگاه‌ها. لطفاً دوباره تلاش کنید.
          <br />
          <small>Error: {error.message}</small>
          <br />
          <small>اگر این مشکل ادامه دارد، لطفاً از حساب کاربری خود خارج شده و دوباره وارد شوید.</small>
        </Alert>
      </Container>
    );
  }

  // Debug logging
  console.log('Current workshops data:', workshops);
  console.log('Is array:', Array.isArray(workshops));
  console.log('Type:', typeof workshops);
  console.log('Length:', workshops?.length);
  console.log('First item:', workshops?.[0]);

  if (!workshops || !Array.isArray(workshops) || workshops.length === 0) {
    return (
      <Container className="py-5">
        <Helmet>
          <title>کارگاه‌های من - داشبورد کاربری</title>
        </Helmet>
        
        <div className="text-center">
          <div className="mb-4">
            <i className="fas fa-chalkboard-teacher text-muted" style={{ fontSize: '4rem' }}></i>
          </div>
          <h3 className="mb-3">هنوز در هیچ کارگاهی ثبت‌نام نکرده‌اید</h3>
          <p className="text-muted mb-4">
            برای شرکت در کارگاه‌های آموزشی، ابتدا در یکی از کارگاه‌های موجود ثبت‌نام کنید.
          </p>
          <Link to="/workshops" className="btn btn-primary btn-lg">
            <i className="fas fa-search me-2"></i>
            مشاهده کارگاه‌ها
          </Link>
        </div>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>کارگاه‌های من - داشبورد کاربری</title>
      </Helmet>

      <Container className="py-5">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 className="mb-2">کارگاه‌های من</h2>
            <p className="text-muted">مدیریت و دسترسی به کارگاه‌های ثبت‌نام شده</p>
          </div>
          <Link to="/workshops" className="btn btn-outline-primary">
            <i className="fas fa-plus me-2"></i>
            ثبت‌نام در کارگاه جدید
          </Link>
        </div>

        <Row>
          {(workshops && Array.isArray(workshops) ? workshops : []).map((registration) => {
            // Safety check for registration object
            if (!registration || !registration.workshop) {
              console.warn('Invalid registration object:', registration);
              return null;
            }
            return (
            <Col lg={6} xl={4} key={registration.id} className="mb-4">
              <Card className="h-100 shadow-sm">
                {registration.workshop?.thumbnail && (
                  <Card.Img
                    variant="top"
                    src={registration.workshop.thumbnail}
                    style={{ height: '200px', objectFit: 'cover' }}
                  />
                )}
                
                <Card.Body className="d-flex flex-column">
                  <div className="mb-3">
                    <Badge bg="info" className="me-2">{(registration.workshop as any)?.category_name || registration.workshop?.category?.name || 'دسته‌بندی نامشخص'}</Badge>
                    {getStatusBadge(registration.status)}
                  </div>

                  <Card.Title className="h5 mb-3">{registration.workshop?.title || 'عنوان نامشخص'}</Card.Title>
                  
                  <Card.Text className="text-muted small mb-3">
                    {registration.workshop?.short_description || 'توضیحات در دسترس نیست'}
                  </Card.Text>

                  <div className="mb-3">
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span className="text-muted">مدرس:</span>
                      <span>{registration.workshop?.instructor_name || 'نامشخص'}</span>
                    </div>
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span className="text-muted">نوع پرداخت:</span>
                      <span>{getPaymentTypeText(registration.payment_type)}</span>
                    </div>
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span className="text-muted">مبلغ کل:</span>
                      <span>{parseInt(registration.total_amount || '0').toLocaleString()} تومان</span>
                    </div>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="text-muted">پرداخت شده:</span>
                      <span>{parseInt(registration.amount_paid || '0').toLocaleString()} تومان</span>
                    </div>
                  </div>

                  {(registration.progress_percentage || 0) > 0 && (
                    <div className="mb-3">
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <small className="text-muted">پیشرفت</small>
                        <small>{(registration.progress_percentage || 0).toFixed(0)}%</small>
                      </div>
                      <div className="progress" style={{ height: '6px' }}>
                        <div
                          className="progress-bar"
                          role="progressbar"
                          style={{ width: `${registration.progress_percentage || 0}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  <div className="mt-auto">
                    <div className="d-grid gap-2">
                      <Link 
                        to={`/workshops/${registration.workshop?.slug || 'unknown'}`}
                        className="btn btn-outline-primary btn-sm"
                      >
                        <i className="fas fa-eye me-2"></i>
                        مشاهده جزئیات
                      </Link>
                      
                      {(registration.workshop?.sessions?.length || 0) > 0 && (
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => setSelectedWorkshop(registration)}
                        >
                          <i className="fas fa-play me-2"></i>
                          جلسات کارگاه
                        </Button>
                      )}
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Col>
            );
          })}
        </Row>

        {/* Workshop Sessions Modal */}
        <Modal 
          show={selectedWorkshop !== null} 
          onHide={() => setSelectedWorkshop(null)}
          size="lg"
          centered
        >
          <Modal.Header closeButton>
            <Modal.Title>
              جلسات کارگاه: {selectedWorkshop?.workshop?.title || 'نامشخص'}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {selectedWorkshop && (
              <ListGroup variant="flush">
                {(selectedWorkshop.workshop?.sessions || []).map((session) => (
                  <ListGroup.Item key={session.id} className="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 className="mb-1">
                        جلسه {session.session_number}: {session.title}
                        {session.is_completed && (
                          <Badge bg="success" className="me-2">تمام شده</Badge>
                        )}
                      </h6>
                      {session.description && (
                        <p className="text-muted small mb-1">{session.description}</p>
                      )}
                      <div className="small text-muted">
                        <i className="fas fa-calendar ms-2"></i>
                        {session.scheduled_datetime_persian}
                        <span className="me-3"></span>
                        <i className="fas fa-clock ms-2"></i>
                        {session.duration_minutes} دقیقه
                      </div>
                    </div>
                    <div>
                      {session.can_join && !session.is_completed && (
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleJoinSession(session)}
                          disabled={joinSessionMutation.isPending}
                        >
                          <i className="fas fa-video me-2"></i>
                          ورود به جلسه
                        </Button>
                      )}
                      {session.is_completed && session.has_recording && (
                        <Button variant="outline-secondary" size="sm">
                          <i className="fas fa-play me-2"></i>
                          مشاهده ضبط
                        </Button>
                      )}
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            )}
          </Modal.Body>
        </Modal>

        {/* Join Session Confirmation Modal */}
        <Modal show={showSessionModal} onHide={() => setShowSessionModal(false)} centered>
          <Modal.Header closeButton>
            <Modal.Title>ورود به جلسه</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>آیا می‌خواهید به جلسه <strong>{selectedSession?.title}</strong> وارد شوید؟</p>
            <div className="small text-muted">
              <i className="fas fa-info-circle me-2"></i>
              جلسه در پنجره جدید باز خواهد شد
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowSessionModal(false)}>
              انصراف
            </Button>
            <Button
              variant="primary"
              onClick={confirmJoinSession}
              disabled={joinSessionMutation.isPending}
            >
              {joinSessionMutation.isPending ? 'در حال اتصال...' : 'ورود به جلسه'}
            </Button>
          </Modal.Footer>
        </Modal>
      </Container>
    </>
  );
};

export default MyWorkshops;
