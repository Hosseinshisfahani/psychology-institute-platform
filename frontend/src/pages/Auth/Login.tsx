import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';

const Login: React.FC = () => {
  const { t } = useI18n();
  const { login, sendOTP } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    phone_number: '',
    otp_code: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [requireOTP, setRequireOTP] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [sendingOTP, setSendingOTP] = useState(false);

  const from = location.state?.from?.pathname || '/';

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSendOTP = async () => {
    setError('');
    
    if (!formData.phone_number) {
      setError('لطفاً شماره تلفن خود را وارد کنید');
      return;
    }
    
    const phoneRegex = /^09\d{9}$/;
    if (!phoneRegex.test(formData.phone_number.replace(/\s/g, ''))) {
      setError('فرمت شماره تلفن صحیح نیست. مثال: 09123456789');
      return;
    }
    
    setSendingOTP(true);
    try {
      await sendOTP(formData.phone_number, 'login');
      setOtpSent(true);
    } catch (err: any) {
      setError(err.message || 'خطا در ارسال کد تایید');
    } finally {
      setSendingOTP(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(
        formData.email, 
        formData.password,
        requireOTP ? formData.otp_code : undefined,
        requireOTP ? formData.phone_number : undefined
      );
      navigate(from, { replace: true });
    } catch (err: any) {
      const errorMessage = err.message || 'خطا در ورود';
      setError(errorMessage);
      
      // If error indicates OTP is required, show OTP section
      if (errorMessage.includes('OTP') || errorMessage.includes('otp')) {
        setRequireOTP(true);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Helmet>
        <title>{t('auth.login.title')} - {t('home.title')}</title>
      </Helmet>

      <Container className="py-5">
        <Row className="justify-content-center">
          <Col md={6} lg={4}>
            <Card className="shadow">
              <Card.Body className="p-4">
                <div className="text-center mb-4">
                  <img 
                    src="/images/1744027219152.png" 
                    alt={t('home.title')} 
                    height="60" 
                    className="mb-3"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                  <h4 className="mb-0">{t('auth.login.title')}</h4>
                </div>

                {error && (
                  <Alert variant="danger" className="mb-3">
                    {error}
                  </Alert>
                )}

                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label>{t('auth.login.email')}</Form.Label>
                    <Form.Control
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      placeholder="example@email.com"
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label>{t('auth.login.password')}</Form.Label>
                    <Form.Control
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      placeholder="••••••••"
                    />
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      label="ورود با کد تایید (اختیاری)"
                      checked={requireOTP}
                      onChange={(e) => {
                        setRequireOTP(e.target.checked);
                        if (!e.target.checked) {
                          setOtpSent(false);
                          setFormData(prev => ({ ...prev, phone_number: '', otp_code: '' }));
                        }
                      }}
                    />
                  </Form.Group>

                  {requireOTP && (
                    <>
                      <Form.Group className="mb-3">
                        <Form.Label>شماره تلفن</Form.Label>
                        <div className="d-flex gap-2">
                          <Form.Control
                            type="tel"
                            name="phone_number"
                            value={formData.phone_number}
                            onChange={handleChange}
                            required={requireOTP}
                            placeholder="09123456789"
                            maxLength={11}
                            disabled={otpSent || sendingOTP}
                          />
                          {!otpSent && (
                            <Button
                              variant="outline-primary"
                              onClick={handleSendOTP}
                              disabled={sendingOTP || !formData.phone_number}
                            >
                              {sendingOTP ? '...' : 'ارسال کد'}
                            </Button>
                          )}
                        </div>
                      </Form.Group>

                      {otpSent && (
                        <Form.Group className="mb-3">
                          <Form.Label>کد تایید</Form.Label>
                          <Form.Control
                            type="text"
                            name="otp_code"
                            value={formData.otp_code}
                            onChange={handleChange}
                            required={requireOTP}
                            placeholder="کد 6 رقمی"
                            maxLength={6}
                            className="text-center"
                            style={{ fontSize: '1.5rem', letterSpacing: '0.5rem' }}
                          />
                          <Form.Text className="text-muted">
                            کد تایید ارسال شده را وارد کنید
                          </Form.Text>
                        </Form.Group>
                      )}
                    </>
                  )}

                  <div className="d-grid mb-3">
                    <Button 
                      type="submit" 
                      variant="primary" 
                      size="lg"
                      disabled={isLoading || (requireOTP && !otpSent && !formData.otp_code)}
                    >
                      {isLoading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          {t('common.loading')}
                        </>
                      ) : (
                        t('auth.login.submit')
                      )}
                    </Button>
                  </div>

                  <div className="text-center">
                    <Link to="/forgot-password" className="text-decoration-none">
                      {t('auth.login.forgot_password')}
                    </Link>
                  </div>
                </Form>

                <hr className="my-4" />

                <div className="text-center">
                  <p className="mb-0 text-muted">
                    {t('auth.login.no_account')}
                  </p>
                  <Link to="/signup" className="btn btn-outline-primary mt-2">
                    {t('auth.login.signup_link')}
                  </Link>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Login;
