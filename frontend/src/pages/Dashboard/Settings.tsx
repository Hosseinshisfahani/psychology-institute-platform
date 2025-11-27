import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Tab, Tabs } from 'react-bootstrap';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';
import { useTheme } from '../../contexts/ThemeContext';
import axios from 'axios';

interface PasswordChangeData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface NotificationSettings {
  email_notifications: boolean;
  sms_notifications: boolean;
  course_reminders: boolean;
  session_reminders: boolean;
  marketing_emails: boolean;
}

interface PrivacySettings {
  profile_visibility: 'public' | 'private';
  show_progress: boolean;
  show_certificates: boolean;
}

const Settings: React.FC = () => {
  const { user } = useAuth();
  const { t, language, changeLanguage } = useI18n();
  const { theme, toggleTheme } = useTheme();
  const queryClient = useQueryClient();

  const [passwordData, setPasswordData] = useState<PasswordChangeData>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [notifications, setNotifications] = useState<NotificationSettings>({
    email_notifications: true,
    sms_notifications: false,
    course_reminders: true,
    session_reminders: true,
    marketing_emails: false,
  });

  const [privacy, setPrivacy] = useState<PrivacySettings>({
    profile_visibility: 'public',
    show_progress: true,
    show_certificates: true,
  });

  const [alerts, setAlerts] = useState<{ type: 'success' | 'danger'; message: string } | null>(null);

  // Password change mutation
  const passwordMutation = useMutation({
    mutationFn: async (data: PasswordChangeData) => {
      await axios.post('/api/dashboard/change-password/', data);
    },
    onSuccess: () => {
      setAlerts({ type: 'success', message: 'رمز عبور با موفقیت تغییر یافت' });
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    },
    onError: (error: any) => {
      setAlerts({ 
        type: 'danger', 
        message: error.response?.data?.error || 'خطا در تغییر رمز عبور' 
      });
    },
  });

  // Notification settings mutation
  const notificationMutation = useMutation({
    mutationFn: async (data: NotificationSettings) => {
      await axios.post('/api/dashboard/notification-settings/', data);
    },
    onSuccess: () => {
      setAlerts({ type: 'success', message: 'تنظیمات اعلان‌ها ذخیره شد' });
    },
    onError: () => {
      setAlerts({ type: 'danger', message: 'خطا در ذخیره تنظیمات' });
    },
  });

  // Privacy settings mutation
  const privacyMutation = useMutation({
    mutationFn: async (data: PrivacySettings) => {
      await axios.post('/api/dashboard/privacy-settings/', data);
    },
    onSuccess: () => {
      setAlerts({ type: 'success', message: 'تنظیمات حریم خصوصی ذخیره شد' });
    },
    onError: () => {
      setAlerts({ type: 'danger', message: 'خطا در ذخیره تنظیمات' });
    },
  });

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setAlerts({ type: 'danger', message: 'رمز عبور جدید و تکرار آن مطابقت ندارند' });
      return;
    }
    
    if (passwordData.new_password.length < 8) {
      setAlerts({ type: 'danger', message: 'رمز عبور باید حداقل ۸ کاراکتر باشد' });
      return;
    }
    
    passwordMutation.mutate(passwordData);
  };

  const handleNotificationSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    notificationMutation.mutate(notifications);
  };

  const handlePrivacySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    privacyMutation.mutate(privacy);
  };

  const handleDeleteAccount = () => {
    if (window.confirm('آیا مطمئن هستید که می‌خواهید حساب کاربری خود را حذف کنید؟ این عمل غیرقابل بازگشت است.')) {
      // Handle account deletion
      console.log('Delete account requested');
    }
  };

  return (
    <>
      <Helmet>
        <title>تنظیمات - {user?.full_name}</title>
        <meta name="description" content="تنظیمات حساب کاربری، رمز عبور، اعلان‌ها و حریم خصوصی" />
      </Helmet>

      <Container className="py-4">
        <Row>
          <Col lg={8} className="mx-auto">
            <div className="d-flex align-items-center mb-4">
              <i className="fas fa-cog me-3 text-primary fs-3"></i>
              <h2 className="mb-0">تنظیمات</h2>
            </div>

            {alerts && (
              <Alert 
                variant={alerts.type} 
                dismissible 
                onClose={() => setAlerts(null)}
                className="mb-4"
              >
                {alerts.message}
              </Alert>
            )}

            <Tabs defaultActiveKey="general" className="mb-4">
              {/* General Settings */}
              <Tab eventKey="general" title="عمومی">
                <Card>
                  <Card.Body>
                    <h5 className="mb-4">تنظیمات عمومی</h5>
                    
                    <Form>
                      <Row>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label>زبان</Form.Label>
                            <Form.Select 
                              value={language} 
                              onChange={(e) => changeLanguage(e.target.value)}
                            >
                              <option value="fa">فارسی</option>
                              <option value="en">English</option>
                            </Form.Select>
                          </Form.Group>
                        </Col>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label>تم</Form.Label>
                            <div className="d-flex gap-2">
                              <Button
                                variant={theme === 'light' ? 'primary' : 'outline-primary'}
                                onClick={theme === 'dark' ? toggleTheme : undefined}
                              >
                                <i className="fas fa-sun me-2"></i>روشن
                              </Button>
                              <Button
                                variant={theme === 'dark' ? 'primary' : 'outline-primary'}
                                onClick={theme === 'light' ? toggleTheme : undefined}
                              >
                                <i className="fas fa-moon me-2"></i>تاریک
                              </Button>
                            </div>
                          </Form.Group>
                        </Col>
                      </Row>
                    </Form>
                  </Card.Body>
                </Card>
              </Tab>

              {/* Password */}
              <Tab eventKey="password" title="رمز عبور">
                <Card>
                  <Card.Body>
                    <h5 className="mb-4">تغییر رمز عبور</h5>
                    
                    <Form onSubmit={handlePasswordSubmit}>
                      <Form.Group className="mb-3">
                        <Form.Label>رمز عبور فعلی</Form.Label>
                        <Form.Control
                          type="password"
                          value={passwordData.current_password}
                          onChange={(e) => setPasswordData(prev => ({
                            ...prev,
                            current_password: e.target.value
                          }))}
                          required
                        />
                      </Form.Group>
                      
                      <Form.Group className="mb-3">
                        <Form.Label>رمز عبور جدید</Form.Label>
                        <Form.Control
                          type="password"
                          value={passwordData.new_password}
                          onChange={(e) => setPasswordData(prev => ({
                            ...prev,
                            new_password: e.target.value
                          }))}
                          minLength={8}
                          required
                        />
                        <Form.Text className="text-muted">
                          رمز عبور باید حداقل ۸ کاراکتر باشد
                        </Form.Text>
                      </Form.Group>
                      
                      <Form.Group className="mb-4">
                        <Form.Label>تکرار رمز عبور جدید</Form.Label>
                        <Form.Control
                          type="password"
                          value={passwordData.confirm_password}
                          onChange={(e) => setPasswordData(prev => ({
                            ...prev,
                            confirm_password: e.target.value
                          }))}
                          required
                        />
                      </Form.Group>
                      
                      <Button 
                        type="submit" 
                        variant="primary"
                        disabled={passwordMutation.isPending}
                      >
                        {passwordMutation.isPending ? 'در حال ذخیره...' : 'تغییر رمز عبور'}
                      </Button>
                    </Form>
                  </Card.Body>
                </Card>
              </Tab>

              {/* Notifications */}
              <Tab eventKey="notifications" title="اعلان‌ها">
                <Card>
                  <Card.Body>
                    <h5 className="mb-4">تنظیمات اعلان‌ها</h5>
                    
                    <Form onSubmit={handleNotificationSubmit}>
                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          id="email-notifications"
                          label="اعلان‌های ایمیل"
                          checked={notifications.email_notifications}
                          onChange={(e) => setNotifications(prev => ({
                            ...prev,
                            email_notifications: e.target.checked
                          }))}
                        />
                        <Form.Text className="text-muted">
                          دریافت اعلان‌های مهم از طریق ایمیل
                        </Form.Text>
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          id="sms-notifications"
                          label="اعلان‌های پیامکی"
                          checked={notifications.sms_notifications}
                          onChange={(e) => setNotifications(prev => ({
                            ...prev,
                            sms_notifications: e.target.checked
                          }))}
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          id="course-reminders"
                          label="یادآوری بسته‌های آموزشی"
                          checked={notifications.course_reminders}
                          onChange={(e) => setNotifications(prev => ({
                            ...prev,
                            course_reminders: e.target.checked
                          }))}
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          id="session-reminders"
                          label="یادآوری جلسات"
                          checked={notifications.session_reminders}
                          onChange={(e) => setNotifications(prev => ({
                            ...prev,
                            session_reminders: e.target.checked
                          }))}
                        />
                      </Form.Group>

                      <Form.Group className="mb-4">
                        <Form.Check
                          type="switch"
                          id="marketing-emails"
                          label="ایمیل‌های تبلیغاتی"
                          checked={notifications.marketing_emails}
                          onChange={(e) => setNotifications(prev => ({
                            ...prev,
                            marketing_emails: e.target.checked
                          }))}
                        />
                      </Form.Group>

                      <Button 
                        type="submit" 
                        variant="primary"
                        disabled={notificationMutation.isPending}
                      >
                        {notificationMutation.isPending ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
                      </Button>
                    </Form>
                  </Card.Body>
                </Card>
              </Tab>

              {/* Privacy */}
              <Tab eventKey="privacy" title="حریم خصوصی">
                <Card>
                  <Card.Body>
                    <h5 className="mb-4">تنظیمات حریم خصوصی</h5>
                    
                    <Form onSubmit={handlePrivacySubmit}>
                      <Form.Group className="mb-3">
                        <Form.Label>نمایش پروفایل</Form.Label>
                        <Form.Select
                          value={privacy.profile_visibility}
                          onChange={(e) => setPrivacy(prev => ({
                            ...prev,
                            profile_visibility: e.target.value as 'public' | 'private'
                          }))}
                        >
                          <option value="public">عمومی</option>
                          <option value="private">خصوصی</option>
                        </Form.Select>
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Check
                          type="switch"
                          id="show-progress"
                          label="نمایش پیشرفت بسته‌های آموزشی"
                          checked={privacy.show_progress}
                          onChange={(e) => setPrivacy(prev => ({
                            ...prev,
                            show_progress: e.target.checked
                          }))}
                        />
                      </Form.Group>

                      <Form.Group className="mb-4">
                        <Form.Check
                          type="switch"
                          id="show-certificates"
                          label="نمایش گواهینامه‌ها"
                          checked={privacy.show_certificates}
                          onChange={(e) => setPrivacy(prev => ({
                            ...prev,
                            show_certificates: e.target.checked
                          }))}
                        />
                      </Form.Group>

                      <Button 
                        type="submit" 
                        variant="primary"
                        disabled={privacyMutation.isPending}
                      >
                        {privacyMutation.isPending ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
                      </Button>
                    </Form>
                  </Card.Body>
                </Card>
              </Tab>

              {/* Danger Zone */}
              <Tab eventKey="danger" title="منطقه خطر">
                <Card border="danger">
                  <Card.Body>
                    <h5 className="text-danger mb-4">منطقه خطر</h5>
                    
                    <div className="p-3 border border-danger rounded mb-3">
                      <h6 className="text-danger">حذف حساب کاربری</h6>
                      <p className="text-muted mb-3">
                        حذف حساب کاربری شما تمام اطلاعات، پیشرفت بسته‌های آموزشی، و داده‌های مرتبط را به صورت دائمی پاک می‌کند.
                        این عمل غیرقابل بازگشت است.
                      </p>
                      
                      <Button 
                        variant="outline-danger"
                        onClick={handleDeleteAccount}
                      >
                        <i className="fas fa-trash me-2"></i>
                        حذف حساب کاربری
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              </Tab>
            </Tabs>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Settings;
