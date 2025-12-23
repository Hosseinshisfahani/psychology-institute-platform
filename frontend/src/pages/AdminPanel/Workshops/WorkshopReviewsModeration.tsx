import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  IconButton,
  Chip,
  Avatar,
  Alert,
  Skeleton,
  Tooltip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Stack,
} from '@mui/material';
import {
  Check as ApproveIcon,
  Close as RejectIcon,
  Delete as DeleteIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import axios from 'axios';

interface WorkshopReview {
  id: number;
  rating: number;
  title: string;
  content: string;
  instructor_rating: number;
  content_rating: number;
  interaction_rating: number;
  author_name: string;
  author_email: string;
  workshop_title: string;
  workshop_slug: string;
  is_approved: boolean;
  is_approved_display: string;
  created_at: string;
  created_at_persian: string;
  updated_at: string;
  updated_at_persian: string;
}

interface ReviewFilters {
  is_approved?: boolean;
  search?: string;
}

const WorkshopReviewsModeration: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [selectedReviews, setSelectedReviews] = useState<number[]>([]);
  const [filters, setFilters] = useState<ReviewFilters>({});

  // Fetch reviews
  const { data: reviewsData, isLoading, error } = useQuery({
    queryKey: ['admin-workshop-reviews', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.is_approved !== undefined) {
        params.append('is_approved', filters.is_approved.toString());
      }
      if (filters.search) {
        params.append('search', filters.search);
      }
      const response = await axios.get(`/api/admin/workshops/reviews/?${params}`);
      return response.data;
    },
  });

  // Extract reviews from paginated response
  const reviews = Array.isArray(reviewsData) ? reviewsData : (reviewsData?.results || []);

  // Approve review mutation
  const approveMutation = useMutation({
    mutationFn: (id: number) => axios.patch(`/api/admin/workshops/reviews/${id}/`, { is_approved: true }),
    onSuccess: () => {
      enqueueSnackbar('نظر تایید شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-workshop-reviews'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در تایید نظر', { variant: 'error' });
    },
  });

  // Reject review mutation
  const rejectMutation = useMutation({
    mutationFn: (id: number) => axios.patch(`/api/admin/workshops/reviews/${id}/`, { is_approved: false }),
    onSuccess: () => {
      enqueueSnackbar('نظر رد شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-workshop-reviews'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در رد نظر', { variant: 'error' });
    },
  });

  // Delete review mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/admin/workshops/reviews/${id}/`),
    onSuccess: () => {
      enqueueSnackbar('نظر حذف شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-workshop-reviews'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در حذف نظر', { variant: 'error' });
    },
  });

  // Bulk action mutation
  const bulkActionMutation = useMutation({
    mutationFn: async (data: { action: string; review_ids: number[] }) => {
      const response = await axios.post('/api/admin/workshops/reviews/bulk-action/', data);
      return response.data;
    },
    onSuccess: (data) => {
      enqueueSnackbar(data.message || 'عملیات با موفقیت انجام شد', { variant: 'success' });
      setSelectedReviews([]);
      queryClient.invalidateQueries({ queryKey: ['admin-workshop-reviews'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در انجام عملیات', { variant: 'error' });
    },
  });

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedReviews(reviews.map((r: WorkshopReview) => r.id));
    } else {
      setSelectedReviews([]);
    }
  };

  const handleSelectReview = (id: number) => {
    setSelectedReviews((prev) =>
      prev.includes(id) ? prev.filter((r) => r !== id) : [...prev, id]
    );
  };

  const handleBulkAction = (action: string) => {
    if (selectedReviews.length === 0) {
      enqueueSnackbar('لطفاً حداقل یک نظر را انتخاب کنید', { variant: 'warning' });
      return;
    }
    bulkActionMutation.mutate({ action, review_ids: selectedReviews });
  };

  const handleFilterChange = (key: keyof ReviewFilters, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  const getActiveFiltersCount = () => {
    return Object.values(filters).filter((v) => v !== undefined && v !== '').length;
  };

  if (error) {
    return (
      <Alert severity="error">
        خطا در بارگذاری نظرات: {error instanceof Error ? error.message : 'خطای ناشناخته'}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            مدیریت نظرات کارگاه‌ها
          </Typography>
          <Typography variant="body1" color="text.secondary">
            تایید، رد و مدیریت نظرات کارگاه‌های آموزشی
          </Typography>
        </Box>
      </Box>

      {/* Quick Stats */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="primary">
              {reviews.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              کل نظرات
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="warning.main">
              {reviews.filter((r: WorkshopReview) => !r.is_approved).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              در انتظار تایید
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="success.main">
              {reviews.filter((r: WorkshopReview) => r.is_approved).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              تایید شده
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>وضعیت</InputLabel>
              <Select
                value={filters.is_approved === undefined ? '' : filters.is_approved}
                onChange={(e) => handleFilterChange('is_approved', e.target.value === '' ? undefined : e.target.value === 'true')}
                label="وضعیت"
              >
                <MenuItem value="">همه</MenuItem>
                <MenuItem value="true">تایید شده</MenuItem>
                <MenuItem value="false">در انتظار</MenuItem>
              </Select>
            </FormControl>

            <TextField
              size="small"
              placeholder="جستجو در نظرات..."
              value={filters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value || undefined)}
              sx={{ minWidth: 200 }}
            />

            {getActiveFiltersCount() > 0 && (
              <Button
                size="small"
                startIcon={<ClearIcon />}
                onClick={handleClearFilters}
              >
                پاک کردن
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedReviews.length > 0 && (
        <Card sx={{ mb: 3, bgcolor: 'action.selected' }}>
          <CardContent>
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="body2">
                {selectedReviews.length} نظر انتخاب شده
              </Typography>
              <Divider orientation="vertical" flexItem />
              <Button
                size="small"
                color="success"
                startIcon={<ApproveIcon />}
                onClick={() => handleBulkAction('approve')}
                disabled={bulkActionMutation.isPending}
              >
                تایید انتخاب شده‌ها
              </Button>
              <Button
                size="small"
                color="error"
                startIcon={<RejectIcon />}
                onClick={() => handleBulkAction('reject')}
                disabled={bulkActionMutation.isPending}
              >
                رد انتخاب شده‌ها
              </Button>
              <Button
                size="small"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => handleBulkAction('delete')}
                disabled={bulkActionMutation.isPending}
              >
                حذف انتخاب شده‌ها
              </Button>
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* Reviews Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      indeterminate={selectedReviews.length > 0 && selectedReviews.length < reviews.length}
                      checked={reviews.length > 0 && selectedReviews.length === reviews.length}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                  <TableCell>نویسنده</TableCell>
                  <TableCell>کارگاه</TableCell>
                  <TableCell>امتیاز</TableCell>
                  <TableCell>عنوان</TableCell>
                  <TableCell>محتوا</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>تاریخ</TableCell>
                  <TableCell align="center">عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}>
                      <TableCell colSpan={9}>
                        <Skeleton variant="text" height={40} />
                      </TableCell>
                    </TableRow>
                  ))
                ) : reviews.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">
                        نظری یافت نشد
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  reviews.map((review: WorkshopReview) => (
                    <TableRow key={review.id} hover>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedReviews.includes(review.id)}
                          onChange={() => handleSelectReview(review.id)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ width: 32, height: 32 }}>
                            {review.author_name.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {review.author_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {review.author_email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{review.workshop_title}</Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          {[...Array(5)].map((_, i) => (
                            <i
                              key={i}
                              className={`fas fa-star ${i < review.rating ? 'text-warning' : 'text-muted'}`}
                              style={{ fontSize: '0.875rem' }}
                            ></i>
                          ))}
                          <Typography variant="caption" sx={{ ml: 1 }}>
                            {review.rating}/5
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {review.title}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            maxWidth: 300,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {review.content}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={review.is_approved_display}
                          color={review.is_approved ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {review.created_at_persian || review.created_at}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Stack direction="row" spacing={1} justifyContent="center">
                          {!review.is_approved && (
                            <Tooltip title="تایید">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => approveMutation.mutate(review.id)}
                                disabled={approveMutation.isPending}
                              >
                                <ApproveIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          {review.is_approved && (
                            <Tooltip title="رد">
                              <IconButton
                                size="small"
                                color="warning"
                                onClick={() => rejectMutation.mutate(review.id)}
                                disabled={rejectMutation.isPending}
                              >
                                <RejectIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title="حذف">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => {
                                if (window.confirm('آیا از حذف این نظر اطمینان دارید؟')) {
                                  deleteMutation.mutate(review.id);
                                }
                              }}
                              disabled={deleteMutation.isPending}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default WorkshopReviewsModeration;

