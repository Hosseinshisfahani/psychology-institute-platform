import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Breadcrumbs,
  Link,
  Badge,
  useTheme,
  alpha,
  Popover,
  Paper,
  ListItemAvatar,
  CircularProgress,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  School as SchoolIcon,
  Article as ArticleIcon,
  Event as EventIcon,
  WorkOutline as WorkshopIcon,
  Psychology as TestIcon,
  Payment as PaymentIcon,
  Analytics as AnalyticsIcon,
  Chat as ChatIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Inventory2 as PackageIcon,
  Brightness4,
  Brightness7,
  NavigateNext,
  Home,
  AccountCircle,
  Logout,
  Person,
} from '@mui/icons-material';
import { useAdminTheme } from '../../contexts/AdminThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const drawerWidth = 280;

interface MenuItem {
  title: string;
  path: string;
  icon: React.ReactElement;
}

const menuItems: MenuItem[] = [
  { title: 'داشبورد', path: '/admin-panel', icon: <DashboardIcon /> },
  { title: 'کاربران', path: '/admin-panel/users', icon: <PeopleIcon /> },
  { title: 'دوره‌های آموزشی', path: '/admin-panel/courses', icon: <SchoolIcon /> },
  { title: 'پکیج‌ها', path: '/admin-panel/packages', icon: <PackageIcon /> },
  { title: 'بلاگ', path: '/admin-panel/blog', icon: <ArticleIcon /> },
  { title: 'سیستم نوبت دهی', path: '/admin-panel/appointments', icon: <EventIcon /> },
  { title: 'کارگاه‌ها', path: '/admin-panel/workshops', icon: <WorkshopIcon /> },
  { title: 'تست‌های روانشناختی', path: '/admin-panel/tests', icon: <TestIcon /> },
  { title: 'پرداخت‌ها', path: '/admin-panel/payments', icon: <PaymentIcon /> },
  { title: 'مدیریت گفتگوها', path: '/admin-panel/chat', icon: <ChatIcon /> },
  { title: 'تحلیل و گزارش', path: '/admin-panel/analytics', icon: <AnalyticsIcon /> },
  { title: 'تنظیمات', path: '/admin-panel/settings', icon: <SettingsIcon /> },
];

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const AdminLayout: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { mode, toggleTheme } = useAdminTheme();
  const { user, logout } = useAuth();
  const queryClient = useQueryClient();
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationAnchorEl, setNotificationAnchorEl] = useState<null | HTMLElement>(null);

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

  // Fetch unread notification count
  const { data: notificationCount = 0, refetch: refetchNotificationCount } = useQuery<number>({
    queryKey: ['adminNotificationCount'],
    queryFn: async () => {
      const csrfToken = getCsrfToken();
      const response = await axios.get(`${API_BASE_URL}/api/admin/notifications/count/`, {
        withCredentials: true,
        headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
      });
      return response.data.unread_count || 0;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Fetch recent notifications
  const { data: notifications = [], isLoading: notificationsLoading } = useQuery({
    queryKey: ['adminNotifications'],
    queryFn: async () => {
      const csrfToken = getCsrfToken();
      const response = await axios.get(`${API_BASE_URL}/api/admin/notifications/`, {
        withCredentials: true,
        headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
        params: { limit: 10 },
      });
      // Handle both paginated and non-paginated responses
      if (Array.isArray(response.data)) {
        return response.data;
      }
      return response.data.results || [];
    },
    enabled: Boolean(notificationAnchorEl), // Only fetch when dropdown is open
  });

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setNotificationAnchorEl(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    handleProfileMenuClose();
  };

  // Generate breadcrumbs from current path
  const generateBreadcrumbs = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    const breadcrumbs = [
      <Link
        key="home"
        component={RouterLink}
        to="/"
        underline="hover"
        color="inherit"
        sx={{ display: 'flex', alignItems: 'center' }}
      >
        <Home sx={{ mr: 0.5 }} fontSize="small" />
        خانه
      </Link>,
    ];

    let currentPath = '';
    paths.forEach((path, index) => {
      currentPath += `/${path}`;
      const menuItem = menuItems.find((item) => item.path === currentPath);
      const label = menuItem?.title || path;

      if (index === paths.length - 1) {
        breadcrumbs.push(
          <Typography key={currentPath} color="text.primary">
            {label}
          </Typography>
        );
      } else {
        breadcrumbs.push(
          <Link
            key={currentPath}
            component={RouterLink}
            to={currentPath}
            underline="hover"
            color="inherit"
          >
            {label}
          </Link>
        );
      }
    });

    return breadcrumbs;
  };

  const drawer = (
    <Box>
      <Toolbar
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 2,
        }}
      >
        <DashboardIcon sx={{ fontSize: 32, ml: 1 }} />
        <Typography variant="h6" noWrap component="div" fontWeight="bold">
          پنل مدیریت
        </Typography>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1, py: 2 }}>
        {menuItems.map((item) => {
          const isSelected = location.pathname === item.path;
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                selected={isSelected}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    color: theme.palette.primary.main,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.15),
                    },
                    '& .MuiListItemIcon-root': {
                      color: theme.palette.primary.main,
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isSelected ? theme.palette.primary.main : 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.title}
                  primaryTypographyProps={{
                    fontSize: '0.95rem',
                    fontWeight: isSelected ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }}>
            <Breadcrumbs
              separator={<NavigateNext fontSize="small" />}
              aria-label="breadcrumb"
            >
              {generateBreadcrumbs()}
            </Breadcrumbs>
          </Box>

          <IconButton onClick={toggleTheme} color="inherit" sx={{ ml: 1 }}>
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>

          <IconButton 
            onClick={handleNotificationMenuOpen}
            color="inherit" 
            sx={{ ml: 1 }}
          >
            <Badge badgeContent={notificationCount > 0 ? notificationCount : undefined} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <Popover
            open={Boolean(notificationAnchorEl)}
            anchorEl={notificationAnchorEl}
            onClose={handleNotificationMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            PaperProps={{
              sx: {
                width: 360,
                maxHeight: 500,
                mt: 1,
              },
            }}
          >
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                اعلان‌ها
              </Typography>
            </Box>
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              {notificationsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : notifications.length === 0 ? (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    اعلانی وجود ندارد
                  </Typography>
                </Box>
              ) : (
                <List sx={{ p: 0 }}>
                  {notifications.map((notification: any) => (
                    <ListItem
                      key={notification.id}
                      sx={{
                        borderBottom: 1,
                        borderColor: 'divider',
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.primary.main, 0.05),
                        },
                      }}
                    >
                      <ListItemButton
                        onClick={() => {
                          handleNotificationMenuClose();
                          // Navigate to notifications page or handle click
                        }}
                      >
                        <ListItemText
                          primary={notification.title}
                          secondary={
                            <Box>
                              <Typography variant="caption" color="text.secondary" display="block">
                                {notification.message}
                              </Typography>
                              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                                {notification.created_at_persian || notification.created_at}
                              </Typography>
                            </Box>
                          }
                        />
                        {!notification.is_read && (
                          <Box
                            sx={{
                              width: 8,
                              height: 8,
                              borderRadius: '50%',
                              bgcolor: 'primary.main',
                              ml: 1,
                            }}
                          />
                        )}
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
            {notifications.length > 0 && (
              <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
                <Link
                  component="button"
                  variant="body2"
                  onClick={() => {
                    handleNotificationMenuClose();
                    navigate('/admin-panel/notifications');
                  }}
                  sx={{ cursor: 'pointer' }}
                >
                  مشاهده همه اعلان‌ها
                </Link>
              </Box>
            )}
          </Popover>

          <IconButton
            onClick={handleProfileMenuOpen}
            sx={{ ml: 1 }}
            color="inherit"
          >
            <Avatar
              sx={{
                width: 36,
                height: 36,
                bgcolor: theme.palette.primary.main,
              }}
            >
              {user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'A'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={() => { navigate('/dashboard/profile'); handleProfileMenuClose(); }}>
              <ListItemIcon>
                <Person fontSize="small" />
              </ListItemIcon>
              <ListItemText>پروفایل</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => { navigate('/dashboard/settings'); handleProfileMenuClose(); }}>
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>تنظیمات</ListItemText>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              <ListItemText>خروج</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              borderRight: 'none',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
          backgroundColor: theme.palette.background.default,
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};

export default AdminLayout;

