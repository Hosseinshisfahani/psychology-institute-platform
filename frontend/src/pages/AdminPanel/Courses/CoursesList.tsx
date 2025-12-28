import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  IconButton,
  MenuItem,
  TextField,
  Tooltip,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Avatar,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { useSnackbar } from 'notistack';
import { useAuth } from '../../../contexts/AuthContext';
import { useLocation } from 'react-router-dom';
import CourseCommentsModeration from './CourseCommentsModeration';

interface Course {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  instructor: {
    id: number;
    full_name: string;
  };
  category: {
    id: number;
    name: string;
  };
  difficulty: string;
  status: string;
  price: number;
  discount_price?: number;
  thumbnail?: string;
  enrollment_count?: number;
  created_at: string;
}

const CoursesList: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const { user, isLoading: authLoading } = useAuth();
  const location = useLocation();
  
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    difficulty: '',
    category: '',
  });
  const [activeTab, setActiveTab] = useState(0);

  // Check if we're on an admin route
  const isAdminRoute = location.pathname.startsWith('/admin-panel');
  
  // Check if user is admin (only after auth is loaded)
  const isAdmin = !authLoading && (user?.user_type === 'admin' || user?.is_staff);
  
  // Only enable query if we're on admin route AND user is admin
  const shouldFetch = isAdminRoute && isAdmin;

  // Fetch courses - only if user is admin, auth is loaded, and we're on admin route
  const { data: courses = [], isLoading, error: queryError } = useQuery({
    queryKey: ['admin-courses-list', filters, user?.id], // Include user ID to make query user-specific
    queryFn: async () => {
      // Double-check conditions before making the request
      if (!isAdminRoute || !isAdmin) {
        throw new Error('Unauthorized');
      }
      
      const params = new URLSearchParams({
        ...(filters.search && { search: filters.search }),
        ...(filters.status && { status: filters.status }),
        ...(filters.difficulty && { difficulty: filters.difficulty }),
        ...(filters.category && { category: filters.category }),
      });
      const response = await axios.get(`/api/admin/courses/?${params}`);
      return response.data.results || response.data;
    },
    enabled: shouldFetch, // Only execute query if conditions are met
    retry: false, // Don't retry on 403 errors
  });

  // Handle query errors (React Query v5 doesn't support onError in useQuery)
  useEffect(() => {
    if (queryError) {
      const error = queryError as any;
      // Silently handle 403 and unauthorized errors
      if (error?.response?.status === 403 || error?.message === 'Unauthorized') {
        return; // Don't show error for permission issues
      }
      enqueueSnackbar('خطا در بارگذاری دوره‌های آموزشی', { variant: 'error' });
    }
  }, [queryError, enqueueSnackbar]);

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (courseId: number) => {
      const response = await axios.delete(`/api/admin/courses/${courseId}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-courses-list'] });
      enqueueSnackbar('دوره آموزشی با موفقیت حذف شد', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('خطا در حذف دوره آموزشی', { variant: 'error' });
    },
  });

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fa-IR').format(price);
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, any> = {
      published: 'success',
      draft: 'warning',
      archived: 'default',
    };
    return colors[status] || 'default';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      published: 'منتشر شده',
      draft: 'پیش‌نویس',
      archived: 'بایگانی شده',
    };
    return labels[status] || status;
  };

  const getDifficultyLabel = (difficulty: string) => {
    const labels: Record<string, string> = {
      beginner: 'مبتدی',
      intermediate: 'متوسط',
      advanced: 'پیشرفته',
    };
    return labels[difficulty] || difficulty;
  };

  const handleDelete = (courseId: number) => {
    if (window.confirm('آیا از حذف این دوره آموزشی اطمینان دارید؟')) {
      deleteMutation.mutate(courseId);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            مدیریت دوره‌های آموزشی
          </Typography>
          <Typography variant="body1" color="text.secondary">
            مشاهده و مدیریت دوره‌های آموزشی
          </Typography>
        </Box>
        {activeTab === 0 && (
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            size="large"
            onClick={() => {
              const apiUrl = process.env.REACT_APP_API_URL || 'https://sarmadclinic.ir';
              window.location.href = `${apiUrl}/admin/courses/course/add/`;
            }}
          >
            افزودن دوره جدید
          </Button>
        )}
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="لیست دوره‌ها" />
          <Tab label="مدیریت نظرات" />
        </Tabs>
      </Box>

      {activeTab === 1 && <CourseCommentsModeration />}
      {activeTab === 0 && (
        <>
      {/* Filters */}
      <Box sx={{ mb: 3, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(4, 1fr)' }, gap: 2 }}>
        <TextField
          id="search-filter"
          fullWidth
          placeholder="جستجو بر اساس عنوان..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <TextField
          id="status-filter"
          fullWidth
          select
          label="وضعیت"
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
        >
          <MenuItem value="">همه</MenuItem>
          <MenuItem value="published">منتشر شده</MenuItem>
          <MenuItem value="draft">پیش‌نویس</MenuItem>
          <MenuItem value="archived">بایگانی شده</MenuItem>
        </TextField>
        <TextField
          id="difficulty-filter"
          fullWidth
          select
          label="سطح دشواری"
          value={filters.difficulty}
          onChange={(e) => setFilters({ ...filters, difficulty: e.target.value })}
        >
          <MenuItem value="">همه</MenuItem>
          <MenuItem value="beginner">مبتدی</MenuItem>
          <MenuItem value="intermediate">متوسط</MenuItem>
          <MenuItem value="advanced">پیشرفته</MenuItem>
        </TextField>
        <TextField
          id="category-filter"
          fullWidth
          select
          label="دسته‌بندی"
          value={filters.category}
          onChange={(e) => setFilters({ ...filters, category: e.target.value })}
        >
          <MenuItem value="">همه</MenuItem>
        </TextField>
      </Box>

      {/* Courses Grid */}
      {isLoading ? (
        <Typography>در حال بارگذاری...</Typography>
      ) : courses.length === 0 ? (
        <Typography align="center" color="text.secondary" sx={{ py: 4 }}>
          هیچ دوره آموزشی‌ای یافت نشد
        </Typography>
      ) : (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
          {courses.map((course: Course) => (
            <Box key={course.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 8,
                  },
                }}
              >
                <CardMedia
                  component="img"
                  height="200"
                  image={course.thumbnail || '/static/images/course-placeholder.png'}
                  alt={course.title}
                  loading="lazy"
                  sx={{ objectFit: 'cover' }}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <Chip
                      label={getStatusLabel(course.status)}
                      color={getStatusColor(course.status)}
                      size="small"
                    />
                    <Chip
                      label={getDifficultyLabel(course.difficulty)}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                  <Typography gutterBottom variant="h6" component="div" sx={{ fontWeight: 600 }}>
                    {course.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {course.short_description?.substring(0, 100)}
                    {course.short_description?.length > 100 ? '...' : ''}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Avatar sx={{ width: 24, height: 24, fontSize: '0.875rem' }}>
                      {course.instructor?.full_name?.charAt(0) || 'M'}
                    </Avatar>
                    <Typography variant="body2" color="text.secondary">
                      {course.instructor?.full_name || 'بدون مدرس'}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PeopleIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      {course.enrollment_count || 0} دانشجو
                    </Typography>
                  </Box>
                  <Typography variant="h6" color="primary" sx={{ mt: 2, fontWeight: 700 }}>
                    {course.discount_price ? (
                      <>
                        <Typography
                          component="span"
                          variant="body2"
                          sx={{ textDecoration: 'line-through', ml: 1, color: 'text.secondary' }}
                        >
                          {formatPrice(course.price)}
                        </Typography>
                        {formatPrice(course.discount_price)} تومان
                      </>
                    ) : (
                      `${formatPrice(course.price)} تومان`
                    )}
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <Tooltip title="مشاهده">
                      <IconButton size="small" color="info">
                        <ViewIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <IconButton size="small" color="primary">
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="حذف">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(course.id)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </CardActions>
              </Card>
            </Box>
          ))}
        </Box>
      )}
        </>
      )}
    </Box>
  );
};

export default CoursesList;

