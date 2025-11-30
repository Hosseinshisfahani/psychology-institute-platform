import React, { useMemo, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert, ListGroup } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';

const PaymentSuccess: React.FC = () => {
  const location = useLocation();
  const { checkAuthStatus } = useAuth();

  // Refresh auth state on mount to ensure user is authenticated after payment redirect
  useEffect(() => {
    // Refresh auth status to ensure user state is up to date after payment redirect
    checkAuthStatus();
  }, [checkAuthStatus]);

  const { orderId, refId, appointmentId } = useMemo(() => {
    const params = new URLSearchParams(location.search);

    return {
      orderId: params.get('order_id'),
      refId: params.get('ref_id'),
      appointmentId: params.get('appointment_id'),
    };
  }, [location.search]);

  return (
    <>
      <Helmet>
        <title>پرداخت موفق - تشکر از شما</title>
        <meta name="robots" content="noindex" />
      </Helmet>

      <Container className="py-5">
        <Row className="justify-content-center">
          <Col lg={8} xl={7}>
            <Card className="shadow-sm border-0">
              <Card.Body className="p-4 p-lg-5">
                <div className="text-center mb-4">
                  <div
                    className="d-inline-flex align-items-center justify-content-center rounded-circle bg-success bg-opacity-10 text-success mb-3"
                    style={{ width: '90px', height: '90px' }}
                  >
                    <i className="fas fa-check fa-3x"></i>
                  </div>
                  <h2 className="fw-bold mb-2">پرداخت شما با موفقیت انجام شد</h2>
                  <p className="text-muted mb-0">
                    ضمن سپاس از اعتمادتان، رسید پرداخت شما ثبت و برای بررسی‌های بعدی ذخیره شد.
                  </p>
                </div>

                <Alert variant="info" className="mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-info-circle fa-lg me-3"></i>
                    <div className="text-start">
                      لطفاً رسید پرداخت را نزد خود نگه دارید. در صورت بروز هرگونه مشکل می‌توانید با واحد پشتیبانی تماس بگیرید.
                    </div>
                  </div>
                </Alert>

                {appointmentId && (
                  <Alert variant="success" className="mb-4">
                    <div className="d-flex align-items-center">
                      <i className="fas fa-calendar-check fa-lg me-3"></i>
                      <div className="text-start">
                        ودیعه نوبت شما با موفقیت پرداخت شد. می‌توانید جزئیات نوبت را در بخش «نوبت‌های من» مشاهده و مدیریت کنید.
                      </div>
                    </div>
                  </Alert>
                )}

                {(orderId || refId) && (
                  <Card className="border-0 bg-light mb-4">
                    <Card.Body className="p-3 p-lg-4">
                      <h5 className="fw-semibold mb-3">جزئیات تراکنش</h5>
                      <ListGroup variant="flush" className="small">
                        {orderId && (
                          <ListGroup.Item className="d-flex justify-content-between px-0">
                            <span className="text-muted">شماره سفارش:</span>
                            <span className="fw-semibold">{orderId}</span>
                          </ListGroup.Item>
                        )}
                        {refId && (
                          <ListGroup.Item className="d-flex justify-content-between px-0">
                            <span className="text-muted">شناسه پیگیری (بانک):</span>
                            <span className="fw-semibold">{refId}</span>
                          </ListGroup.Item>
                        )}
                        {appointmentId && (
                          <ListGroup.Item className="d-flex justify-content-between px-0">
                            <span className="text-muted">شناسه نوبت:</span>
                            <span className="fw-semibold">{appointmentId}</span>
                          </ListGroup.Item>
                        )}
                      </ListGroup>
                    </Card.Body>
                  </Card>
                )}

                <div className="d-grid gap-3">
                  {appointmentId && (
                    <Link to="/appointments" className="text-decoration-none">
                      <Button variant="success" size="lg" className="w-100">
                        <i className="fas fa-calendar-day me-2"></i>
                        مشاهده نوبت‌های من
                      </Button>
                    </Link>
                  )}

                  <Link to="/courses" className="text-decoration-none">
                    <Button variant="primary" size="lg" className="w-100">
                      <i className="fas fa-graduation-cap me-2"></i>
                      مشاهده دوره‌های در دسترس
                    </Button>
                  </Link>

                  <Link to="/dashboard" className="text-decoration-none">
                    <Button variant="outline-primary" size="lg" className="w-100">
                      <i className="fas fa-th-large me-2"></i>
                      رفتن به پیشخوان کاربری
                    </Button>
                  </Link>
                </div>
              </Card.Body>
            </Card>

            <div className="text-center text-muted small mt-4">
              <p className="mb-1">
                در صورت نیاز به راهنمایی بیشتر، با شماره <a href="tel:+983137239797">031-37239797</a> تماس بگیرید یا برای ما ایمیل بفرستید.
              </p>
              <p className="mb-0">
                آدرس ایمیل پشتیبانی: <a href="mailto:info@sarmadclinic.ir">info@sarmadclinic.ir</a>
              </p>
            </div>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default PaymentSuccess;

