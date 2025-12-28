import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, Alert, ListGroup } from 'react-bootstrap';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { getWalletBalance } from '../../services/walletApi';
import axios from 'axios';

const Checkout: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string>('zarinpal');
  const [useWallet, setUseWallet] = useState<boolean>(false);
  const [couponCode, setCouponCode] = useState<string>('');
  const [agreeToTerms, setAgreeToTerms] = useState<boolean>(false);
  const [couponMessage, setCouponMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [appliedDiscount, setAppliedDiscount] = useState<number>(0);

  // Fetch cart summary
  const { data: cart, refetch: refetchCart } = useQuery({
    queryKey: ['cart-summary'],
    queryFn: async () => {
      const response = await axios.get('/api/payment/cart/');
      return response.data;
    },
  });

  // Fetch wallet balance
  const { data: walletBalance } = useQuery({
    queryKey: ['wallet-balance'],
    queryFn: getWalletBalance,
    enabled: !!user,
  });

  // Apply coupon mutation
  const applyCouponMutation = useMutation({
    mutationFn: async (code: string) => {
      const response = await axios.post('/api/payment/apply-coupon/', { code });
      return response.data;
    },
    onSuccess: (data) => {
      setCouponMessage({ type: 'success', text: data.message || 'کد تخفیف با موفقیت اعمال شد' });
      setAppliedDiscount(data.discount || 0);
      refetchCart(); // Refresh cart to show updated totals
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.error || 'خطا در اعمال کد تخفیف';
      setCouponMessage({ type: 'error', text: errorMessage });
      setAppliedDiscount(0);
    },
  });

  // Process payment mutation
  const processPaymentMutation = useMutation({
    mutationFn: async (paymentData: any) => {
      const response = await axios.post('/api/payment/process/', paymentData);
      return response.data;
    },
    onSuccess: (data) => {
      if (data.success && data.free_order) {
        // Free order - redirect to success page
        navigate('/payment/success', { state: { freeOrder: true, orderId: data.order_id } });
      } else if (data.success && data.payment_url) {
        // Redirect to Zarinpal payment gateway
        window.location.href = data.payment_url;
      } else if (data.success) {
        navigate('/payment/success');
      } else {
        alert(data.error || 'خطا در پردازش پرداخت');
      }
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در پردازش پرداخت');
    },
  });

  const handlePayment = async () => {
    if (!agreeToTerms) {
      alert('لطفاً شرایط و قوانین را بپذیرید');
      return;
    }

    processPaymentMutation.mutate({
      payment_method: selectedPaymentMethod,
      coupon_code: couponCode,
      use_wallet: useWallet,
    });
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fa-IR').format(price);
  };

  if (!cart || cart.items.length === 0) {
    return (
      <Container className="py-5">
        <Alert variant="warning">
          سبد خرید شما خالی است. لطفاً ابتدا بسته آموزشی را انتخاب کنید.
        </Alert>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>تسویه حساب - پرداخت</title>
      </Helmet>

      <Container className="py-4">
        <Row>
          <Col lg={8}>
            {/* Payment Methods */}
            <Card className="mb-4">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-credit-card me-2"></i>
                  روش پرداخت
                </h5>
              </Card.Header>
              <Card.Body>
                <Form.Check
                  type="radio"
                  id="zarinpal"
                  name="paymentMethod"
                  checked={selectedPaymentMethod === 'zarinpal'}
                  onChange={() => setSelectedPaymentMethod('zarinpal')}
                  label={
                    <div className="d-flex align-items-center">
                      <i className="fas fa-credit-card me-3 text-primary"></i>
                      <div>
                        <div className="fw-medium">زرین پال</div>
                        <small className="text-muted">پرداخت امن با کارت‌های بانکی</small>
                      </div>
                    </div>
                  }
                />
                
                {/* Wallet Payment Option */}
                {walletBalance && parseFloat(walletBalance.balance) > 0 && (
                  <div className="mt-3 pt-3 border-top">
                    <Form.Check
                      type="checkbox"
                      id="use-wallet"
                      checked={useWallet}
                      onChange={(e) => setUseWallet(e.target.checked)}
                      label={
                        <div className="d-flex align-items-center justify-content-between w-100">
                          <div className="d-flex align-items-center">
                            <i className="fas fa-wallet me-3 text-warning"></i>
                            <div>
                              <div className="fw-medium">استفاده از کیف پول</div>
                              <small className="text-muted">
                                موجودی: {parseFloat(walletBalance.balance).toLocaleString('fa-IR')} تومان
                              </small>
                            </div>
                          </div>
                        </div>
                      }
                    />
                    {useWallet && (
                      <Alert variant="info" className="mt-2 mb-0 small">
                        {parseFloat(walletBalance.balance) >= (cart?.total || cart?.subtotal || 0) - (appliedDiscount || cart?.discount || 0) ? (
                          <span>مبلغ کامل از کیف پول شما کسر خواهد شد.</span>
                        ) : (
                          <span>
                            مبلغ {parseFloat(walletBalance.balance).toLocaleString('fa-IR')} تومان از کیف پول کسر شده و مابقی از طریق درگاه پرداخت خواهد شد.
                          </span>
                        )}
                      </Alert>
                    )}
                  </div>
                )}
              </Card.Body>
            </Card>

            {/* Coupon Code */}
            <Card className="mb-4">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-tag me-2"></i>
                  کد تخفیف
                </h5>
              </Card.Header>
              <Card.Body>
                {couponMessage && (
                  <Alert 
                    variant={couponMessage.type === 'success' ? 'success' : 'danger'}
                    dismissible
                    onClose={() => setCouponMessage(null)}
                    className="mb-3"
                  >
                    {couponMessage.text}
                  </Alert>
                )}
                <Form.Group>
                  <Form.Label>کد تخفیف دارید؟</Form.Label>
                  <div className="d-flex gap-2">
                    <Form.Control
                      type="text"
                      placeholder="کد تخفیف را وارد کنید"
                      value={couponCode}
                      onChange={(e) => {
                        setCouponCode(e.target.value.toUpperCase());
                        setCouponMessage(null); // Clear message when user types
                      }}
                    />
                    <Button
                      variant="outline-primary"
                      onClick={() => applyCouponMutation.mutate(couponCode)}
                      disabled={!couponCode || applyCouponMutation.isPending}
                    >
                      {applyCouponMutation.isPending ? (
                        <span className="spinner-border spinner-border-sm"></span>
                      ) : (
                        'اعمال'
                      )}
                    </Button>
                  </div>
                </Form.Group>
              </Card.Body>
            </Card>

            {/* Terms */}
            <Card>
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-file-contract me-2"></i>
                  شرایط و قوانین
                </h5>
              </Card.Header>
              <Card.Body>
                <div className="mb-3" style={{ maxHeight: '300px', overflowY: 'auto', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '0.375rem' }}>
                  <p className="mb-2">
                    <strong>با تشکر از اعتماد شما به مرکز مشاوره و خدمات روانشناختی سرمد.</strong>
                  </p>
                  <p className="mb-2 small">
                    این قوانین جهت شفافیت و ایجاد فهم مشترک در خصوص خرید دوره‌های آنلاین، کارگاه‌های حضوری و آنلاین، بسته‌های آموزشی و جلسات مشاوره تنظیم شده است. لطفاً قبل از هرگونه خرید یا ثبت‌نام، این قوانین را به دقت مطالعه فرمایید. هرگونه خرید یا ثبت‌نام به منزله پذیرش کامل این قوانین و مقررات است.
                  </p>
                  <p className="mb-2 small">
                    <strong>نکات مهم:</strong>
                  </p>
                  <ul className="small mb-2">
                    <li>بسته‌های آموزشی دیجیتال پس از فعال شدن لینک، غیر قابل استرداد هستند.</li>
                    <li>کارگاه‌های آنلاین: استرداد کامل تا ۷۲ ساعت قبل، استرداد ۵۰% تا ۲۴ ساعت قبل.</li>
                    <li>کارگاه‌های حضوری: استرداد کامل تا ۷ روز قبل، استرداد ۵۰% تا ۴۸ ساعت قبل.</li>
                    <li>جلسات مشاوره: استرداد کامل تا ۴۸ ساعت قبل از جلسه.</li>
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
            <Card>
              <Card.Header>
                <h5 className="mb-0">خلاصه سفارش</h5>
              </Card.Header>
              <Card.Body>
                <ListGroup variant="flush" className="mb-3">
                  {cart.items.map((item: any) => {
                    const itemTitle =
                      item.course?.title ||
                      item.package?.title ||
                      item.item_title ||
                      `آیتم شماره ${item.id}`;
                    const priceNumber =
                      item.total_price ??
                      item.course?.discount_price ??
                      item.course?.price ??
                      item.package?.current_price ??
                      item.package?.discount_price ??
                      item.package?.price ??
                      item.unit_price ??
                      0;

                    return (
                      <ListGroup.Item key={item.id} className="px-0 py-2">
                        <div className="d-flex justify-content-between">
                          <span className="small">
                            {item.item_type === 'package' ? (
                              <i className="fas fa-box me-2 text-muted"></i>
                            ) : (
                              <i className="fas fa-book me-2 text-muted"></i>
                            )}
                            {itemTitle}
                          </span>
                          <span className="small">
                            {formatPrice(priceNumber)} تومان
                          </span>
                        </div>
                      </ListGroup.Item>
                    );
                  })}
                </ListGroup>

                <div className="d-flex justify-content-between mb-2">
                  <span>جمع:</span>
                  <span>{formatPrice(cart.subtotal || cart.total)} تومان</span>
                </div>

                {(appliedDiscount > 0 || cart.discount > 0) && (
                  <div className="d-flex justify-content-between mb-2 text-success">
                    <span>تخفیف:</span>
                    <span>-{formatPrice(appliedDiscount || cart.discount || 0)} تومان</span>
                  </div>
                )}

                <hr />

                {useWallet && walletBalance && (
                  <div className="d-flex justify-content-between mb-2 text-warning">
                    <span>کسر از کیف پول:</span>
                    <span>
                      -{formatPrice(Math.min(parseFloat(walletBalance.balance), (cart.subtotal || cart.total) - (appliedDiscount || cart.discount || 0)))} تومان
                    </span>
                  </div>
                )}

                <div className="d-flex justify-content-between mb-3 fs-5 fw-bold">
                  <span>مبلغ نهایی:</span>
                  <span className="text-primary">
                    {formatPrice(
                      Math.max(0, (cart.subtotal || cart.total) - (appliedDiscount || cart.discount || 0) - (useWallet && walletBalance ? Math.min(parseFloat(walletBalance.balance), (cart.subtotal || cart.total) - (appliedDiscount || cart.discount || 0)) : 0))
                    )} تومان
                  </span>
                </div>

                <Button
                  variant="success"
                  size="lg"
                  className="w-100"
                  onClick={handlePayment}
                  disabled={!agreeToTerms || processPaymentMutation.isPending}
                >
                  {processPaymentMutation.isPending ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      در حال پردازش...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-lock me-2"></i>
                      پرداخت امن
                    </>
                  )}
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Checkout;
