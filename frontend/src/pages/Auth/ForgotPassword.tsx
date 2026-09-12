import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';

const ForgotPassword: React.FC = () => {
  const { t } = useI18n();
  const { sendOTP, resetPassword } = useAuth();
  const navigate = useNavigate();

  const [method, setMethod] = useState<'phone' | 'email'>('phone');
  const [formData, setFormData] = useState({
    email: '',
    phone_number: '',
    otp_code: '',
    password1: '',
    password2: '',
  });
  const [error, setError] = useState('');
  const [phoneHint, setPhoneHint] = useState('');
  const [step, setStep] = useState<'identifier' | 'reset' | 'done'>('identifier');
  const [sendingOTP, setSendingOTP] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSendOTP = async () => {
    setError('');

    if (method === 'phone') {
      if (!formData.phone_number) {
        setError('لطفاً شماره تلفن خود را وارد کنید');
        return;
      }

      const phoneRegex = /^09\d{9}$/;
      const normalizedPhone = formData.phone_number.replace(/\s/g, '');
      if (!phoneRegex.test(normalizedPhone)) {
        setError('فرمت شماره تلفن صحیح نیست. مثال: 09123456789');
        return;
      }
    } else if (!formData.email) {
      setError('لطفاً ایمیل خود را وارد کنید');
      return;
    }

    setSendingOTP(true);
    try {
      const result = await sendOTP(
        method === 'phone' ? formData.phone_number.replace(/\s/g, '') : '',
        'password_reset',
        method === 'email' ? formData.email.trim() : undefined
      );
      setPhoneHint(result?.phone_hint || (method === 'phone' ? formData.phone_number : ''));
      setStep('reset');
    } catch (err: any) {
      setError(err.message || 'خطا در ارسال کد تایید');
    } finally {
      setSendingOTP(false);
    }
  };

  const handleReset = async () => {
    setError('');

    if (!formData.otp_code || (formData.otp_code.length !== 4 && formData.otp_code.length !== 6)) {
      setError('لطفاً کد تایید را وارد کنید (4 یا 6 رقمی)');
      return;
    }

    if (formData.password1.length < 8) {
      setError('رمز عبور باید حداقل 8 کاراکتر باشد');
      return;
    }

    if (formData.password1 !== formData.password2) {
      setError('رمزهای عبور مطابقت ندارند');
      return;
    }

    setIsLoading(true);
    try {
      await resetPassword(
        method === 'phone'
          ? { phoneNumber: formData.phone_number.replace(/\s/g, '') }
          : { email: formData.email.trim() },
        formData.otp_code,
        formData.password1,
        formData.password2
      );
      setStep('done');
    } catch (err: any) {
      setError(err.message || 'خطا در بازیابی رمز عبور');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (step === 'identifier') {
      await handleSendOTP();
    } else if (step === 'reset') {
      await handleReset();
    }
  };

  return (
    <>
      <Helmet>
        <title>{t('auth.forgot.title')} - {t('home.title')}</title>
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
                    loading="lazy"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                  <h4 className="mb-2">{t('auth.forgot.title')}</h4>
                  {step !== 'done' && (
                    <p className="text-muted mb-0">{t('auth.forgot.subtitle')}</p>
                  )}
                </div>

                {error && (
                  <Alert variant="danger" className="mb-3">
                    {error}
                  </Alert>
                )}

                {step === 'done' ? (
                  <>
                    <Alert variant="success" className="mb-4">
                      {t('auth.forgot.success')}
                    </Alert>
                    <div className="d-grid">
                      <Button variant="primary" size="lg" onClick={() => navigate('/login')}>
                        {t('auth.forgot.back_to_login')}
                      </Button>
                    </div>
                  </>
                ) : (
                  <Form onSubmit={handleSubmit}>
                    {step === 'identifier' && (
                      <>
                        <Form.Group className="mb-3">
                          <Form.Label>روش بازیابی</Form.Label>
                          <div className="btn-group w-100" role="group">
                            <input
                              type="radio"
                              className="btn-check"
                              name="resetMethod"
                              id="resetPhone"
                              checked={method === 'phone'}
                              onChange={() => {
                                setMethod('phone');
                                setError('');
                              }}
                            />
                            <label className="btn btn-outline-primary" htmlFor="resetPhone">
                              <i className="fas fa-phone me-2"></i>
                              {t('auth.forgot.phone')}
                            </label>

                            <input
                              type="radio"
                              className="btn-check"
                              name="resetMethod"
                              id="resetEmail"
                              checked={method === 'email'}
                              onChange={() => {
                                setMethod('email');
                                setError('');
                              }}
                            />
                            <label className="btn btn-outline-primary" htmlFor="resetEmail">
                              <i className="fas fa-envelope me-2"></i>
                              {t('auth.forgot.email')}
                            </label>
                          </div>
                        </Form.Group>

                        {method === 'phone' ? (
                          <Form.Group className="mb-3">
                            <Form.Label>{t('auth.forgot.phone')}</Form.Label>
                            <Form.Control
                              type="tel"
                              name="phone_number"
                              value={formData.phone_number}
                              onChange={handleChange}
                              required
                              placeholder="09123456789"
                              maxLength={11}
                              autoComplete="tel"
                              disabled={sendingOTP}
                            />
                          </Form.Group>
                        ) : (
                          <Form.Group className="mb-3">
                            <Form.Label>{t('auth.forgot.email')}</Form.Label>
                            <Form.Control
                              type="email"
                              name="email"
                              value={formData.email}
                              onChange={handleChange}
                              required
                              placeholder="example@email.com"
                              autoComplete="email"
                              disabled={sendingOTP}
                            />
                          </Form.Group>
                        )}

                        <div className="d-grid mb-3">
                          <Button type="submit" variant="primary" size="lg" disabled={sendingOTP}>
                            {sendingOTP ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                {t('common.loading')}
                              </>
                            ) : (
                              t('auth.forgot.send_code')
                            )}
                          </Button>
                        </div>
                      </>
                    )}

                    {step === 'reset' && (
                      <>
                        <Alert variant="info" className="mb-3">
                          کد تایید به شماره {phoneHint || formData.phone_number} ارسال شد.
                        </Alert>

                        <Form.Group className="mb-3">
                          <Form.Label>{t('auth.forgot.otp')}</Form.Label>
                          <Form.Control
                            type="text"
                            name="otp_code"
                            value={formData.otp_code}
                            onChange={handleChange}
                            required
                            placeholder={t('auth.forgot.otp')}
                            maxLength={6}
                            className="text-center"
                            style={{ fontSize: '1.5rem', letterSpacing: '0.5rem' }}
                            autoComplete="one-time-code"
                            disabled={isLoading}
                          />
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>{t('auth.forgot.new_password')}</Form.Label>
                          <Form.Control
                            type="password"
                            name="password1"
                            value={formData.password1}
                            onChange={handleChange}
                            required
                            placeholder="••••••••"
                            minLength={8}
                            autoComplete="new-password"
                            disabled={isLoading}
                          />
                          <Form.Text className="text-muted">
                            حداقل 8 کاراکتر
                          </Form.Text>
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>{t('auth.forgot.confirm_password')}</Form.Label>
                          <Form.Control
                            type="password"
                            name="password2"
                            value={formData.password2}
                            onChange={handleChange}
                            required
                            placeholder="••••••••"
                            autoComplete="new-password"
                            disabled={isLoading}
                          />
                        </Form.Group>

                        <div className="d-grid mb-3">
                          <Button type="submit" variant="primary" size="lg" disabled={isLoading}>
                            {isLoading ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                {t('common.loading')}
                              </>
                            ) : (
                              t('auth.forgot.submit')
                            )}
                          </Button>
                        </div>

                        <div className="text-center">
                          <Button
                            variant="link"
                            onClick={() => {
                              setStep('identifier');
                              setFormData(prev => ({ ...prev, otp_code: '', password1: '', password2: '' }));
                              setError('');
                            }}
                            disabled={isLoading || sendingOTP}
                          >
                            {t('auth.forgot.change_identifier')}
                          </Button>
                          {' | '}
                          <Button
                            variant="link"
                            onClick={handleSendOTP}
                            disabled={sendingOTP || isLoading}
                          >
                            {sendingOTP ? t('common.loading') : t('auth.forgot.resend')}
                          </Button>
                        </div>
                      </>
                    )}
                  </Form>
                )}

                <hr className="my-4" />

                <div className="text-center">
                  <Link to="/login" className="btn btn-outline-primary">
                    {t('auth.forgot.back_to_login')}
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

export default ForgotPassword;
