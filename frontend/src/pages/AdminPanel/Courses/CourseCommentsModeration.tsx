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
  Paper,
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
  Badge,
} from '@mui/material';
import {
  Check as ApproveIcon,
  Close as RejectIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import axios from 'axios';

interface CourseComment {
  id: number;
  content: string;
  author: number;
  author_name: string;
  author_email: string;
  course: number;
  course_title: string;
  course_slug: string;
  is_approved: boolean;
  is_approved_display: string;
  parent: number | null;
  replies_count: number;
  created_at: string;
  created_at_persian: string;
  updated_at: string;
  updated_at_persian: string;
}

interface CommentFilters {
  is_approved?: boolean;
  course?: number;
  search?: string;
}

const CourseCommentsModeration: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [selectedComments, setSelectedComments] = useState<number[]>([]);
  const [filters, setFilters] = useState<CommentFilters>({});

  // Fetch comments
  const { data: commentsData, isLoading, error } = useQuery({
    queryKey: ['admin-course-comments', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.is_approved !== undefined) {
        params.append('is_approved', filters.is_approved.toString());
      }
      if (filters.course) {
        params.append('course', filters.course.toString());
      }
      if (filters.search) {
        params.append('search', filters.search);
      }
      const response = await axios.get(`/api/admin/courses/comments/?${params}`);
      return response.data;
    },
  });

  // Fetch courses for filter dropdown
  const { data: coursesData } = useQuery({
    queryKey: ['admin-courses-for-comments'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/courses/?page_size=100');
      return response.data;
    },
  });
  
  // Extract courses from paginated response
  const courses = Array.isArray(coursesData) ? coursesData : (coursesData?.results || []);

  // Extract comments from paginated response
  const comments = Array.isArray(commentsData) ? commentsData : (commentsData?.results || []);

  // Approve comment mutation
  const approveMutation = useMutation({
    mutationFn: (id: number) => axios.patch(`/api/admin/courses/comments/${id}/`, { is_approved: true }),
    onSuccess: () => {
      enqueueSnackbar('نظر تایید شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-course-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در تایید نظر', { variant: 'error' });
    },
  });

  // Reject comment mutation
  const rejectMutation = useMutation({
    mutationFn: (id: number) => axios.patch(`/api/admin/courses/comments/${id}/`, { is_approved: false }),
    onSuccess: () => {
      enqueueSnackbar('نظر رد شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-course-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در رد نظر', { variant: 'error' });
    },
  });

  // Delete comment mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/admin/courses/comments/${id}/`),
    onSuccess: () => {
      enqueueSnackbar('نظر حذف شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-course-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در حذف نظر', { variant: 'error' });
    },
  });

  // Bulk action mutation
  const bulkActionMutation = useMutation({
    mutationFn: async (data: { action: string; comment_ids: number[] }) => {
      const response = await axios.post('/api/admin/courses/comments/bulk-action/', data);
      return response.data;
    },
    onSuccess: (data) => {
      enqueueSnackbar(data.message || 'عملیات با موفقیت انجام شد', { variant: 'success' });
      setSelectedComments([]);
      queryClient.invalidateQueries({ queryKey: ['admin-course-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در انجام عملیات', { variant: 'error' });
    },
  });

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedComments(comments.map((c: CourseComment) => c.id));
    } else {
      setSelectedComments([]);
    }
  };

  const handleSelectComment = (id: number) => {
    setSelectedComments((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const handleBulkAction = (action: string) => {
    if (selectedComments.length === 0) {
      enqueueSnackbar('لطفاً حداقل یک نظر را انتخاب کنید', { variant: 'warning' });
      return;
    }
    bulkActionMutation.mutate({ action, comment_ids: selectedComments });
  };

  const handleFilterChange = (key: keyof CommentFilters, value: any) => {
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
            مدیریت نظرات دوره‌ها
          </Typography>
          <Typography variant="body1" color="text.secondary">
            تایید، رد و مدیریت نظرات دوره‌های آموزشی
          </Typography>
        </Box>
      </Box>

      {/* Quick Stats */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="primary">
              {comments.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              کل نظرات
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="warning.main">
              {comments.filter((c: CourseComment) => !c.is_approved).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              در انتظار تایید
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="success.main">
              {comments.filter((c: CourseComment) => c.is_approved).length}
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

            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>دوره</InputLabel>
              <Select
                value={filters.course || ''}
                onChange={(e) => handleFilterChange('course', e.target.value || undefined)}
                label="دوره"
              >
                <MenuItem value="">همه دوره‌ها</MenuItem>
                {courses.slice(0, 20).map((course: any) => (
                  <MenuItem key={course.id} value={course.id}>
                    {course.title}
                  </MenuItem>
                ))}
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
      {selectedComments.length > 0 && (
        <Card sx={{ mb: 3, bgcolor: 'action.selected' }}>
          <CardContent>
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="body2">
                {selectedComments.length} نظر انتخاب شده
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

      {/* Comments Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      indeterminate={selectedComments.length > 0 && selectedComments.length < comments.length}
                      checked={comments.length > 0 && selectedComments.length === comments.length}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                  <TableCell>نویسنده</TableCell>
                  <TableCell>دوره</TableCell>
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
                      <TableCell colSpan={7}>
                        <Skeleton variant="text" height={40} />
                      </TableCell>
                    </TableRow>
                  ))
                ) : comments.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">
                        نظری یافت نشد
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  comments.map((comment: CourseComment) => (
                    <TableRow key={comment.id} hover>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedComments.includes(comment.id)}
                          onChange={() => handleSelectComment(comment.id)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ width: 32, height: 32 }}>
                            {comment.author_name.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {comment.author_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {comment.author_email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{comment.course_title}</Typography>
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
                          {comment.content}
                        </Typography>
                        {comment.replies_count > 0 && (
                          <Chip
                            label={`${comment.replies_count} پاسخ`}
                            size="small"
                            sx={{ mt: 0.5 }}
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={comment.is_approved_display}
                          color={comment.is_approved ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {comment.created_at_persian || comment.created_at}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Stack direction="row" spacing={1} justifyContent="center">
                          {!comment.is_approved && (
                            <Tooltip title="تایید">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => approveMutation.mutate(comment.id)}
                                disabled={approveMutation.isPending}
                              >
                                <ApproveIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          {comment.is_approved && (
                            <Tooltip title="رد">
                              <IconButton
                                size="small"
                                color="warning"
                                onClick={() => rejectMutation.mutate(comment.id)}
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
                                  deleteMutation.mutate(comment.id);
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

export default CourseCommentsModeration;

