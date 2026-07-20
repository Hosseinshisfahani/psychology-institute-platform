import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Badge, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

interface Appointment {
  id: number;
  client_name: string;
  therapist_name: string;
  appointment_type_name: string;
  location_name: string;
  scheduled_datetime: string;
  duration_minutes: number;
  status: string;
  status_display: string;
  notes?: string;
  created_at: string;
}

const AppointmentsList: React.FC = () => {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const queryClient = useQueryClient();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Check for success message from appointment booking
  useEffect(() => {
    const successData = localStorage.getItem('appointmentSuccess');
    if (successData) {
      const { message } = JSON.parse(successData);
      setSuccessMessage(message);
      // Clear the message from localStorage after showing it
      localStorage.removeItem('appointmentSuccess');
    }
  }, []);

  const { data: appointments = [], isLoading, error } = useQuery<Appointment[]>({
    queryKey: ['appointments'],
    queryFn: async () => {
      const response = await axios.get('/api/appointments/');
      return response.data.results || response.data;
    },
    enabled: isAuthenticated && !!user,
  });

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'pending_deposit':
        return 'warning';
      case 'scheduled':
        return 'primary';
      case 'confirmed':
        return 'success';
      case 'completed':
        return 'info';
      case 'cancelled':
        return 'danger';
      case 'no_show':
        return 'warning';
      case 'rescheduled':
        return 'secondary';
      default:
        return 'light';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('fa-IR', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  };

  const handleChangeTime = (appointmentId: number) => {
    // Navigate to appointment booking page with the appointment ID for rescheduling
    window.location.href = `/appointment/booking?reschedule=${appointmentId}`;
  };

  const handleCancelAppointment = async (appointmentId: number) => {
    const initialConfirm = window.confirm('آیا مطمئن هستید که می‌خواهید این نوبت را لغو کنید؟');
    if (!initialConfirm) {
      return;
    }

    try {
      let response = await axios.post(`/api/appointments/${appointmentId}/cancel/`, {
        reason: ''
      });

      if (response.data?.requires_confirmation) {
        const warningMessage =
          response.data.warning ||
          'در صورت کنسل کردن نوبت در این بازه زمانی، ودیعه شما بازگردانده نخواهد شد. آیا از لغو نوبت اطمینان دارید؟';
        const proceed = window.confirm(warningMessage);
        if (!proceed) {
          return;
        }

        response = await axios.post(`/api/appointments/${appointmentId}/cancel/`, {
          confirm: true,
          reason: ''
        });
      }

      if (response.data?.warning) {
        alert(response.data.warning);
      }

      alert(response.data?.message || 'نوبت با موفقیت لغو شد');
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
    } catch (error) {
      console.error('Error cancelling appointment:', error);
      alert('خطا در لغو نوبت. لطفاً دوباره تلاش کنید.');
    }
  };

  // Show loading while checking auth
  if (authLoading) {
    return (
      <Container className="py-5">
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
            <span className="visually-hidden">در حال بارگذاری...</span>
          </div>
          <p className="text-muted mt-3">در حال بررسی وضعیت ورود...</p>
        </div>
      </Container>
    );
  }

  // Show login required if not authenticated
  if (!isAuthenticated || !user) {
    return (
      <Container className="py-5">
        <Alert variant="warning" className="text-center">
          <Alert.Heading>ورود الزامی است</Alert.Heading>
          <p>برای مشاهده نوبت‌های خود، ابتدا باید وارد حساب کاربری خود شوید.</p>
          <Button variant="primary" href="/login">
            ورود به حساب کاربری
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>نوبت‌های من - موسسه روانشناسی</title>
        <meta name="description" content="مشاهده و مدیریت نوبت‌های رزرو شده" />
      </Helmet>

      <Container className="py-5">
        <div className="d-flex justify-content-between align-items-center mb-5">
          <div>
            <h1 className="display-5 fw-bold mb-2">نوبت‌های من</h1>
            <p className="text-muted">مشاهده و مدیریت نوبت‌های رزرو شده</p>
          </div>
          <div className="d-flex flex-wrap justify-content-end gap-2">
            <Link to="/">
              <Button variant="outline-secondary" size="lg">
                <i className="fas fa-home me-2"></i>
                بازگشت به خانه
              </Button>
            </Link>
            <Link to="/dashboard">
              <Button variant="outline-primary" size="lg">
                <i className="fas fa-th-large me-2"></i>
                داشبورد
              </Button>
            </Link>
            <Link to="/appointment/booking">
              <Button variant="primary" size="lg">
                <i className="fas fa-plus me-2"></i>
                رزرو نوبت جدید
              </Button>
            </Link>
          </div>
        </div>

        {/* Success Banner */}
        {successMessage && (
          <Alert variant="success" className="mb-4" dismissible onClose={() => setSuccessMessage(null)}>
            <Alert.Heading className="h5">
              <i className="fas fa-check-circle me-2"></i>
              {successMessage}
            </Alert.Heading>
            <p className="mb-0">
              برای مدیریت نوبت های خود میتوانید از این صفحه استفاده کنید.
            </p>
          </Alert>
        )}

        {isLoading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
              <span className="visually-hidden">در حال بارگذاری...</span>
            </div>
            <p className="text-muted mt-3">در حال بارگذاری نوبت‌ها...</p>
          </div>
        ) : error ? (
          <Alert variant="danger">
            <Alert.Heading>خطا در بارگذاری</Alert.Heading>
            <p>متأسفانه خطایی در بارگذاری نوبت‌ها رخ داده است. لطفاً دوباره تلاش کنید.</p>
          </Alert>
        ) : appointments.length === 0 ? (
          <Card className="text-center" style={{ borderRadius: '20px', border: 'none', background: '#f8f9fa' }}>
            <Card.Body className="py-5">
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
                <i className="fas fa-calendar-times" style={{ fontSize: '3.5rem', color: '#6c757d' }}></i>
              </div>
              <h5 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem', color: '#495057' }}>
                هیچ نوبتی رزرو نشده
              </h5>
              <p className="text-muted" style={{ fontSize: '1.05rem', maxWidth: '500px', margin: '0 auto 2rem' }}>
                هنوز هیچ نوبتی رزرو نکرده‌اید. برای شروع، نوبت جدیدی رزرو کنید.
              </p>
              <Link to="/appointment/booking">
                <Button variant="primary" size="lg">
                  <i className="fas fa-calendar-plus me-2"></i>
                  رزرو نوبت جدید
                </Button>
              </Link>
            </Card.Body>
          </Card>
        ) : (
          <Row className="g-4">
            {appointments.map((appointment) => (
              <Col key={appointment.id} lg={6}>
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
                    e.currentTarget.style.transform = 'translateY(-8px)';
                    e.currentTarget.style.boxShadow = '0 15px 40px rgba(0,0,0,0.12)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 5px 15px rgba(0,0,0,0.08)';
                  }}
                >
                  <Card.Body className="p-4">
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <h6 className="mb-0" style={{ fontSize: '1.1rem', fontWeight: 600 }}>
                        {appointment.appointment_type_name}
                      </h6>
                      <Badge 
                        bg={getStatusVariant(appointment.status)}
                        style={{ fontSize: '0.8rem', padding: '0.5rem 0.75rem' }}
                      >
                        {appointment.status_display}
                      </Badge>
                    </div>

                    <div className="mb-3">
                      <div className="d-flex align-items-center mb-2">
                        <i className="fas fa-user-md text-primary me-2" style={{ width: '18px' }}></i>
                        <span style={{ fontSize: '0.95rem' }}>{appointment.therapist_name}</span>
                      </div>
                      <div className="d-flex align-items-center mb-2">
                        <i className="fas fa-map-marker-alt text-primary me-2" style={{ width: '18px' }}></i>
                        <span style={{ fontSize: '0.95rem' }}>{appointment.location_name}</span>
                      </div>
                      <div className="d-flex align-items-center mb-2">
                        <i className="fas fa-calendar text-primary me-2" style={{ width: '18px' }}></i>
                        <span style={{ fontSize: '0.95rem' }}>{formatDate(appointment.scheduled_datetime)}</span>
                      </div>
                      <div className="d-flex align-items-center mb-2">
                        <i className="fas fa-clock text-primary me-2" style={{ width: '18px' }}></i>
                        <span style={{ fontSize: '0.95rem' }}>
                          {formatTime(appointment.scheduled_datetime)} ({appointment.duration_minutes} دقیقه)
                        </span>
                      </div>
                    </div>

                    {appointment.notes && (
                      <div className="mb-3">
                        <small className="text-muted">
                          <i className="fas fa-sticky-note me-1"></i>
                          {appointment.notes}
                        </small>
                      </div>
                    )}

                    <div className="d-flex gap-2">
                      {appointment.status === 'scheduled' && (
                        <>
                          <Button 
                            variant="outline-primary" 
                            size="sm"
                            onClick={() => handleChangeTime(appointment.id)}
                          >
                            <i className="fas fa-edit me-1"></i>
                            تغییر زمان
                          </Button>
                          <Button 
                            variant="outline-danger" 
                            size="sm"
                            onClick={() => handleCancelAppointment(appointment.id)}
                          >
                            <i className="fas fa-times me-1"></i>
                            لغو نوبت
                          </Button>
                        </>
                      )}
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </Container>
    </>
  );
};

export default AppointmentsList;
