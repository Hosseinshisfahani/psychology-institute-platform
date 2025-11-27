import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { Alert, Container, Button, Spinner } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';
import axios from 'axios';
import './Dashboard.css';

interface DashboardStats {
  user: {
    id: number;
    email: string;
    full_name: string;
    user_type: string;
    is_verified: boolean;
    date_joined: string;
  };
  notifications: {
    unread_count: number;
    total_count: number;
  };
  courses?: {
    total_purchased: number;
    total_spent: number;
  };
  packages?: {
    total_purchased: number;
    total_spent: number;
  };
}

const Dashboard: React.FC = () => {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const { t } = useI18n();
  const location = useLocation();
  const navigate = useNavigate();
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [infoMessage, setInfoMessage] = useState<{
    title: string;
    subtitle: string;
    actionPath: string;
    actionLabel: string;
  } | null>(null);

  // Check for success message from navigation state or sessionStorage
  useEffect(() => {
    // Check sessionStorage first (after reload)
    const storedMessage = sessionStorage.getItem('dashboardMessage');
    if (storedMessage) {
      setSuccessMessage(storedMessage);
      sessionStorage.removeItem('dashboardMessage');
      
      // Auto-hide after 5 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 5000);
    }
    
    // Check navigation state (from redirect)
    if (location.state?.message) {
      // Store message in sessionStorage
      sessionStorage.setItem('dashboardMessage', location.state.message);
      // Clear the message from location state
      window.history.replaceState({}, document.title);
      
      // Reload to refresh user data
      window.location.reload();
    }
  }, [location]);

  // Fetch dashboard stats (only if authenticated)
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/dashboard/stats/');
      return response.data as DashboardStats;
    },
    enabled: isAuthenticated,
  });

  const handleRestrictedNavigation = (
    event: React.MouseEvent<HTMLAnchorElement, MouseEvent>,
    type: 'courses' | 'packages'
  ) => {
    if (statsLoading || !stats) {
      return;
    }

    const hasPurchased =
      type === 'courses'
        ? (stats.courses?.total_purchased ?? 0) > 0
        : (stats.packages?.total_purchased ?? 0) > 0;

    if (!hasPurchased) {
      event.preventDefault();
      setInfoMessage({
        title: 'شما هنوز دوره/بسته‌ای خریداری نکردید.',
        subtitle: 'برای خریداری بسته/دوره مورد نظر کلیک کنید.',
        actionPath: type === 'courses' ? '/courses' : '/packages',
        actionLabel: type === 'courses' ? 'مشاهده دوره‌ها' : 'مشاهده بسته‌ها',
      });
    }
  };

  // Show loading spinner while checking auth
  if (authLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3 text-muted">{t('common.loading')}</p>
      </Container>
    );
  }

  // Show message if user is not authenticated
  if (!isAuthenticated) {
    return (
      <Container className="py-5">
        <Alert variant="warning" className="text-center">
          <Alert.Heading>
            <i className="fas fa-exclamation-triangle me-2"></i>
            دسترسی محدود
          </Alert.Heading>
          <p className="mb-4">لطفا ابتدا به حساب کاربری خود وارد شوید</p>
          <Button variant="primary" onClick={() => navigate('/login')}>
            <i className="fas fa-sign-in-alt me-2"></i>
            ورود به حساب کاربری
          </Button>
          <Button 
            variant="outline-primary" 
            className="me-2" 
            onClick={() => navigate('/signup')}
          >
            <i className="fas fa-user-plus me-2"></i>
            ثبت‌نام
          </Button>
        </Alert>
      </Container>
    );
  }

  if (statsLoading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">{t('common.loading')}</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>{t('nav.dashboard')} - {t('home.title')}</title>
      </Helmet>

      <div className="modern-dashboard">
        {/* Success Message */}
        {successMessage && (
          <div className="container mb-3">
            <Alert variant="success" onClose={() => setSuccessMessage('')} dismissible>
              <i className="fas fa-check-circle me-2"></i>
              {successMessage}
            </Alert>
          </div>
        )}

        {infoMessage && (
          <div className="container mb-3">
            <Alert variant="info" onClose={() => setInfoMessage(null)} dismissible>
              <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between">
                <div>
                  <p className="mb-1 fw-bold">{infoMessage.title}</p>
                  <p className="mb-0 text-muted">{infoMessage.subtitle}</p>
                </div>
                <Button
                  variant="primary"
                  className="mt-3 mt-md-0"
                  onClick={() => {
                    navigate(infoMessage.actionPath);
                    setInfoMessage(null);
                  }}
                >
                  <i className="fas fa-shopping-cart me-2"></i>
                  {infoMessage.actionLabel}
                </Button>
              </div>
            </Alert>
          </div>
        )}
        
        <div className="dashboard-container">
          {/* Profile Sidebar */}
          <div className="profile-sidebar">
            <div className="profile-card">
              <div className="profile-image-wrapper">
                {user?.profile_image ? (
                  <img 
                    src={user.profile_image} 
                    alt="Profile" 
                    className="profile-image"
                  />
                ) : (
                  <div className="profile-placeholder">
                    <i className="fas fa-user"></i>
                  </div>
                )}
              </div>
              
              <h3 className="profile-greeting">سلام کاربر عزیز!</h3>
              
              <div className="profile-info">
                <div className="info-item">
                  <span className="info-label">نام:</span>
                  <span className="info-value">{user?.full_name || 'بدون اطلاعات'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">کد ملی:</span>
                  <span className="info-value">{user?.national_id || 'بدون اطلاعات'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">ایمیل:</span>
                  <span className="info-value">{user?.email || 'بدون اطلاعات'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">شماره تلفن:</span>
                  <span className="info-value">{user?.phone_number || 'بدون اطلاعات'}</span>
                </div>
              </div>

              <Link to="/dashboard/profile" className="edit-profile-btn">
                <i className="fas fa-edit me-2"></i>
                ویرایش پروفایل
              </Link>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="dashboard-content">
            <div className="feature-cards-grid">
              {/* Connection with Advisor Card */}
              <div className="feature-card card-blue">
                <div className="card-icon">
                  <i className="fas fa-comments"></i>
                </div>
                <h4 className="card-title">چت آنلاین</h4>
                <Link to="/coach" className="card-btn">
                  <i className="fas fa-eye me-2"></i>
                  مشاهده
                </Link>
              </div>

              {/* My Tests Card */}
              <div className="feature-card card-blue">
                <div className="card-icon">
                  <i className="fas fa-clipboard-list"></i>
                </div>
                <h4 className="card-title">تست‌های من</h4>
                <Link to="/tests" className="card-btn">
                  <i className="fas fa-eye me-2"></i>
                  مشاهده
                </Link>
              </div>

              {/* My Workshops Card */}
              <div className="feature-card card-blue">
                <div className="card-icon">
                  <i className="fas fa-chalkboard-teacher"></i>
                </div>
                <h4 className="card-title">کارگاه‌های من</h4>
                <Link to="/dashboard/my-workshops" className="card-btn">
                  <i className="fas fa-eye me-2"></i>
                  مشاهده
                </Link>
              </div>

              {/* My Educational Packages Card */}
              <div className="feature-card card-purple">
                <div className="card-icon">
                  <i className="fas fa-graduation-cap"></i>
                </div>
                <h4 className="card-title">بسته‌های آموزشی من</h4>
                <p className="card-subtitle">مشاهده وضعیت و مدیریت بسته‌ها</p>
                <Link
                  to="/packages"
                  className="card-btn"
                  onClick={(event) => handleRestrictedNavigation(event, 'packages')}
                >
                  <i className="fas fa-arrow-left me-2"></i>
                  مشاهده بسته‌ها
                </Link>
              </div>

              {/* My Courses Card */}
              <div className="feature-card card-green">
                <div className="card-icon">
                  <i className="fas fa-book-reader"></i>
                </div>
                <h4 className="card-title">دوره‌های من</h4>
                <p className="card-subtitle">دسترسی به دوره‌های خریداری شده</p>
                <Link
                  to="/courses"
                  className="card-btn"
                  onClick={(event) => handleRestrictedNavigation(event, 'courses')}
                >
                  <i className="fas fa-eye me-2"></i>
                  مشاهده دوره‌ها
                </Link>
              </div>

              {/* Financial Reports Card */}
              <div className="feature-card card-dark-teal">
                <div className="card-icon">
                  <i className="fas fa-chart-bar"></i>
                </div>
                <div className="card-count">0 مورد</div>
                <h4 className="card-title">گزارشات مالی</h4>
                <Link to="/financial-reports" className="card-btn">
                  <i className="fas fa-eye me-2"></i>
                  مشاهده
                </Link>
              </div>

              {/* My Appointments Card */}
              <div className="feature-card card-teal">
                <div className="card-icon">
                  <i className="fas fa-calendar-check"></i>
                </div>
                <div className="card-count">0 مورد</div>
                <h4 className="card-title">نوبت‌های من</h4>
                <Link to="/appointments" className="card-btn">
                  <i className="fas fa-eye me-2"></i>
                  مشاهده
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
