import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Avatar,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  ArrowBack as BackIcon,
  School as SchoolIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
  Schedule as ScheduleIcon,
  Star as StarIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useSnackbar } from 'notistack';

interface Package {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  category: {
    id: number;
    name: string;
    color: string;
  };
  status: string;
  price: number;
  discount_price?: number;
  current_price: number;
  discount_percentage: number;
  is_featured: boolean;
  duration_months: number;
  language: string;
  prerequisites: string;
  learning_objectives: string;
  thumbnail?: string;
  intro_video?: string;
  total_courses: number;
  total_hours: number;
  original_total_price: number;
  savings_amount: number;
  savings_percentage: number;
  purchase_count: number;
  revenue: number;
  rating: number;
  review_count: number;
  meta_title?: string;
  meta_description?: string;
  courses: Array<{
    id: number;
    title: string;
    instructor_name: string;
    current_price: number;
    thumbnail?: string;
    difficulty: string;
    duration_hours: number;
  }>;
  created_at: string;
  created_at_persian: string;
  updated_at: string;
  updated_at_persian: string;
  published_at?: string;
  published_at_persian?: string;
}

const PackageDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  
  const [deleteDialog, setDeleteDialog] = useState(false);

  // Fetch package data
  const { data: packageData, isLoading } = useQuery({
    queryKey: ['admin-package', id],
    queryFn: async () => {
      const response = await axios.get(`/api/admin/packages/${id}/`);
      return response.data;
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.delete(`/api/admin/packages/${id}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-packages'] });
      enqueueSnackbar('پکیج با موفقیت حذف شد', { variant: 'success' });
      navigate('/admin-panel/packages');
    },
    onError: () => {
      enqueueSnackbar('خطا در حذف پکیج', { variant: 'error' });
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

  const handleDelete = () => {
    deleteMutation.mutate();
    setDeleteDialog(false);
  };

  if (isLoading) {
    return <Typography>در حال بارگذاری...</Typography>;
  }

  if (!packageData) {
    return <Typography>پکیج یافت نشد</Typography>;
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          startIcon={<BackIcon />}
          onClick={() => navigate('/admin-panel/packages')}
        >
          بازگشت
        </Button>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          {packageData.title}
        </Typography>
        <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => navigate(`/admin-panel/packages/${id}/edit`)}
          >
            ویرایش
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={() => setDeleteDialog(true)}
          >
            حذف
          </Button>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
        {/* Main Content */}
        <Box sx={{ flex: { xs: '1', md: '2' } }}>
          {/* Package Info */}
          <Card sx={{ mb: 3 }}>
            <CardMedia
              component="img"
              height="300"
              image={packageData.thumbnail || '/static/images/package-placeholder.png'}
              alt={packageData.title}
              loading="lazy"
              sx={{ objectFit: 'cover' }}
            />
            <CardContent>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip
                  label={getStatusLabel(packageData.status)}
                  color={getStatusColor(packageData.status)}
                />
                {packageData.is_featured && (
                  <Chip label="ویژه" color="secondary" />
                )}
                <Chip
                  label={packageData.category?.name || 'بدون دسته‌بندی'}
                  sx={{ backgroundColor: packageData.category?.color || '#007bff', color: 'white' }}
                />
              </Box>
              
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 2 }}>
                {packageData.title}
              </Typography>
              
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                {packageData.description}
              </Typography>

              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(4, 1fr)' }, gap: 2, mb: 3 }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    {packageData.total_courses}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    دوره
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    {packageData.total_hours}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ساعت
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    {packageData.purchase_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    خرید
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    {packageData.rating.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    امتیاز
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" sx={{ mb: 2 }}>
                اهداف یادگیری
              </Typography>
              <Typography variant="body2" sx={{ mb: 3 }}>
                {packageData.learning_objectives}
              </Typography>

              {packageData.prerequisites && (
                <>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    پیش‌نیازها
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 3 }}>
                    {packageData.prerequisites}
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>

          {/* Courses */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3 }}>
                دوره‌های پکیج ({packageData.courses.length})
              </Typography>
              
              {packageData.courses.length > 0 ? (
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 2 }}>
                  {packageData.courses.map((course: any) => (
                    <Paper key={course.id} sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar src={course.thumbnail} sx={{ width: 50, height: 50 }}>
                        <SchoolIcon />
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {course.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {course.instructor_name}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                          <Chip
                            label={getDifficultyLabel(course.difficulty)}
                            size="small"
                            variant="outlined"
                          />
                          <Typography variant="body2" color="text.secondary">
                            {course.duration_hours} ساعت
                          </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ textAlign: 'left' }}>
                        <Typography variant="h6" color="primary">
                          {formatPrice(course.current_price)} تومان
                        </Typography>
                      </Box>
                    </Paper>
                  ))}
                </Box>
              ) : (
                <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
                  هیچ دوره‌ای در این پکیج وجود ندارد
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Sidebar */}
        <Box sx={{ flex: { xs: '1', md: '1' } }}>
          {/* Pricing */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                قیمت‌گذاری
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="h4" color="primary" sx={{ fontWeight: 700 }}>
                  {packageData.discount_price ? (
                    <>
                      <Typography
                        component="span"
                        variant="h6"
                        sx={{ textDecoration: 'line-through', ml: 1, color: 'text.secondary' }}
                      >
                        {formatPrice(packageData.price)}
                      </Typography>
                      {formatPrice(packageData.discount_price)} تومان
                    </>
                  ) : (
                    `${formatPrice(packageData.price)} تومان`
                  )}
                </Typography>
                {packageData.discount_percentage > 0 && (
                  <Chip
                    label={`${packageData.discount_percentage}% تخفیف`}
                    color="success"
                    sx={{ mt: 1 }}
                  />
                )}
              </Box>

              {packageData.savings_amount > 0 && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  صرفه‌جویی {formatPrice(packageData.savings_amount)} تومان 
                  ({packageData.savings_percentage}%) نسبت به خرید جداگانه
                </Alert>
              )}

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <MoneyIcon fontSize="small" color="action" />
                <Typography variant="body2">
                  قیمت کل دوره‌ها: {formatPrice(packageData.original_total_price)} تومان
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Statistics */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                آمار
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <PeopleIcon fontSize="small" color="action" />
                <Typography variant="body2">
                  {packageData.purchase_count} خرید
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <MoneyIcon fontSize="small" color="action" />
                <Typography variant="body2">
                  {formatPrice(packageData.revenue)} تومان درآمد
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <StarIcon fontSize="small" color="action" />
                <Typography variant="body2">
                  {packageData.rating.toFixed(1)} امتیاز ({packageData.review_count} نظر)
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <ScheduleIcon fontSize="small" color="action" />
                <Typography variant="body2">
                  {packageData.duration_months} ماه مدت زمان
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Package Details */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                جزئیات
              </Typography>
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  زبان:
                </Typography>
                <Typography variant="body2">
                  {packageData.language === 'fa' ? 'فارسی' : 'انگلیسی'}
                </Typography>
              </Box>
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  ایجاد شده:
                </Typography>
                <Typography variant="body2">
                  {packageData.created_at_persian}
                </Typography>
              </Box>
              
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  آخرین بروزرسانی:
                </Typography>
                <Typography variant="body2">
                  {packageData.updated_at_persian}
                </Typography>
              </Box>
              
              {packageData.published_at_persian && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    تاریخ انتشار:
                  </Typography>
                  <Typography variant="body2">
                    {packageData.published_at_persian}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>تأیید حذف</DialogTitle>
        <DialogContent>
          <Typography>
            آیا از حذف این پکیج اطمینان دارید؟ این عمل قابل بازگشت نیست.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>انصراف</Button>
          <Button
            color="error"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'در حال حذف...' : 'حذف'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PackageDetail;
