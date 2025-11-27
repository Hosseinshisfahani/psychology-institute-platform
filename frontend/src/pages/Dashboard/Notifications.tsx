import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Badge, ListGroup, Dropdown, Form } from 'react-bootstrap';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';
import axios from 'axios';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  is_read: boolean;
  created_at: string;
  created_at_persian: string;
  action_url?: string;
}

const Notifications: React.FC = () => {
  const { user } = useAuth();
  const { t } = useI18n();
  const queryClient = useQueryClient();
  
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');

  // Fetch notifications
  const { data: notifications = [], isLoading } = useQuery<Notification[]>({
    queryKey: ['notifications', filter],
    queryFn: async () => {
      const params = filter !== 'all' ? `?filter=${filter}` : '';
      const response = await axios.get(`/api/dashboard/notifications/${params}`);
      return response.data.results || [];
    },
  });

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      await axios.patch(`/api/dashboard/notifications/${notificationId}/`, { is_read: true });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  // Mark all as read mutation
  const markAllAsReadMutation = useMutation({
    mutationFn: async () => {
      await axios.post('/api/dashboard/notifications/mark-all-read/');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  // Delete notification mutation
  const deleteNotificationMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      await axios.delete(`/api/dashboard/notifications/${notificationId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return 'fas fa-check-circle text-success';
      case 'warning':
        return 'fas fa-exclamation-triangle text-warning';
      case 'error':
        return 'fas fa-times-circle text-danger';
      default:
        return 'fas fa-info-circle text-primary';
    }
  };

  const getNotificationVariant = (type: string) => {
    switch (type) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'danger';
      default:
        return 'primary';
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  if (isLoading) {
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
        <title>اعلان‌ها - {user?.full_name}</title>
        <meta name="description" content="مشاهده و مدیریت اعلان‌های حساب کاربری" />
      </Helmet>

      <Container className="py-4">
        <Row>
          <Col lg={8} className="mx-auto">
            {/* Header */}
            <div className="d-flex align-items-center justify-content-between mb-4">
              <div className="d-flex align-items-center">
                <i className="fas fa-bell me-3 text-primary fs-3"></i>
                <h2 className="mb-0">اعلان‌ها</h2>
                {unreadCount > 0 && (
                  <Badge bg="danger" className="ms-2">
                    {unreadCount}
                  </Badge>
                )}
              </div>
              
              <div className="d-flex gap-2">
                {unreadCount > 0 && (
                  <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={() => markAllAsReadMutation.mutate()}
                    disabled={markAllAsReadMutation.isPending}
                  >
                    <i className="fas fa-check-double me-2"></i>
                    همه را خوانده
                  </Button>
                )}
                
                <Dropdown>
                  <Dropdown.Toggle variant="outline-secondary" size="sm">
                    <i className="fas fa-filter me-2"></i>
                    فیلتر
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item 
                      active={filter === 'all'}
                      onClick={() => setFilter('all')}
                    >
                      همه
                    </Dropdown.Item>
                    <Dropdown.Item 
                      active={filter === 'unread'}
                      onClick={() => setFilter('unread')}
                    >
                      خوانده نشده
                    </Dropdown.Item>
                    <Dropdown.Item 
                      active={filter === 'read'}
                      onClick={() => setFilter('read')}
                    >
                      خوانده شده
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </div>

            {/* Notifications List */}
            {notifications.length === 0 ? (
              <Card>
                <Card.Body className="text-center py-5">
                  <i className="fas fa-bell-slash text-muted mb-3" style={{ fontSize: '3rem' }}></i>
                  <h5 className="text-muted">اعلانی وجود ندارد</h5>
                  <p className="text-muted">
                    {filter === 'unread' 
                      ? 'شما اعلان خوانده نشده‌ای ندارید'
                      : 'هنوز اعلانی دریافت نکرده‌اید'
                    }
                  </p>
                </Card.Body>
              </Card>
            ) : (
              <ListGroup>
                {notifications.map((notification) => (
                  <ListGroup.Item
                    key={notification.id}
                    className={`p-0 ${!notification.is_read ? 'border-start border-primary border-3' : ''}`}
                  >
                    <Card className={`border-0 ${!notification.is_read ? 'bg-light' : ''}`}>
                      <Card.Body>
                        <div className="d-flex align-items-start">
                          <div className="me-3 mt-1">
                            <i className={getNotificationIcon(notification.type)}></i>
                          </div>
                          
                          <div className="flex-grow-1">
                            <div className="d-flex justify-content-between align-items-start mb-2">
                              <h6 className="mb-1">{notification.title}</h6>
                              <div className="d-flex align-items-center gap-2">
                                <small className="text-muted">
                                  {notification.created_at_persian}
                                </small>
                                <Dropdown>
                                  <Dropdown.Toggle 
                                    variant="link" 
                                    size="sm" 
                                    className="p-0 text-muted"
                                    style={{ border: 'none', fontSize: '0.8rem' }}
                                  >
                                    <i className="fas fa-ellipsis-v"></i>
                                  </Dropdown.Toggle>
                                  <Dropdown.Menu>
                                    {!notification.is_read && (
                                      <Dropdown.Item
                                        onClick={() => markAsReadMutation.mutate(notification.id)}
                                      >
                                        <i className="fas fa-check me-2"></i>
                                        علامت‌گذاری به عنوان خوانده شده
                                      </Dropdown.Item>
                                    )}
                                    <Dropdown.Item
                                      className="text-danger"
                                      onClick={() => deleteNotificationMutation.mutate(notification.id)}
                                    >
                                      <i className="fas fa-trash me-2"></i>
                                      حذف
                                    </Dropdown.Item>
                                  </Dropdown.Menu>
                                </Dropdown>
                              </div>
                            </div>
                            
                            <p className="mb-2 text-muted">{notification.message}</p>
                            
                            <div className="d-flex justify-content-between align-items-center">
                              <Badge bg={getNotificationVariant(notification.type)}>
                                {notification.type === 'info' && 'اطلاعات'}
                                {notification.type === 'success' && 'موفقیت'}
                                {notification.type === 'warning' && 'هشدار'}
                                {notification.type === 'error' && 'خطا'}
                              </Badge>
                              
                              {notification.action_url && (
                                <Button
                                  variant="outline-primary"
                                  size="sm"
                                  onClick={() => {
                                    if (!notification.is_read) {
                                      markAsReadMutation.mutate(notification.id);
                                    }
                                    window.location.href = notification.action_url!;
                                  }}
                                >
                                  مشاهده
                                  <i className="fas fa-external-link-alt ms-2"></i>
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            )}

            {/* Load More Button */}
            {notifications.length >= 20 && (
              <div className="text-center mt-4">
                <Button variant="outline-primary">
                  نمایش بیشتر
                </Button>
              </div>
            )}
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Notifications;
