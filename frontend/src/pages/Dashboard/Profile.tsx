import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import BirthdayOrDatePicker from '../../components/BirthdayOrDatePicker';
import DateObject from 'react-date-object';
import persian from 'react-date-object/calendars/persian';
import gregorian from 'react-date-object/calendars/gregorian';
import persian_fa from 'react-date-object/locales/persian_fa';
import gregorian_en from 'react-date-object/locales/gregorian_en';
import './Profile.css';

const Profile: React.FC = () => {
  const { user } = useAuth();
  const { t } = useI18n();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    first_name_en: user?.first_name_en || '',
    last_name_en: user?.last_name_en || '',
    email: user?.email || '',
    phone_number: user?.phone_number || '',
    national_id: user?.national_id || '',
    birth_date: user?.birth_date || '',
    gender: user?.gender || '',
    address: user?.address || '',
    city: user?.city || '',
    postal_code: user?.postal_code || '',
    bio: user?.bio || '',
  });

  const [birthDateValue, setBirthDateValue] = useState<any>(null);
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>(user?.profile_image || '');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Initialize birth date picker value from user data
  useEffect(() => {
    if (user?.birth_date) {
      try {
        // Backend sends Gregorian date, convert to Persian DateObject
        const gregorianDate = new DateObject({
          date: user.birth_date,
          calendar: gregorian,
          locale: gregorian_en
        });
        // Convert to Persian calendar for display
        const persianDate = gregorianDate.convert(persian, persian_fa);
        setBirthDateValue(persianDate);
      } catch (e) {
        console.error('Error parsing birth date:', e);
      }
    } else {
      setBirthDateValue(null);
    }
  }, [user?.birth_date]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Special handling for national_id - only allow Persian or ASCII digits
    if (name === 'national_id') {
      // Persian digits: ۰۱۲۳۴۵۶۷۸۹
      // ASCII digits: 0123456789
      const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
      const asciiDigits = '0123456789';
      const allowedChars = persianDigits + asciiDigits;
      
      // Filter out any non-digit characters
      const filteredValue = value.split('').filter(char => allowedChars.includes(char)).join('').slice(0, 10);
      setFormData(prev => ({ ...prev, [name]: filteredValue }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleBirthDateChange = (dateObject: any) => {
    setBirthDateValue(dateObject);
    if (dateObject) {
      // Convert Jalali date to Gregorian ISO format for backend
      try {
        const gregorianDate = dateObject.toDate().toISOString().split('T')[0];
        setFormData(prev => ({ ...prev, birth_date: gregorianDate }));
      } catch (e) {
        console.error('Error converting date:', e);
      }
    } else {
      setFormData(prev => ({ ...prev, birth_date: '' }));
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setProfileImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const getCsrfToken = () => {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      // CSRF token is handled automatically by axios interceptor
      // No need to fetch it manually here
      
      const formDataToSend = new FormData();
      
      // Append all form fields
      Object.entries(formData).forEach(([key, value]) => {
        if (value) {
          formDataToSend.append(key, value);
        }
      });

      // Append profile image if changed
      if (profileImage) {
        formDataToSend.append('profile_image', profileImage);
      }

      // Get CSRF token from cookie
      const csrfToken = getCsrfToken();

      const updateResponse = await axios.patch('/api/dashboard/profile/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': csrfToken || '',
        },
      });

      // Redirect to dashboard with success message
      navigate('/dashboard', {
        state: { message: 'آپدیت پروفایل شما با موفقیت انجام شد' }
      });
    } catch (error: any) {
      setMessage({ 
        type: 'danger', 
        text: error.response?.data?.detail || error.response?.data?.message || 'خطا در به‌روزرسانی پروفایل' 
      });
      console.error('Profile update error:', error.response?.data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Helmet>
        <title>{t('nav.profile')} - {t('home.title')}</title>
      </Helmet>

      <div className="profile-page">
        <Container className="py-4">
          <h2 className="page-title mb-4">
            <i className="fas fa-user-edit me-2"></i>
            ویرایش پروفایل
          </h2>

          {message.text && (
            <Alert variant={message.type} onClose={() => setMessage({ type: '', text: '' })} dismissible>
              {message.text}
            </Alert>
          )}

          <Form onSubmit={handleSubmit}>
            <Row>
              {/* Profile Image Section */}
              <Col lg={4} className="mb-4">
                <Card className="profile-image-card">
                  <Card.Body className="text-center">
                    <div className="profile-image-wrapper">
                      {imagePreview ? (
                        <img src={imagePreview} alt="Profile" className="profile-preview-image" />
                      ) : (
                        <div className="profile-placeholder-large">
                          <i className="fas fa-user"></i>
                        </div>
                      )}
                    </div>
                    
                    <h5 className="mt-3 mb-1">{user?.full_name}</h5>
                    <p className="text-muted mb-3">{user?.email}</p>
                    
                    <Form.Group>
                      <Form.Label className="btn btn-outline-primary btn-sm w-100">
                        <i className="fas fa-camera me-2"></i>
                        تغییر عکس پروفایل
                        <Form.Control
                          type="file"
                          accept="image/*"
                          onChange={handleImageChange}
                          style={{ display: 'none' }}
                        />
                      </Form.Label>
                    </Form.Group>

                    <div className="user-stats mt-4">
                      <div className="stat-item">
                        <i className="fas fa-calendar-alt text-primary"></i>
                        <div>
                          <small className="text-muted">تاریخ عضویت</small>
                          <div>{new Date(user?.date_joined || '').toLocaleDateString('fa-IR')}</div>
                        </div>
                      </div>
                      <div className="stat-item mt-3">
                        <i className="fas fa-check-circle text-success"></i>
                        <div>
                          <small className="text-muted">وضعیت حساب</small>
                          <div>{user?.is_verified ? 'تایید شده' : 'در انتظار تایید'}</div>
                        </div>
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              </Col>

              {/* Profile Form Section */}
              <Col lg={8}>
                <Card className="profile-form-card">
                  <Card.Body>
                    <h5 className="section-title mb-4">
                      <i className="fas fa-info-circle me-2"></i>
                      اطلاعات شخصی
                    </h5>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>نام</Form.Label>
                          <Form.Control
                            type="text"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleInputChange}
                            placeholder="نام خود را وارد کنید"
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>نام خانوادگی</Form.Label>
                          <Form.Control
                            type="text"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleInputChange}
                            placeholder="نام خانوادگی خود را وارد کنید"
                          />
                        </Form.Group>
                      </Col>
                    </Row>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>نام لاتین</Form.Label>
                          <Form.Control
                            type="text"
                            name="first_name_en"
                            value={formData.first_name_en}
                            onChange={handleInputChange}
                            placeholder="Latin First Name"
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>نام خانوادگی لاتین</Form.Label>
                          <Form.Control
                            type="text"
                            name="last_name_en"
                            value={formData.last_name_en}
                            onChange={handleInputChange}
                            placeholder="Latin Last Name"
                          />
                        </Form.Group>
                      </Col>
                    </Row>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>ایمیل</Form.Label>
                          <Form.Control
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            disabled
                            placeholder="ایمیل خود را وارد کنید"
                          />
                          <Form.Text className="text-muted">
                            ایمیل قابل تغییر نیست
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>شماره تماس</Form.Label>
                          <Form.Control
                            type="tel"
                            name="phone_number"
                            value={formData.phone_number}
                            onChange={handleInputChange}
                            placeholder="09123456789"
                          />
                        </Form.Group>
                      </Col>
                    </Row>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>کد ملی</Form.Label>
                          <Form.Control
                            type="text"
                            name="national_id"
                            value={formData.national_id}
                            onChange={handleInputChange}
                            placeholder="کد ملی را با اعداد فارسی وارد کنید"
                            maxLength={10}
                            dir="rtl"
                          />
                          <Form.Text className="text-muted">
                            فقط اعداد فارسی یا لاتین مجاز است
                          </Form.Text>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <BirthdayOrDatePicker
                            label="تاریخ تولد"
                            value={birthDateValue}
                            onChange={handleBirthDateChange}
                            placeholder="تاریخ تولد خود را انتخاب کنید"
                            className="mb-0"
                          />
                        </Form.Group>
                      </Col>
                    </Row>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>جنسیت</Form.Label>
                          <Form.Select
                            name="gender"
                            value={formData.gender}
                            onChange={handleInputChange}
                          >
                            <option value="">انتخاب کنید</option>
                            <option value="M">آقای</option>
                            <option value="F">خانم</option>
                          </Form.Select>
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>شهر</Form.Label>
                          <Form.Control
                            type="text"
                            name="city"
                            value={formData.city}
                            onChange={handleInputChange}
                            placeholder="تهران"
                          />
                        </Form.Group>
                      </Col>
                    </Row>

                    <Form.Group className="mb-3">
                      <Form.Label>آدرس</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={2}
                        name="address"
                        value={formData.address}
                        onChange={handleInputChange}
                        placeholder="آدرس کامل خود را وارد کنید"
                      />
                    </Form.Group>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>کد پستی</Form.Label>
                          <Form.Control
                            type="text"
                            name="postal_code"
                            value={formData.postal_code}
                            onChange={handleInputChange}
                            placeholder="1234567890"
                            maxLength={10}
                          />
                        </Form.Group>
                      </Col>
                    </Row>

                    <Form.Group className="mb-4">
                      <Form.Label>درباره من</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={4}
                        name="bio"
                        value={formData.bio}
                        onChange={handleInputChange}
                        placeholder="درباره خود بنویسید..."
                      />
                    </Form.Group>

                    <div className="d-flex gap-2 justify-content-end">
                      <Button variant="secondary" type="button" onClick={() => window.history.back()}>
                        <i className="fas fa-times me-2"></i>
                        انصراف
                      </Button>
                      <Button variant="primary" type="submit" disabled={loading}>
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                            در حال ذخیره...
                          </>
                        ) : (
                          <>
                            <i className="fas fa-save me-2"></i>
                            ذخیره تغییرات
                          </>
                        )}
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Form>
        </Container>
      </div>
    </>
  );
};

export default Profile;
