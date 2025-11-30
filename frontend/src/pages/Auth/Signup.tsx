import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';

const Signup: React.FC = () => {
  const { t } = useI18n();
  const { signup, sendOTP, verifyOTP } = useAuth();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    email: '',
    password1: '',
    password2: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    otp_code: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState<'form' | 'otp'>('form');
  const [otpSent, setOtpSent] = useState(false);
  const [sendingOTP, setSendingOTP] = useState(false);
  const [verifyingOTP, setVerifyingOTP] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSendOTP = async () => {
    setError('');
    console.log('[Signup] handleSendOTP called', { phone_number: formData.phone_number });
    
    // Validate phone number
    if (!formData.phone_number) {
      setError('لطفاً شماره تلفن خود را وارد کنید');
      console.log('[Signup] Validation failed: phone number missing');
      return;
    }
    
    // Validate phone number format (Iranian mobile: 09xxxxxxxxx)
    const phoneRegex = /^09\d{9}$/;
    const normalizedPhone = formData.phone_number.replace(/\s/g, '');
    if (!phoneRegex.test(normalizedPhone)) {
      setError('فرمت شماره تلفن صحیح نیست. مثال: 09123456789');
      console.log('[Signup] Validation failed: invalid phone format', normalizedPhone);
      return;
    }
    
    setSendingOTP(true);
    console.log('[Signup] Calling sendOTP API', { phone: normalizedPhone, purpose: 'signup' });
    try {
      await sendOTP(normalizedPhone, 'signup');
      console.log('[Signup] OTP sent successfully');
      // Success - show OTP input field
      setOtpSent(true);
      setStep('otp');
      setError(''); // Clear any previous errors
    } catch (err: any) {
      console.error('[Signup] Error sending OTP:', err);
      // Better error message handling
      let errorMsg = 'خطا در ارسال کد تایید';
      
      if (err.message) {
        const msg = err.message;
        // Don't show raw numbers or status codes
        if (typeof msg === 'string' && !/^\d+$/.test(msg)) {
          errorMsg = msg;
        } else if (typeof msg === 'string' && msg.length > 0) {
          errorMsg = `خطا در ارسال کد تایید: ${msg}`;
        }
      }
      
      setError(errorMsg);
    } finally {
      setSendingOTP(false);
    }
  };

  const handleVerifyOTP = async () => {
    setError('');
    
    // Accept both 4-digit and 6-digit codes (SMS service may send 4-digit)
    if (!formData.otp_code || (formData.otp_code.length !== 4 && formData.otp_code.length !== 6)) {
      setError('لطفاً کد تایید را وارد کنید (4 یا 6 رقمی)');
      return;
    }
    
    setVerifyingOTP(true);
    try {
      const normalizedPhone = formData.phone_number.replace(/\s/g, '');
      await verifyOTP(normalizedPhone, formData.otp_code, 'signup');
      setOtpVerified(true);
      // After OTP verification, proceed with signup
      await handleSignup();
    } catch (err: any) {
      // Better error message handling
      let errorMsg = 'کد تایید نامعتبر است';
      
      if (err.message) {
        const msg = err.message;
        // Don't show raw numbers or status codes
        if (typeof msg === 'string' && !/^\d+$/.test(msg)) {
          errorMsg = msg;
        } else if (typeof msg === 'string' && msg.length > 0) {
          errorMsg = `خطا در تایید کد: ${msg}`;
        }
      }
      
      setError(errorMsg);
    } finally {
      setVerifyingOTP(false);
    }
  };

  const handleSignup = async () => {
    setError('');
    setIsLoading(true);

    // Basic validation
    if (formData.password1 !== formData.password2) {
      setError('رمزهای عبور مطابقت ندارند');
      setIsLoading(false);
      return;
    }

    if (formData.password1.length < 8) {
      setError('رمز عبور باید حداقل 8 کاراکتر باشد');
      setIsLoading(false);
      return;
    }

    if (!otpVerified) {
      setError('لطفاً ابتدا شماره تلفن خود را تایید کنید');
      setIsLoading(false);
      return;
    }

    try {
      const normalizedPhone = formData.phone_number.replace(/\s/g, '');
      await signup(
        formData.email,
        formData.password1,
        formData.password2,
        formData.first_name,
        formData.last_name,
        normalizedPhone,
        formData.otp_code
      );
      navigate('/');
    } catch (err: any) {
      // Better error message handling
      let errorMsg = 'خطا در ثبت‌نام';
      
      if (err.message) {
        const msg = err.message;
        // Don't show raw numbers or status codes
        if (typeof msg === 'string' && !/^\d+$/.test(msg)) {
          errorMsg = msg;
        } else if (typeof msg === 'string' && msg.length > 0) {
          errorMsg = `خطا در ثبت‌نام: ${msg}`;
        }
      }
      
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('[Signup] Form submitted', { step, formData, agreeToTerms });
    
    if (step === 'form') {
      // Validate form fields first
      if (!formData.first_name || !formData.last_name || !formData.email || !formData.password1 || !formData.password2) {
        console.log('[Signup] Validation failed: missing fields', {
          first_name: !!formData.first_name,
          last_name: !!formData.last_name,
          email: !!formData.email,
          password1: !!formData.password1,
          password2: !!formData.password2,
        });
        setError('لطفاً تمام فیلدها را پر کنید');
        return;
      }
      
      // Check terms acceptance
      if (!agreeToTerms) {
        console.log('[Signup] Validation failed: terms not accepted');
        setError('لطفاً شرایط و قوانین را بپذیرید');
        return;
      }
      
      // Then send OTP
      console.log('[Signup] All validations passed, calling handleSendOTP');
      await handleSendOTP();
    } else if (step === 'otp') {
      // Verify OTP and signup
      await handleVerifyOTP();
    }
  };

  return (
    <>
      <Helmet>
        <title>{t('auth.signup.title')} - {t('home.title')}</title>
      </Helmet>

      <Container className="py-5">
        <Row className="justify-content-center">
          <Col md={6} lg={5}>
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
                  <h4 className="mb-0">{t('auth.signup.title')}</h4>
                </div>

                {error && (
                  <Alert variant="danger" className="mb-3">
                    {error}
                    {step === 'form' && error.includes('ارسال') && (
                      <div className="mt-2">
                        <Button
                          variant="link"
                          size="sm"
                          className="p-0"
                          onClick={() => {
                            // If user received OTP despite error, allow them to proceed
                            setStep('otp');
                            setOtpSent(true);
                            setError('');
                          }}
                        >
                          کد را دریافت کرده‌ام، ادامه می‌دهم
                        </Button>
                      </div>
                    )}
                  </Alert>
                )}

                <Form onSubmit={handleSubmit}>
                  {step === 'form' ? (
                    <>
                      <Row>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label>{t('auth.signup.first_name')}</Form.Label>
                            <Form.Control
                              type="text"
                              name="first_name"
                              value={formData.first_name}
                              onChange={handleChange}
                              required
                              placeholder="نام"
                              disabled={sendingOTP}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label>{t('auth.signup.last_name')}</Form.Label>
                            <Form.Control
                              type="text"
                              name="last_name"
                              value={formData.last_name}
                              onChange={handleChange}
                              required
                              placeholder="نام خانوادگی"
                              disabled={sendingOTP}
                            />
                          </Form.Group>
                        </Col>
                      </Row>

                      <Form.Group className="mb-3">
                        <Form.Label>{t('auth.signup.email')}</Form.Label>
                        <Form.Control
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          required
                          placeholder="example@email.com"
                          disabled={sendingOTP}
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label>شماره تلفن</Form.Label>
                        <Form.Control
                          type="tel"
                          name="phone_number"
                          value={formData.phone_number}
                          onChange={handleChange}
                          required
                          placeholder="09123456789"
                          disabled={sendingOTP}
                          maxLength={11}
                          autoComplete="tel"
                        />
                        <Form.Text className="text-muted">
                          شماره تلفن همراه خود را وارد کنید
                        </Form.Text>
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label>{t('auth.signup.password')}</Form.Label>
                        <Form.Control
                          type="password"
                          name="password1"
                          value={formData.password1}
                          onChange={handleChange}
                          required
                          placeholder="••••••••"
                          minLength={8}
                          disabled={sendingOTP}
                          autoComplete="new-password"
                        />
                        <Form.Text className="text-muted">
                          حداقل 8 کاراکتر
                        </Form.Text>
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label>{t('auth.signup.confirm_password')}</Form.Label>
                        <Form.Control
                          type="password"
                          name="password2"
                          value={formData.password2}
                          onChange={handleChange}
                          required
                          placeholder="••••••••"
                          disabled={sendingOTP}
                          autoComplete="new-password"
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Check
                          type="checkbox"
                          id="agree-terms-signup"
                          checked={agreeToTerms}
                          onChange={(e) => setAgreeToTerms(e.target.checked)}
                          label={
                            <span>
                              با{' '}
                              <Link to="/terms" target="_blank" onClick={(e) => e.stopPropagation()}>
                                شرایط و قوانین
                              </Link>
                              {' '}موافقم
                            </span>
                          }
                          required
                        />
                      </Form.Group>

                      <div className="d-grid mb-3">
                        <Button 
                          type="submit" 
                          variant="primary" 
                          size="lg"
                          disabled={sendingOTP || isLoading || !agreeToTerms}
                        >
                          {sendingOTP ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                              در حال ارسال کد تایید...
                            </>
                          ) : (
                            'ارسال کد تایید'
                          )}
                        </Button>
                      </div>
                    </>
                  ) : (
                    <>
                      <Alert variant="info" className="mb-3">
                        کد تایید به شماره {formData.phone_number} ارسال شد.
                      </Alert>
                      
                      <Form.Group className="mb-3">
                        <Form.Label>کد تایید</Form.Label>
                        <Form.Control
                          type="text"
                          name="otp_code"
                          value={formData.otp_code}
                          onChange={handleChange}
                          required
                          placeholder="کد تایید"
                          maxLength={6}
                          disabled={verifyingOTP || isLoading}
                          className="text-center"
                          style={{ fontSize: '1.5rem', letterSpacing: '0.5rem' }}
                        />
                        <Form.Text className="text-muted">
                          کد تایید ارسال شده را وارد کنید (4 یا 6 رقمی)
                        </Form.Text>
                      </Form.Group>

                      <div className="d-grid mb-3">
                        <Button 
                          type="submit" 
                          variant="primary" 
                          size="lg"
                          disabled={verifyingOTP || isLoading}
                        >
                          {verifyingOTP || isLoading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                              {isLoading ? 'در حال ثبت‌نام...' : 'در حال تایید...'}
                            </>
                          ) : (
                            'تایید و ثبت‌نام'
                          )}
                        </Button>
                      </div>

                      <div className="text-center">
                        <Button 
                          variant="link" 
                          onClick={() => {
                            setStep('form');
                            setOtpSent(false);
                            setOtpVerified(false);
                            setFormData(prev => ({ ...prev, otp_code: '' }));
                          }}
                          disabled={verifyingOTP || isLoading}
                        >
                          تغییر شماره تلفن
                        </Button>
                        {' | '}
                        <Button 
                          variant="link" 
                          onClick={handleSendOTP}
                          disabled={sendingOTP || verifyingOTP || isLoading}
                        >
                          ارسال مجدد کد
                        </Button>
                      </div>
                    </>
                  )}
                </Form>

                <hr className="my-4" />

                <div className="text-center">
                  <p className="mb-0 text-muted">
                    {t('auth.signup.have_account')}
                  </p>
                  <Link to="/login" className="btn btn-outline-primary mt-2">
                    {t('auth.signup.login_link')}
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

export default Signup;
