import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Alert, Tab, Tabs } from 'react-bootstrap';
import { useQuery } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import './AdminDashboard.css';

interface DashboardStats {
  total_users: number;
  total_courses: number;
  total_sessions: number;
  total_revenue: number;
  active_users: number;
  pending_sessions: number;
}

interface RecentActivity {
  id: number;
  type: 'user_registration' | 'course_enrollment' | 'session_booking' | 'payment';
  description: string;
  user_name: string;
  created_at: string;
  status: 'success' | 'pending' | 'failed';
}

interface User {
  id: number;
  full_name: string;
  email: string;
  user_type: string;
  is_active: boolean;
  created_at: string;
  last_login: string;
}

interface Course {
  id: number;
  title: string;
  instructor_name: string;
  status: string;
  enrollment_count: number;
  revenue: number;
}

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/dashboard/stats/');
      return response.data;
    },
    enabled: user?.user_type === 'admin',
  });

  // Fetch recent activities
  const { data: activities = [] } = useQuery<RecentActivity[]>({
    queryKey: ['admin-activities'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/activities/');
      return response.data;
    },
    enabled: user?.user_type === 'admin',
  });

  // Fetch users
  const { data: users = [] } = useQuery<User[]>({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/users/');
      return response.data.results || [];
    },
    enabled: user?.user_type === 'admin',
  });

  // Fetch courses
  const { data: courses = [] } = useQuery<Course[]>({
    queryKey: ['admin-courses'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/courses/');
      return response.data.results || [];
    },
    enabled: user?.user_type === 'admin',
  });

  // Check if user is admin
  if (user?.user_type !== 'admin') {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          شما دسترسی به این بخش ندارید.
        </Alert>
      </Container>
    );
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fa-IR').format(price);
  };

  const getActivityIcon = (type: string) => {
    const icons: Record<string, string> = {
      user_registration: 'fas fa-user-plus',
      course_enrollment: 'fas fa-book',
      session_booking: 'fas fa-calendar',
      payment: 'fas fa-credit-card',
    };
    return icons[type] || 'fas fa-info-circle';
  };

  const getActivityColor = (type: string) => {
    const colors: Record<string, string> = {
      user_registration: 'success',
      course_enrollment: 'primary',
      session_booking: 'warning',
      payment: 'info',
    };
    return colors[type] || 'secondary';
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      success: 'success',
      pending: 'warning',
      failed: 'danger',
    };
    return variants[status] || 'secondary';
  };

  if (statsLoading) {
    return (
      <Container className="py-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">در حال بارگذاری...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>پنل مدیریت - مرکز مشاوره سرمد</title>
        <meta name="description" content="پنل مدیریت سیستم" />
      </Helmet>

      <Container fluid className="admin-dashboard-container">
        {/* Header */}
        <div className="admin-dashboard-header">
          <h2>
            <i className="fas fa-tachometer-alt me-2 text-primary"></i>
            پنل مدیریت
          </h2>
          <div className="admin-dashboard-actions">
            <Button variant="outline-primary">
              <i className="fas fa-download me-2"></i>
              <span className="d-none d-sm-inline">گزارش</span>
              <span className="d-sm-none">گزارش</span>
            </Button>
          </div>
        </div>

        <Tabs 
          activeKey={activeTab} 
          onSelect={(k) => setActiveTab(k || 'overview')}
          className="admin-tabs"
        >
          {/* Overview Tab */}
          <Tab eventKey="overview" title="نمای کلی">
            <Row className="mb-4">
              {/* Stats Cards */}
              <Col xl={3} lg={6} md={6} sm={6} xs={12} className="mb-3">
                <Card className="admin-stats-card text-center">
                  <Card.Body>
                    <i className="fas fa-users text-primary stats-icon"></i>
                    <div className="stats-value">{stats?.total_users || 0}</div>
                    <p className="stats-label mb-0">کل کاربران</p>
                  </Card.Body>
                </Card>
              </Col>
              <Col xl={3} lg={6} md={6} sm={6} xs={12} className="mb-3">
                <Card className="admin-stats-card text-center">
                  <Card.Body>
                    <i className="fas fa-book text-success stats-icon"></i>
                    <div className="stats-value">{stats?.total_courses || 0}</div>
                    <p className="stats-label mb-0">کل بسته‌های آموزشی</p>
                  </Card.Body>
                </Card>
              </Col>
              <Col xl={3} lg={6} md={6} sm={6} xs={12} className="mb-3">
                <Card className="admin-stats-card text-center">
                  <Card.Body>
                    <i className="fas fa-calendar text-warning stats-icon"></i>
                    <div className="stats-value">{stats?.total_sessions || 0}</div>
                    <p className="stats-label mb-0">کل جلسات</p>
                  </Card.Body>
                </Card>
              </Col>
              <Col xl={3} lg={6} md={6} sm={6} xs={12} className="mb-3">
                <Card className="admin-stats-card text-center">
                  <Card.Body>
                    <i className="fas fa-chart-line text-info stats-icon"></i>
                    <div className="stats-value">{formatPrice(stats?.total_revenue || 0)}</div>
                    <p className="stats-label mb-0">کل درآمد (تومان)</p>
                  </Card.Body>
                </Card>
              </Col>
            </Row>

            <Row>
              {/* Recent Activities */}
              <Col lg={8} className="mb-4 mb-lg-0">
                <Card>
                  <Card.Header>
                    <h5 className="mb-0">فعالیت‌های اخیر</h5>
                  </Card.Header>
                  <Card.Body>
                    {activities.length === 0 ? (
                      <p className="text-muted text-center py-3">هیچ فعالیتی یافت نشد</p>
                    ) : (
                      <div className="activity-list">
                        {activities.slice(0, 10).map((activity) => (
                          <div key={activity.id} className="activity-item">
                            <div className={`activity-icon-wrapper bg-${getActivityColor(activity.type)}-light`}>
                              <i className={`${getActivityIcon(activity.type)} text-${getActivityColor(activity.type)}`}></i>
                            </div>
                            <div className="activity-content">
                              <div className="activity-description">{activity.description}</div>
                              <div className="activity-meta">
                                <span>{activity.user_name}</span>
                                <span>•</span>
                                <span>{activity.created_at}</span>
                              </div>
                            </div>
                            <Badge bg={getStatusBadge(activity.status)} className="activity-badge">
                              {activity.status === 'success' && 'موفق'}
                              {activity.status === 'pending' && 'در انتظار'}
                              {activity.status === 'failed' && 'ناموفق'}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    )}
                  </Card.Body>
                </Card>
              </Col>

              {/* Quick Stats */}
              <Col lg={4}>
                <Card className="quick-stats-card">
                  <Card.Header>
                    <h5 className="mb-0">آمار سریع</h5>
                  </Card.Header>
                  <Card.Body>
                    <div className="stat-item">
                      <span className="stat-label">کاربران فعال:</span>
                      <Badge bg="success" className="stat-value">{stats?.active_users || 0}</Badge>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">جلسات در انتظار:</span>
                      <Badge bg="warning" className="stat-value">{stats?.pending_sessions || 0}</Badge>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">نرخ تبدیل:</span>
                      <span className="stat-value fw-bold">12.5%</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">رضایت مشتریان:</span>
                      <span className="stat-value fw-bold text-success">4.8/5</span>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Tab>

          {/* Users Tab */}
          <Tab eventKey="users" title="کاربران">
            <Card>
              <Card.Header>
                <h5 className="mb-0">مدیریت کاربران</h5>
              </Card.Header>
              <Card.Body>
                {/* Desktop Table View */}
                <div className="admin-table-wrapper">
                  <Table responsive className="admin-table">
                    <thead>
                      <tr>
                        <th>نام</th>
                        <th>ایمیل</th>
                        <th>نوع کاربر</th>
                        <th>وضعیت</th>
                        <th>تاریخ عضویت</th>
                        <th>عملیات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td>{user.full_name}</td>
                          <td>{user.email}</td>
                          <td>
                            <Badge bg="secondary">{user.user_type}</Badge>
                          </td>
                          <td>
                            <Badge bg={user.is_active ? 'success' : 'danger'}>
                              {user.is_active ? 'فعال' : 'غیرفعال'}
                            </Badge>
                          </td>
                          <td>{user.created_at}</td>
                          <td>
                            <div className="action-buttons">
                              <Button variant="outline-primary" size="sm">
                                <i className="fas fa-edit"></i>
                              </Button>
                              <Button variant="outline-danger" size="sm">
                                <i className="fas fa-ban"></i>
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>

                {/* Mobile Card View */}
                <div className="mobile-table-cards">
                  {users.length === 0 ? (
                    <p className="text-muted text-center py-3">هیچ کاربری یافت نشد</p>
                  ) : (
                    users.map((user) => (
                    <div key={user.id} className="mobile-table-card">
                      <div className="card-row">
                        <span className="card-label">نام:</span>
                        <span className="card-value">{user.full_name}</span>
                      </div>
                      <div className="card-row">
                        <span className="card-label">ایمیل:</span>
                        <span className="card-value">{user.email}</span>
                      </div>
                      <div className="card-row">
                        <span className="card-label">نوع کاربر:</span>
                        <span className="card-value">
                          <Badge bg="secondary">{user.user_type}</Badge>
                        </span>
                      </div>
                      <div className="card-row">
                        <span className="card-label">وضعیت:</span>
                        <span className="card-value">
                          <Badge bg={user.is_active ? 'success' : 'danger'}>
                            {user.is_active ? 'فعال' : 'غیرفعال'}
                          </Badge>
                        </span>
                      </div>
                      <div className="card-row">
                        <span className="card-label">تاریخ عضویت:</span>
                        <span className="card-value">{user.created_at}</span>
                      </div>
                      <div className="card-actions">
                        <Button variant="outline-primary" size="sm" className="flex-fill">
                          <i className="fas fa-edit me-2"></i>
                          ویرایش
                        </Button>
                        <Button variant="outline-danger" size="sm" className="flex-fill">
                          <i className="fas fa-ban me-2"></i>
                          غیرفعال
                        </Button>
                      </div>
                    </div>
                    ))
                  )}
                </div>
              </Card.Body>
            </Card>
          </Tab>

          {/* Courses Tab */}
          <Tab eventKey="courses" title="بسته‌های آموزشی">
            <Card>
              <Card.Header>
                <h5 className="mb-0">مدیریت بسته‌های آموزشی</h5>
              </Card.Header>
              <Card.Body>
                {/* Desktop Table View */}
                <div className="admin-table-wrapper">
                  <Table responsive className="admin-table">
                    <thead>
                      <tr>
                        <th>عنوان بسته آموزشی</th>
                        <th>مدرس</th>
                        <th>وضعیت</th>
                        <th>تعداد ثبت‌نام</th>
                        <th>درآمد</th>
                        <th>عملیات</th>
                      </tr>
                    </thead>
                    <tbody>
                      {courses.map((course) => (
                        <tr key={course.id}>
                          <td>{course.title}</td>
                          <td>{course.instructor_name}</td>
                          <td>
                            <Badge bg={course.status === 'published' ? 'success' : 'warning'}>
                              {course.status === 'published' ? 'منتشر شده' : 'پیش‌نویس'}
                            </Badge>
                          </td>
                          <td>{course.enrollment_count}</td>
                          <td>{formatPrice(course.revenue)} تومان</td>
                          <td>
                            <div className="action-buttons">
                              <Button variant="outline-primary" size="sm">
                                <i className="fas fa-edit"></i>
                              </Button>
                              <Button variant="outline-success" size="sm">
                                <i className="fas fa-eye"></i>
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>

                {/* Mobile Card View */}
                <div className="mobile-table-cards">
                  {courses.length === 0 ? (
                    <p className="text-muted text-center py-3">هیچ بسته آموزشی یافت نشد</p>
                  ) : (
                    courses.map((course) => (
                    <div key={course.id} className="mobile-table-card">
                      <div className="card-row">
                        <span className="card-label">عنوان:</span>
                        <span className="card-value">{course.title}</span>
                      </div>
                      <div className="card-row">
                        <span className="card-label">مدرس:</span>
                        <span className="card-value">{course.instructor_name}</span>
                      </div>
                      <div className="card-row">
                        <span className="card-label">وضعیت:</span>
                        <span className="card-value">
                          <Badge bg={course.status === 'published' ? 'success' : 'warning'}>
                            {course.status === 'published' ? 'منتشر شده' : 'پیش‌نویس'}
                          </Badge>
                        </span>
                      </div>
                      <div className="card-row">
                        <span className="card-label">تعداد ثبت‌نام:</span>
                        <span className="card-value">{course.enrollment_count}</span>
                      </div>
                      <div className="card-row">
                        <span className="card-label">درآمد:</span>
                        <span className="card-value">{formatPrice(course.revenue)} تومان</span>
                      </div>
                      <div className="card-actions">
                        <Button variant="outline-primary" size="sm" className="flex-fill">
                          <i className="fas fa-edit me-2"></i>
                          ویرایش
                        </Button>
                        <Button variant="outline-success" size="sm" className="flex-fill">
                          <i className="fas fa-eye me-2"></i>
                          مشاهده
                        </Button>
                      </div>
                    </div>
                    ))
                  )}
                </div>
              </Card.Body>
            </Card>
          </Tab>

          {/* Content Management Tab */}
          <Tab eventKey="content" title="مدیریت محتوا">
            <Row>
              <Col xl={4} lg={6} md={6} sm={12} className="mb-3">
                <Card className="content-management-card h-100">
                  <Card.Body className="text-center">
                    <i className="fas fa-blog text-primary content-icon"></i>
                    <h5>مدیریت وبلاگ</h5>
                    <p className="text-muted">مدیریت مقالات و پست‌های وبلاگ</p>
                    <Button variant="primary" className="w-100">
                      <i className="fas fa-edit me-2"></i>
                      مدیریت وبلاگ
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
              <Col xl={4} lg={6} md={6} sm={12} className="mb-3">
                <Card className="content-management-card h-100">
                  <Card.Body className="text-center">
                    <i className="fas fa-graduation-cap text-success content-icon"></i>
                    <h5>مدیریت بسته‌های آموزشی</h5>
                    <p className="text-muted">افزودن و ویرایش بسته‌های آموزشی</p>
                    <Button variant="success" className="w-100">
                      <i className="fas fa-plus me-2"></i>
                      افزودن بسته آموزشی
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
              <Col xl={4} lg={6} md={6} sm={12} className="mb-3">
                <Card className="content-management-card h-100">
                  <Card.Body className="text-center">
                    <i className="fas fa-clipboard-list text-warning content-icon"></i>
                    <h5>مدیریت تست‌ها</h5>
                    <p className="text-muted">ایجاد و مدیریت تست‌های روانشناختی</p>
                    <Button variant="warning" className="w-100">
                      <i className="fas fa-plus me-2"></i>
                      افزودن تست
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Tab>
        </Tabs>
      </Container>
    </>
  );
};

export default AdminDashboard;
