import React from 'react';
import { Container, Row, Col, Card, Button, Alert, ListGroup, Badge, Spinner } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

interface SessionData {
  session: {
    id: number;
    session_number: number;
    title: string;
    description: string;
    scheduled_datetime_persian: string;
    duration_minutes: number;
    is_completed: boolean;
  };
  meeting_link: string | null;
  recording_url: string | null;
  can_join: boolean;
  attendance: {
    attended: boolean;
    join_time: string | null;
    leave_time: string | null;
  };
}

const WorkshopSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const queryClient = useQueryClient();

  const { data: sessionData, isLoading, error } = useQuery<SessionData>({
    queryKey: ['workshop-session', sessionId],
    queryFn: async () => {
      const response = await axios.get(`/api/workshops/sessions/${sessionId}/access/`);
      return response.data;
    },
  });

  const markAttendanceMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/workshops/sessions/${sessionId}/attendance/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workshop-session', sessionId] });
      alert('حضور شما ثبت شد');
    },
  });

  if (isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3 text-muted">در حال بارگذاری...</p>
      </Container>
    );
  }

  if (error || !sessionData) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          <i className="fas fa-exclamation-triangle ms-2"></i>
          {(error as any)?.response?.data?.error || 'خطا در بارگذاری اطلاعات جلسه'}
        </Alert>
      </Container>
    );
  }

  const { session, meeting_link, recording_url, can_join, attendance } = sessionData;

  return (
    <>
      <Helmet>
        <title>{session.title} - جلسه کارگاه</title>
      </Helmet>

      <Container className="py-5">
        <Row className="justify-content-center">
          <Col lg={10}>
            {/* Session Header */}
            <Card className="mb-4">
              <Card.Body>
                <Badge bg="primary" className="mb-3">
                  جلسه {session.session_number}
                </Badge>
                <h2 className="mb-3">{session.title}</h2>
                {session.description && (
                  <p className="text-muted">{session.description}</p>
                )}

                <ListGroup horizontal className="mb-0">
                  <ListGroup.Item>
                    <i className="fas fa-calendar ms-2 text-primary"></i>
                    {session.scheduled_datetime_persian}
                  </ListGroup.Item>
                  <ListGroup.Item>
                    <i className="fas fa-clock ms-2 text-primary"></i>
                    {session.duration_minutes} دقیقه
                  </ListGroup.Item>
                  <ListGroup.Item>
                    <i className="fas fa-check-circle ms-2 text-success"></i>
                    {attendance.attended ? 'حضور ثبت شده' : 'حضور ثبت نشده'}
                  </ListGroup.Item>
                </ListGroup>
              </Card.Body>
            </Card>

            {/* Live Session */}
            {can_join && meeting_link && !session.is_completed && (
              <Card className="mb-4 border-primary">
                <Card.Header className="bg-primary text-white">
                  <h5 className="mb-0">
                    <i className="fas fa-video ms-2"></i>
                    جلسه زنده
                  </h5>
                </Card.Header>
                <Card.Body>
                  <Alert variant="info" className="mb-4">
                    <i className="fas fa-info-circle ms-2"></i>
                    جلسه آماده پیوستن است. با کلیک روی دکمه زیر وارد کلاس آنلاین شوید.
                  </Alert>

                  <div className="d-grid gap-2">
                    <Button
                      variant="success"
                      size="lg"
                      href={meeting_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={() => markAttendanceMutation.mutate()}
                    >
                      <i className="fas fa-video ms-2"></i>
                      ورود به کلاس آنلاین
                    </Button>
                  </div>

                  <div className="mt-3 text-center text-muted small">
                    لینک در پنجره جدید باز می‌شود
                  </div>
                </Card.Body>
              </Card>
            )}

            {/* Recording */}
            {recording_url && (
              <Card className="mb-4">
                <Card.Header>
                  <h5 className="mb-0">
                    <i className="fas fa-film ms-2"></i>
                    ضبط جلسه
                  </h5>
                </Card.Header>
                <Card.Body>
                  <Alert variant="success" className="mb-4">
                    <i className="fas fa-check-circle ms-2"></i>
                    ضبط این جلسه آماده مشاهده است
                  </Alert>

                  <div className="ratio ratio-16x9 mb-3">
                    <video
                      controls
                      controlsList="nodownload"
                      onContextMenu={(e) => e.preventDefault()}
                      style={{ backgroundColor: '#000' }}
                    >
                      <source src={recording_url} type="video/mp4" />
                      مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند
                    </video>
                  </div>

                  <Alert variant="warning" className="mb-0">
                    <i className="fas fa-exclamation-triangle ms-2"></i>
                    دانلود ویدیو امکان‌پذیر نیست. فقط قابل مشاهده آنلاین است.
                  </Alert>
                </Card.Body>
              </Card>
            )}

            {/* Waiting State */}
            {!can_join && !recording_url && !session.is_completed && (
              <Card className="text-center py-5">
                <Card.Body>
                  <i className="fas fa-clock text-muted mb-3" style={{ fontSize: '3rem' }}></i>
                  <h4>جلسه هنوز شروع نشده است</h4>
                  <p className="text-muted mb-4">
                    این جلسه در تاریخ {session.scheduled_datetime_persian} برگزار خواهد شد.
                    <br />
                    15 دقیقه قبل از شروع جلسه می‌توانید وارد شوید.
                  </p>
                  <Button variant="primary" onClick={() => window.location.reload()}>
                    <i className="fas fa-sync-alt ms-2"></i>
                    بروزرسانی صفحه
                  </Button>
                </Card.Body>
              </Card>
            )}

            {/* Attendance Info */}
            {attendance.attended && (
              <Card>
                <Card.Header>
                  <h5 className="mb-0">
                    <i className="fas fa-check-circle ms-2"></i>
                    اطلاعات حضور
                  </h5>
                </Card.Header>
                <Card.Body>
                  <ListGroup variant="flush">
                    {attendance.join_time && (
                      <ListGroup.Item className="d-flex justify-content-between">
                        <span>زمان ورود</span>
                        <strong>{new Date(attendance.join_time).toLocaleString('fa-IR')}</strong>
                      </ListGroup.Item>
                    )}
                    {attendance.leave_time && (
                      <ListGroup.Item className="d-flex justify-content-between">
                        <span>زمان خروج</span>
                        <strong>{new Date(attendance.leave_time).toLocaleString('fa-IR')}</strong>
                      </ListGroup.Item>
                    )}
                  </ListGroup>
                </Card.Body>
              </Card>
            )}
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default WorkshopSession;

