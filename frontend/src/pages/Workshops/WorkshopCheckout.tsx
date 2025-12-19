import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, ListGroup, Alert, Spinner, Form } from 'react-bootstrap';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

interface OrderDetails {
  id: number;
  order_number: string;
  subtotal: string;
  discount_amount: string;
  tax_amount: string;
  total_amount: string;
  payment_status: string;
  created_at: string;
  items: Array<{
    id: number;
    item_type: string;
    item_id: number;
    item_title: string;
    quantity: number;
    unit_price: string;
    total_price: string;
  }>;
  workshop_details?: {
    id: number;
    title: string;
    slug: string;
    price: string;
    thumbnail: string | null;
    instructor_name: string;
    payment_type: string;
  };
}

const WorkshopCheckout: React.FC = () => {
  const { orderNumber } = useParams<{ orderNumber: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [agreeToTerms, setAgreeToTerms] = useState(false);

  // Fetch order details
  const { data: order, isLoading, error } = useQuery<OrderDetails>({
    queryKey: ['workshop-order', orderNumber],
    queryFn: async () => {
      const response = await axios.get(`/api/workshops/orders/${orderNumber}/`);
      return response.data;
    },
    enabled: isAuthenticated && !!orderNumber,
  });

  // Process payment mutation
  const processPaymentMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/workshops/orders/${orderNumber}/payment/`);
      return response.data;
    },
    onSuccess: (data) => {
      if (data.success && data.payment_url) {
        // Redirect to payment gateway
        window.location.href = data.payment_url;
      } else {
        alert(data.error || 'خطا در ایجاد درخواست پرداخت');
      }
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در پردازش پرداخت');
    },
  });

  const formatPrice = (price: string | number) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('fa-IR').format(numPrice);
  };

  const handlePayment = () => {
    if (!agreeToTerms) {
      alert('لطفاً شرایط و قوانین را بپذیرید');
      return;
    }
    processPaymentMutation.mutate();
  };

  if (!isAuthenticated) {
    return (
      <Container className="py-5">
        <Alert variant="warning">
          برای مشاهده صفحه پرداخت ابتدا وارد حساب کاربری خود شوید.
        </Alert>
      </Container>
    );
  }

  if (isLoading) {
    return (
      <Container className="py-5">
        <div className="text-center">
          <Spinner animation="border" variant="primary" />
          <p className="mt-3">در حال بارگذاری اطلاعات سفارش...</p>
        </div>
      </Container>
    );
  }

  if (error || !order) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          <Alert.Heading>خطا در بارگذاری سفارش</Alert.Heading>
          <p>سفارش مورد نظر یافت نشد یا دسترسی به آن ممکن نیست.</p>
          <hr />
          <div className="d-flex justify-content-end">
            <Link to="/workshops">
              <Button variant="outline-danger">بازگشت به کارگاه‌ها</Button>
            </Link>
          </div>
        </Alert>
      </Container>
    );
  }

  if (order.payment_status === 'completed') {
    return (
      <Container className="py-5">
        <Alert variant="success">
          <Alert.Heading>پرداخت با موفقیت انجام شد!</Alert.Heading>
          <p>سفارش شما قبلاً پرداخت شده است.</p>
          <hr />
          <div className="d-flex justify-content-end">
            <Link to="/dashboard/my-workshops">
              <Button variant="success">مشاهده کارگاه‌های من</Button>
            </Link>
          </div>
        </Alert>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>تکمیل خرید کارگاه - پرداخت</title>
      </Helmet>

      <Container className="py-4">
        <Alert variant="light" className="border border-primary-subtle mb-4">
          <div className="d-flex align-items-start">
            <i className="fas fa-shopping-cart text-primary fa-lg me-3 mt-1"></i>
            <div>
              <h5 className="mb-1">مرور سبد خرید کارگاه</h5>
              <p className="mb-0 text-muted">
                لطفاً جزئیات کارگاه را بررسی کرده و پس از پذیرش شرایط، پرداخت را تکمیل کنید. پس از بازگشت از درگاه به صفحه تأیید پرداخت هدایت می‌شوید و می‌توانید کارگاه را در بخش «کارگاه‌های من» ببینید.
              </p>
            </div>
          </div>
        </Alert>

        <Row>
          <Col lg={8}>
            {/* Order Details */}
            <Card className="mb-4">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-shopping-cart me-2"></i>
                  جزئیات سفارش
                </h5>
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <small className="text-muted">شماره سفارش:</small>
                  <h6 className="mb-0">{order.order_number}</h6>
                </div>

                <ListGroup variant="flush">
                  {order.items.map((item) => (
                    <ListGroup.Item key={item.id} className="px-0">
                      <Row className="align-items-center">
                        <Col md={8}>
                          <div className="d-flex align-items-start">
                            {order.workshop_details?.thumbnail && (
                              <img
                                src={order.workshop_details.thumbnail}
                                alt={item.item_title}
                                className="rounded me-3"
                                style={{ width: '80px', height: '60px', objectFit: 'cover' }}
                                loading="lazy"
                                onError={(e) => {
                                  e.currentTarget.src = '/images/workshop-placeholder.jpg';
                                }}
                              />
                            )}
                            <div>
                              <h6 className="mb-1">{item.item_title}</h6>
                              {order.workshop_details && (
                                <>
                                  <small className="text-muted d-block">
                                    <i className="fas fa-user me-1"></i>
                                    {order.workshop_details.instructor_name}
                                  </small>
                                  <small className="text-muted d-block">
                                    <i className="fas fa-credit-card me-1"></i>
                                    {order.workshop_details.payment_type === 'full_payment' && 'پرداخت کامل'}
                                    {order.workshop_details.payment_type === 'installment' && 'پرداخت قسطی (قسط اول)'}
                                  </small>
                                </>
                              )}
                            </div>
                          </div>
                        </Col>
                        <Col md={4} className="text-end">
                          <div className="fw-bold">{formatPrice(item.total_price)} تومان</div>
                        </Col>
                      </Row>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Card.Body>
            </Card>

            {/* Payment Method */}
            <Card className="mb-4">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-credit-card me-2"></i>
                  روش پرداخت
                </h5>
              </Card.Header>
              <Card.Body>
                <div className="d-flex align-items-center">
                  <i className="fas fa-check-circle text-success me-3" style={{ fontSize: '1.5rem' }}></i>
                  <div>
                    <div className="fw-medium">زرین پال</div>
                    <small className="text-muted">پرداخت امن با کارت‌های بانکی</small>
                  </div>
                </div>
              </Card.Body>
            </Card>

            {/* Terms and Conditions */}
            <Card>
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-file-contract me-2"></i>
                  شرایط و قوانین
                </h5>
              </Card.Header>
              <Card.Body>
                <div className="mb-3" style={{ maxHeight: '200px', overflowY: 'auto', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '0.375rem' }}>
                  <p className="mb-2 small">
                    <strong>قوانین ثبت‌نام و بازپرداخت کارگاه‌ها:</strong>
                  </p>
                  <ul className="small mb-2">
                    <li>ثبت‌نام در کارگاه به منزله پذیرش کامل قوانین و مقررات است.</li>
                    <li>کارگاه‌های آنلاین: استرداد کامل تا ۷۲ ساعت قبل از شروع، استرداد ۵۰٪ تا ۲۴ ساعت قبل.</li>
                    <li>کارگاه‌های حضوری: استرداد کامل تا ۷ روز قبل از شروع، استرداد ۵۰٪ تا ۴۸ ساعت قبل.</li>
                    <li>در صورت پرداخت قسطی، عدم پرداخت به موقع اقساط منجر به تعلیق دسترسی می‌شود.</li>
                    <li>حضور در جلسات و دریافت گواهینامه مستلزم حداقل ۸۰٪ حضور در کارگاه است.</li>
                  </ul>
                  <p className="mb-0">
                    <Link to="/terms" target="_blank" className="btn btn-sm btn-outline-primary">
                      مطالعه کامل شرایط و قوانین
                    </Link>
                  </p>
                </div>
                <Form.Check
                  type="checkbox"
                  id="agree-terms"
                  checked={agreeToTerms}
                  onChange={(e) => setAgreeToTerms(e.target.checked)}
                  label={
                    <span>
                      با{' '}
                      <Link to="/terms" target="_blank" onClick={(e) => e.stopPropagation()}>
                        شرایط و قوانین
                      </Link>
                      {' '}موافقم و تمام موارد ذکر شده را مطالعه کرده‌ام
                    </span>
                  }
                  required
                />
              </Card.Body>
            </Card>
          </Col>

          {/* Order Summary */}
          <Col lg={4}>
            <Card className="sticky-top" style={{ top: '20px' }}>
              <Card.Header>
                <h5 className="mb-0">خلاصه سفارش</h5>
              </Card.Header>
              <Card.Body>
                <div className="d-flex justify-content-between mb-2">
                  <span>جمع:</span>
                  <span>{formatPrice(order.subtotal)} تومان</span>
                </div>

                {parseFloat(order.discount_amount) > 0 && (
                  <div className="d-flex justify-content-between mb-2 text-success">
                    <span>تخفیف:</span>
                    <span>-{formatPrice(order.discount_amount)} تومان</span>
                  </div>
                )}

                {parseFloat(order.tax_amount) > 0 && (
                  <div className="d-flex justify-content-between mb-2">
                    <span>مالیات:</span>
                    <span>{formatPrice(order.tax_amount)} تومان</span>
                  </div>
                )}

                <hr />

                <div className="d-flex justify-content-between mb-3 fs-5 fw-bold">
                  <span>مبلغ نهایی:</span>
                  <span className="text-primary">{formatPrice(order.total_amount)} تومان</span>
                </div>

                <div className="d-grid gap-2">
                  <Button
                    variant="success"
                    size="lg"
                    onClick={handlePayment}
                    disabled={!agreeToTerms || processPaymentMutation.isPending}
                  >
                    {processPaymentMutation.isPending ? (
                      <>
                        <Spinner animation="border" size="sm" className="me-2" />
                        در حال انتقال به درگاه...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-lock me-2"></i>
                        پرداخت امن
                      </>
                    )}
                  </Button>

                  <Link to={`/workshops/${order.workshop_details?.slug}`}>
                    <Button variant="outline-secondary" className="w-100">
                      <i className="fas fa-arrow-right me-2"></i>
                      بازگشت به کارگاه
                    </Button>
                  </Link>
                </div>

                <div className="text-center mt-3 pt-3 border-top">
                  <small className="text-muted">
                    <i className="fas fa-shield-alt text-success me-1"></i>
                    پرداخت امن با درگاه زرین‌پال
                  </small>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default WorkshopCheckout;
