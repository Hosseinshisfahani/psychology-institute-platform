import React, { useMemo } from 'react';
import { Container, Row, Col, Card, Button, Alert } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

const PaymentCancel: React.FC = () => {
  const location = useLocation();

  const { errorMessage } = useMemo(() => {
    const params = new URLSearchParams(location.search);

    return {
      errorMessage: params.get('error') ?? 'پرداخت شما تکمیل نشد. لطفاً بعداً دوباره تلاش کنید.',
    };
  }, [location.search]);

  return (
    <>
      <Helmet>
        <title>پرداخت لغو شد - خطا در پرداخت</title>
        <meta name="robots" content="noindex" />
      </Helmet>

      <Container className="py-5">
        <Row className="justify-content-center">
          <Col lg={8} xl={7}>
            <Card className="shadow-sm border-0">
              <Card.Body className="p-4 p-lg-5">
                <div className="text-center mb-4">
                  <div
                    className="d-inline-flex align-items-center justify-content-center rounded-circle bg-danger bg-opacity-10 text-danger mb-3"
                    style={{ width: '90px', height: '90px' }}
                  >
                    <i className="fas fa-times fa-3x"></i>
                  </div>
                  <h2 className="fw-bold mb-2">پرداخت با مشکل مواجه شد</h2>
                  <p className="text-muted mb-0">
                    متأسفانه تراکنش شما تکمیل نشد. لطفاً پیام زیر را بررسی کرده و در صورت نیاز دوباره اقدام کنید.
                  </p>
                </div>

                <Alert variant="danger" className="mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-exclamation-triangle fa-lg me-3"></i>
                    <div className="text-start">{errorMessage}</div>
                  </div>
                </Alert>

                <div className="d-grid gap-3">
                  <Link to="/payment/checkout" className="text-decoration-none">
                    <Button variant="primary" size="lg" className="w-100">
                      <i className="fas fa-redo me-2"></i>
                      تلاش مجدد برای پرداخت
                    </Button>
                  </Link>

                  <Link to="/dashboard" className="text-decoration-none">
                    <Button variant="outline-secondary" size="lg" className="w-100">
                      <i className="fas fa-th-large me-2"></i>
                      بازگشت به پیشخوان کاربری
                    </Button>
                  </Link>
                </div>
              </Card.Body>
            </Card>

            <div className="text-center text-muted small mt-4">
              <p className="mb-1">
                در صورت تکرار خطا، با شماره <a href="tel:+983137239797">031-37239797</a> تماس بگیرید یا برای ما ایمیل
                ارسال کنید.
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

export default PaymentCancel;


