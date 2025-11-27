import React from 'react';
import { Container, Row, Col, Card, Alert, Button, Spinner, Breadcrumb, Badge } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface WorkshopSession {
  id: number;
  session_number: number;
  title: string;
  description: string;
  scheduled_datetime: string;
  scheduled_datetime_persian: string;
  duration_minutes: number;
  session_video?: string | null;
  has_recording: boolean;
  is_completed: boolean;
}

interface WorkshopDetail {
  id: number;
  title: string;
  slug: string;
  sessions: WorkshopSession[];
  registration_status: {
    is_registered: boolean;
    status?: string;
    payment_type?: string;
    progress_percentage?: number;
    has_overdue?: boolean;
  };
}

const WorkshopVideos: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  const { data: workshop, isLoading, error } = useQuery<WorkshopDetail>({
    queryKey: ['workshop-videos', slug],
    queryFn: async () => {
      const res = await axios.get(`/api/workshops/${slug}/`);
      return res.data;
    },
  });

  if (isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3 text-muted">در حال بارگذاری ویدیوها...</p>
      </Container>
    );
  }

  if (error || !workshop) {
    return (
      <Container className="py-5">
        <Alert variant="danger">خطا در بارگذاری ویدیوهای کارگاه</Alert>
        <Button variant="secondary" onClick={() => navigate(-1)}>بازگشت</Button>
      </Container>
    );
  }

  // Check if user is registered and payment is completed
  if (!workshop.registration_status?.is_registered) {
    return (
      <Container className="py-5">
        <Alert variant="warning">
          <Alert.Heading>دسترسی محدود</Alert.Heading>
          <p>برای مشاهده ویدیوهای این کارگاه، ابتدا باید در کارگاه ثبت‌نام کنید.</p>
          <Button variant="primary" onClick={() => navigate(`/workshops/${workshop.slug}`)}>
            بازگشت به صفحه کارگاه
          </Button>
        </Alert>
      </Container>
    );
  }

  if (workshop.registration_status.status === 'pending_payment') {
    return (
      <Container className="py-5">
        <Alert variant="warning">
          <Alert.Heading>پرداخت تکمیل نشده</Alert.Heading>
          <p>برای مشاهده ویدیوهای این کارگاه، ابتدا باید پرداخت خود را تکمیل کنید.</p>
          <Button variant="primary" onClick={() => navigate(`/workshops/${workshop.slug}`)}>
            بازگشت به صفحه کارگاه
          </Button>
        </Alert>
      </Container>
    );
  }

  const recordedSessions = (workshop.sessions || []).filter((s) => s.has_recording);

  return (
    <>
      <Helmet>
        <title>ویدیوهای {workshop.title} - کارگاه‌های آموزشی</title>
        <meta name="description" content={`ویدیوهای جلسات ضبط‌شده کارگاه ${workshop.title}`} />
      </Helmet>

      <Container className="py-5">
        {/* Breadcrumb */}
        <Row className="mb-4">
          <Col>
            <Breadcrumb className="mb-3">
              <Breadcrumb.Item linkAs={Link} linkProps={{ to: '/workshops' }}>
                <i className="fas fa-home me-1"></i>
                کارگاه‌ها
              </Breadcrumb.Item>
              <Breadcrumb.Item linkAs={Link} linkProps={{ to: `/workshops/${workshop.slug}` }}>
                {workshop.title}
              </Breadcrumb.Item>
              <Breadcrumb.Item active>
                <i className="fas fa-video me-1"></i>
                ویدیوها
              </Breadcrumb.Item>
            </Breadcrumb>

            {/* Header */}
            <div className="d-flex justify-content-between align-items-start mb-4 flex-wrap gap-3">
              <div>
                <h2 className="mb-2 fw-bold">
                  <i className="fas fa-video text-primary me-2"></i>
                  ویدیوهای کارگاه
                </h2>
                <h4 className="text-muted mb-3">{workshop.title}</h4>
                <p className="text-muted mb-0">
                  <i className="fas fa-info-circle me-2"></i>
                  در این صفحه می‌توانید ویدیوهای جلسات ضبط‌شده را مشاهده کنید
                </p>
              </div>
              <Link 
                to={`/workshops/${workshop.slug}`} 
                className="btn btn-outline-primary"
              >
                <i className="fas fa-arrow-right me-2"></i>
                بازگشت به کارگاه
              </Link>
            </div>
          </Col>
        </Row>

        {/* Videos List */}
        {recordedSessions.length === 0 ? (
          <Card className="border-0 shadow-sm">
            <Card.Body className="text-center py-5">
              <div className="mb-4">
                <i className="fas fa-video-slash text-muted" style={{ fontSize: '4rem' }}></i>
              </div>
              <h4 className="mb-3">ویدیویی موجود نیست</h4>
              <p className="text-muted mb-4">
                برای این کارگاه هنوز ویدیویی بارگذاری نشده است.
              </p>
              <Button variant="primary" onClick={() => navigate(`/workshops/${workshop.slug}`)}>
                <i className="fas fa-arrow-right me-2"></i>
                بازگشت به صفحه کارگاه
              </Button>
            </Card.Body>
          </Card>
        ) : (
          <Row>
            {recordedSessions.map((session, index) => (
              <Col key={session.id} lg={12} className="mb-4">
                <Card className="border-0 shadow-sm h-100 workshop-video-card">
                  <Card.Body className="p-4">
                    <Row>
                      <Col lg={8} className="mb-3 mb-lg-0">
                        <div className="d-flex align-items-start mb-3">
                          <div className="session-number-badge me-3">
                            <Badge bg="primary" className="px-3 py-2" style={{ fontSize: '1.1rem' }}>
                              جلسه {session.session_number}
                            </Badge>
                          </div>
                          <div className="flex-grow-1">
                            <h5 className="mb-2 fw-bold">{session.title}</h5>
                            {session.description && (
                              <p className="text-muted small mb-3">{session.description}</p>
                            )}
                            <div className="d-flex flex-wrap gap-3 text-muted small">
                              <span className="d-inline-flex align-items-center">
                                <i className="far fa-calendar-alt me-2 text-primary"></i>
                                {session.scheduled_datetime_persian}
                              </span>
                              <span className="d-inline-flex align-items-center">
                                <i className="far fa-clock me-2 text-primary"></i>
                                {session.duration_minutes} دقیقه
                              </span>
                              {session.is_completed && (
                                <Badge bg="success" className="d-inline-flex align-items-center">
                                  <i className="fas fa-check-circle me-1"></i>
                                  تکمیل شده
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </Col>
                      <Col lg={4}>
                        {session.session_video ? (
                          <div className="video-container-wrapper">
                            <div className="video-container">
                              <video
                                key={`vid-${session.id}`}
                                src={session.session_video || undefined}
                                controls
                                controlsList="nodownload noplaybackrate"
                                onContextMenu={(e) => e.preventDefault()}
                                className="w-100"
                                style={{ borderRadius: '12px', maxHeight: '300px' }}
                                preload="metadata"
                                playsInline
                                poster={undefined}
                              />
                            </div>
                            <div className="text-center mt-2">
                              <small className="text-muted">
                                <i className="fas fa-lock me-1"></i>
                                پخش آنلاین (دانلود غیر فعال است)
                              </small>
                            </div>
                          </div>
                        ) : (
                          <Alert variant="info" className="mb-0 text-center">
                            <i className="fas fa-exclamation-triangle me-2"></i>
                            لینک ویدیو در دسترس نیست
                          </Alert>
                        )}
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Container>

      <style>{`
        .workshop-video-card {
          transition: all 0.3s ease;
          border-radius: 12px;
        }

        .workshop-video-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
        }

        .session-number-badge {
          flex-shrink: 0;
        }

        .video-container {
          position: relative;
          background: #000;
          border-radius: 12px;
          overflow: hidden;
        }

        .video-container video {
          display: block;
          width: 100%;
          height: auto;
          max-height: 300px;
        }

        .video-container-wrapper {
          position: sticky;
          top: 20px;
        }

        @media (max-width: 991px) {
          .video-container-wrapper {
            position: static;
            margin-top: 20px;
          }
        }

        .breadcrumb {
          background-color: transparent;
          padding: 0;
        }

        .breadcrumb-item a {
          text-decoration: none;
          color: #6c757d;
          transition: color 0.2s ease;
        }

        .breadcrumb-item a:hover {
          color: #007bff;
        }

        .breadcrumb-item.active {
          color: #495057;
          font-weight: 500;
        }
      `}</style>
    </>
  );
};

export default WorkshopVideos;


