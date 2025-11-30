import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Chip,
  IconButton,
  Button,
  Menu,
  MenuItem,
  Divider,
  CircularProgress,
  Alert,
  Stack,
  Tooltip,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  Pagination,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  MoreVert as MoreVertIcon,
  MarkEmailRead as MarkReadIcon,
  MarkEmailUnread as MarkUnreadIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircleOutline as SuccessIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import { Helmet } from 'react-helmet-async';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://185.8.175.241:8000';

interface Notification {
  id: number;
  user: number;
  user_name: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  is_read: boolean;
  created_at: string;
  created_at_persian: string;
}

const NotificationsList: React.FC = () => {
  const theme = useTheme();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();

  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');
  const [selectedNotifications, setSelectedNotifications] = useState<number[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);

  // Helper function to get CSRF token
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

  // Fetch notifications
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['adminNotifications', page, filter],
    queryFn: async () => {
      const csrfToken = getCsrfToken();
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '20',
      });
      
      if (filter === 'unread') {
        params.append('is_read', 'false');
      } else if (filter === 'read') {
        params.append('is_read', 'true');
      }

      const response = await axios.get(`${API_BASE_URL}/api/admin/notifications/?${params}`, {
        withCredentials: true,
        headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
      });

      // Handle both paginated and non-paginated responses
      if (Array.isArray(response.data)) {
        return {
          results: response.data,
          count: response.data.length,
          next: null,
          previous: null,
        };
      }
      return response.data;
    },
  });

  const notifications: Notification[] = data?.results || [];
  const totalCount = data?.count || 0;
  const totalPages = Math.ceil(totalCount / 20);

  // Mark as read mutation
  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      const csrfToken = getCsrfToken();
      await axios.patch(
        `${API_BASE_URL}/api/admin/notifications/${notificationId}/read/`,
        {},
        {
          withCredentials: true,
          headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminNotifications'] });
      queryClient.invalidateQueries({ queryKey: ['adminNotificationCount'] });
      enqueueSnackbar('اعلان به عنوان خوانده شده علامت گذاری شد', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('خطا در علامت گذاری اعلان', { variant: 'error' });
    },
  });

  // Mark as unread mutation
  const markAsUnreadMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      const csrfToken = getCsrfToken();
      await axios.patch(
        `${API_BASE_URL}/api/admin/notifications/${notificationId}/unread/`,
        {},
        {
          withCredentials: true,
          headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminNotifications'] });
      queryClient.invalidateQueries({ queryKey: ['adminNotificationCount'] });
      enqueueSnackbar('اعلان به عنوان خوانده نشده علامت گذاری شد', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('خطا در علامت گذاری اعلان', { variant: 'error' });
    },
  });

  // Mark all as read mutation
  const markAllAsReadMutation = useMutation({
    mutationFn: async () => {
      const csrfToken = getCsrfToken();
      await axios.post(
        `${API_BASE_URL}/api/admin/notifications/mark-all-read/`,
        {},
        {
          withCredentials: true,
          headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
        }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminNotifications'] });
      queryClient.invalidateQueries({ queryKey: ['adminNotificationCount'] });
      setSelectedNotifications([]);
      enqueueSnackbar('همه اعلان‌ها به عنوان خوانده شده علامت گذاری شدند', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('خطا در علامت گذاری اعلان‌ها', { variant: 'error' });
    },
  });

  // Delete notification mutation
  const deleteMutation = useMutation({
    mutationFn: async (notificationId: number) => {
      const csrfToken = getCsrfToken();
      await axios.delete(`${API_BASE_URL}/api/admin/notifications/${notificationId}/delete/`, {
        withCredentials: true,
        headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminNotifications'] });
      queryClient.invalidateQueries({ queryKey: ['adminNotificationCount'] });
      enqueueSnackbar('اعلان با موفقیت حذف شد', { variant: 'success' });
      setAnchorEl(null);
      setSelectedNotification(null);
    },
    onError: () => {
      enqueueSnackbar('خطا در حذف اعلان', { variant: 'error' });
    },
  });

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, notification: Notification) => {
    setAnchorEl(event.currentTarget);
    setSelectedNotification(notification);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedNotification(null);
  };

  const handleMarkAsRead = () => {
    if (selectedNotification) {
      markAsReadMutation.mutate(selectedNotification.id);
    }
    handleMenuClose();
  };

  const handleMarkAsUnread = () => {
    if (selectedNotification) {
      markAsUnreadMutation.mutate(selectedNotification.id);
    }
    handleMenuClose();
  };

  const handleDelete = () => {
    if (selectedNotification) {
      deleteMutation.mutate(selectedNotification.id);
    }
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedNotifications(notifications.map((n) => n.id));
    } else {
      setSelectedNotifications([]);
    }
  };

  const handleSelectNotification = (notificationId: number) => {
    setSelectedNotifications((prev) =>
      prev.includes(notificationId)
        ? prev.filter((id) => id !== notificationId)
        : [...prev, notificationId]
    );
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <SuccessIcon sx={{ color: theme.palette.success.main }} />;
      case 'warning':
        return <WarningIcon sx={{ color: theme.palette.warning.main }} />;
      case 'error':
        return <ErrorIcon sx={{ color: theme.palette.error.main }} />;
      default:
        return <InfoIcon sx={{ color: theme.palette.info.main }} />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success':
        return theme.palette.success.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'error':
        return theme.palette.error.main;
      default:
        return theme.palette.info.main;
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <>
      <Helmet>
        <title>اعلان‌ها - پنل مدیریت</title>
      </Helmet>

      <Box>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <NotificationsIcon sx={{ fontSize: 32, color: theme.palette.primary.main }} />
              <Typography variant="h4" component="h1" fontWeight={600}>
                اعلان‌ها
              </Typography>
              {unreadCount > 0 && (
                <Chip
                  label={`${unreadCount} خوانده نشده`}
                  color="error"
                  size="small"
                  sx={{ fontWeight: 600 }}
                />
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="بروزرسانی">
                <IconButton onClick={() => refetch()} color="primary">
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              {unreadCount > 0 && (
                <Button
                  variant="outlined"
                  startIcon={<CheckCircleIcon />}
                  onClick={() => markAllAsReadMutation.mutate()}
                  disabled={markAllAsReadMutation.isPending}
                  size="small"
                >
                  همه را خوانده شده
                </Button>
              )}
            </Box>
          </Box>

          {/* Filters */}
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <FilterIcon color="action" />
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>فیلتر</InputLabel>
              <Select
                value={filter}
                label="فیلتر"
                onChange={(e) => {
                  setFilter(e.target.value as 'all' | 'unread' | 'read');
                  setPage(1);
                }}
              >
                <MenuItem value="all">همه</MenuItem>
                <MenuItem value="unread">خوانده نشده</MenuItem>
                <MenuItem value="read">خوانده شده</MenuItem>
              </Select>
            </FormControl>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
              {totalCount} اعلان
            </Typography>
          </Paper>
        </Box>

        {/* Notifications List */}
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            خطا در بارگذاری اعلان‌ها
          </Alert>
        ) : notifications.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <NotificationsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              اعلانی یافت نشد
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {filter === 'unread'
                ? 'هیچ اعلان خوانده نشده‌ای وجود ندارد'
                : filter === 'read'
                ? 'هیچ اعلان خوانده شده‌ای وجود ندارد'
                : 'هنوز اعلانی ایجاد نشده است'}
            </Typography>
          </Paper>
        ) : (
          <Stack spacing={2}>
            {notifications.map((notification) => (
              <Card
                key={notification.id}
                sx={{
                  transition: 'all 0.2s',
                  borderLeft: `4px solid ${getNotificationColor(notification.type)}`,
                  backgroundColor: notification.is_read
                    ? 'background.paper'
                    : alpha(theme.palette.primary.main, 0.05),
                  '&:hover': {
                    boxShadow: theme.shadows[4],
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                    <Checkbox
                      checked={selectedNotifications.includes(notification.id)}
                      onChange={() => handleSelectNotification(notification.id)}
                      size="small"
                      sx={{ mt: 0.5 }}
                    />
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                          {getNotificationIcon(notification.type)}
                          <Typography
                            variant="h6"
                            component="h3"
                            sx={{
                              fontWeight: notification.is_read ? 400 : 600,
                              color: notification.is_read ? 'text.secondary' : 'text.primary',
                            }}
                          >
                            {notification.title}
                          </Typography>
                          {!notification.is_read && (
                            <Chip
                              label="جدید"
                              size="small"
                              color="primary"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                          )}
                        </Box>
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuOpen(e, notification)}
                          sx={{ ml: 1 }}
                        >
                          <MoreVertIcon />
                        </IconButton>
                      </Box>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 1.5, whiteSpace: 'pre-wrap' }}
                      >
                        {notification.message}
                      </Typography>

                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          {notification.user_name && (
                            <Chip
                              label={notification.user_name}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.75rem' }}
                            />
                          )}
                          <Chip
                            label={notification.type}
                            size="small"
                            sx={{
                              fontSize: '0.75rem',
                              backgroundColor: alpha(getNotificationColor(notification.type), 0.1),
                              color: getNotificationColor(notification.type),
                            }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {notification.created_at_persian || notification.created_at}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}

            {/* Pagination */}
            {totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Pagination
                  count={totalPages}
                  page={page}
                  onChange={(_, value) => setPage(value)}
                  color="primary"
                  size="large"
                />
              </Box>
            )}
          </Stack>
        )}

        {/* Action Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          {selectedNotification && (
            <>
              {selectedNotification.is_read ? (
                <MenuItem onClick={handleMarkAsUnread}>
                  <MarkUnreadIcon sx={{ mr: 1, fontSize: 20 }} />
                  علامت به عنوان خوانده نشده
                </MenuItem>
              ) : (
                <MenuItem onClick={handleMarkAsRead}>
                  <MarkReadIcon sx={{ mr: 1, fontSize: 20 }} />
                  علامت به عنوان خوانده شده
                </MenuItem>
              )}
              <Divider />
              <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
                <DeleteIcon sx={{ mr: 1, fontSize: 20 }} />
                حذف
              </MenuItem>
            </>
          )}
        </Menu>
      </Box>
    </>
  );
};

export default NotificationsList;

