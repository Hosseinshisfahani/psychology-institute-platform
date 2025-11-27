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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Stack,
  Badge,
} from '@mui/material';
import {
  Check as ApproveIcon,
  Close as RejectIcon,
  Delete as DeleteIcon,
  Reply as ReplyIcon,
  Visibility as ViewIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import { blogCommentApi, blogPostApi, BlogComment, CommentFilters } from '../../../services/blogAdminApi';

const CommentsModeration: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [selectedComments, setSelectedComments] = useState<number[]>([]);
  const [filters, setFilters] = useState<CommentFilters>({});
  const [replyDialogOpen, setReplyDialogOpen] = useState(false);
  const [selectedComment, setSelectedComment] = useState<BlogComment | null>(null);
  const [replyText, setReplyText] = useState('');

  // Fetch comments
  const { data: commentsData, isLoading, error } = useQuery({
    queryKey: ['admin-blog-comments', filters],
    queryFn: () => blogCommentApi.getComments(filters),
  });

  // Fetch posts for filter dropdown
  const { data: posts = [] } = useQuery({
    queryKey: ['admin-blog-posts-for-comments'],
    queryFn: () => blogPostApi.getPosts({ page_size: 100 }),
  });

  // Approve comment mutation
  const approveMutation = useMutation({
    mutationFn: (id: number) => blogCommentApi.updateComment(id, { is_approved: true }),
    onSuccess: () => {
      enqueueSnackbar('نظر تایید شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در تایید نظر', { variant: 'error' });
    },
  });

  // Reject comment mutation
  const rejectMutation = useMutation({
    mutationFn: (id: number) => blogCommentApi.updateComment(id, { is_approved: false }),
    onSuccess: () => {
      enqueueSnackbar('نظر رد شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در رد نظر', { variant: 'error' });
    },
  });

  // Delete comment mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => blogCommentApi.deleteComment(id),
    onSuccess: () => {
      enqueueSnackbar('نظر حذف شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در حذف نظر', { variant: 'error' });
    },
  });

  // Bulk action mutation
  const bulkActionMutation = useMutation({
    mutationFn: ({ action, commentIds }: { action: string; commentIds: number[] }) =>
      blogCommentApi.bulkAction(action, commentIds),
    onSuccess: (data) => {
      enqueueSnackbar(data.message, { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-comments'] });
      setSelectedComments([]);
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در انجام عملیات', { variant: 'error' });
    },
  });

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedComments(commentsData?.results?.map((comment: BlogComment) => comment.id!) || []);
    } else {
      setSelectedComments([]);
    }
  };

  const handleSelectComment = (commentId: number, checked: boolean) => {
    if (checked) {
      setSelectedComments(prev => [...prev, commentId]);
    } else {
      setSelectedComments(prev => prev.filter(id => id !== commentId));
    }
  };

  const handleApprove = (id: number) => {
    approveMutation.mutate(id);
  };

  const handleReject = (id: number) => {
    rejectMutation.mutate(id);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('آیا از حذف این نظر اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  const handleBulkAction = (action: string) => {
    if (selectedComments.length === 0) return;
    bulkActionMutation.mutate({ action, commentIds: selectedComments });
  };

  const handleReply = (comment: BlogComment) => {
    setSelectedComment(comment);
    setReplyText('');
    setReplyDialogOpen(true);
  };

  const handleSendReply = () => {
    // TODO: Implement reply functionality
    enqueueSnackbar('قابلیت پاسخ به نظرات به زودی اضافه خواهد شد', { variant: 'info' });
    setReplyDialogOpen(false);
  };

  const handleFilterChange = (key: keyof CommentFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  const getStatusColor = (isApproved: boolean) => {
    if (isApproved) return 'success';
    return 'warning';
  };

  const getStatusLabel = (isApproved: boolean) => {
    if (isApproved) return 'تایید شده';
    return 'در انتظار';
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.is_approved !== undefined) count++;
    if (filters.post) count++;
    if (filters.search) count++;
    return count;
  };

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        خطا در بارگذاری نظرات
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          مدیریت نظرات
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => {/* TODO: Implement filter panel */}}
          >
            فیلترها ({getActiveFiltersCount()})
          </Button>
        </Box>
      </Box>

      {/* Quick Stats */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="primary">
              {commentsData?.results?.length || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              کل نظرات
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="warning.main">
              {commentsData?.results?.filter((c: BlogComment) => !c.is_approved).length || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              در انتظار تایید
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1 }}>
          <CardContent sx={{ textAlign: 'center' }}>
            <Typography variant="h4" color="success.main">
              {commentsData?.results?.filter((c: BlogComment) => c.is_approved).length || 0}
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
              <InputLabel>پست</InputLabel>
              <Select
                value={filters.post || ''}
                onChange={(e) => handleFilterChange('post', e.target.value || undefined)}
                label="پست"
              >
                <MenuItem value="">همه پست‌ها</MenuItem>
                {posts.slice(0, 10).map((post: any) => (
                  <MenuItem key={post.id} value={post.id}>
                    {post.title}
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

      {/* Comments Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedComments.length === commentsData?.results?.length && commentsData?.results?.length > 0}
                      indeterminate={selectedComments.length > 0 && selectedComments.length < (commentsData?.results?.length || 0)}
                      onChange={(e) => handleSelectAll(e.target.checked)}
                    />
                  </TableCell>
                  <TableCell>نظر</TableCell>
                  <TableCell>نویسنده</TableCell>
                  <TableCell>پست</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>تاریخ</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, index) => (
                    <TableRow key={index}>
                      <TableCell padding="checkbox">
                        <Skeleton variant="rectangular" width={20} height={20} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width="80%" />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width="60%" />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width="70%" />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width={80} height={24} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width={80} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width={120} height={32} />
                      </TableCell>
                    </TableRow>
                  ))
                ) : commentsData?.results?.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        هیچ نظری یافت نشد
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  commentsData?.results?.map((comment: BlogComment) => (
                    <TableRow key={comment.id} hover>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedComments.includes(comment.id!)}
                          onChange={(e) => handleSelectComment(comment.id!, e.target.checked)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                            {comment.content}
                          </Typography>
                          {comment.replies_count && comment.replies_count > 0 && (
                            <Chip
                              label={`${comment.replies_count} پاسخ`}
                              size="small"
                              variant="outlined"
                              sx={{ mt: 0.5 }}
                            />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ width: 32, height: 32 }}>
                            {comment.author_name?.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight={600}>
                              {comment.author_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {comment.author_email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight={600} noWrap sx={{ maxWidth: 200 }}>
                            {comment.post_title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {comment.post_slug}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusLabel(comment.is_approved)}
                          color={getStatusColor(comment.is_approved) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {comment.created_at_persian}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {!comment.is_approved && (
                            <Tooltip title="تایید">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => handleApprove(comment.id!)}
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
                                onClick={() => handleReject(comment.id!)}
                                disabled={rejectMutation.isPending}
                              >
                                <RejectIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title="پاسخ">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleReply(comment)}
                            >
                              <ReplyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="حذف">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDelete(comment.id!)}
                              disabled={deleteMutation.isPending}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedComments.length > 0 && (
        <Card sx={{ mt: 2, backgroundColor: 'primary.main', color: 'white' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Typography variant="body1" fontWeight={600}>
                {selectedComments.length} نظر انتخاب شده
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  color="success"
                  size="small"
                  onClick={() => handleBulkAction('approve')}
                  disabled={bulkActionMutation.isPending}
                  startIcon={<ApproveIcon />}
                  sx={{ backgroundColor: 'white', color: 'success.main' }}
                >
                  تایید
                </Button>
                <Button
                  variant="contained"
                  color="warning"
                  size="small"
                  onClick={() => handleBulkAction('reject')}
                  disabled={bulkActionMutation.isPending}
                  startIcon={<RejectIcon />}
                  sx={{ backgroundColor: 'white', color: 'warning.main' }}
                >
                  رد
                </Button>
                <Button
                  variant="contained"
                  color="error"
                  size="small"
                  onClick={() => handleBulkAction('delete')}
                  disabled={bulkActionMutation.isPending}
                  startIcon={<DeleteIcon />}
                  sx={{ backgroundColor: 'white', color: 'error.main' }}
                >
                  حذف
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setSelectedComments([])}
                  sx={{ borderColor: 'white', color: 'white' }}
                >
                  لغو انتخاب
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Reply Dialog */}
      <Dialog open={replyDialogOpen} onClose={() => setReplyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          پاسخ به نظر {selectedComment?.author_name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              نظر اصلی:
            </Typography>
            <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
              <Typography variant="body2">
                {selectedComment?.content}
              </Typography>
            </Paper>
          </Box>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="پاسخ شما"
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder="پاسخ خود را بنویسید..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReplyDialogOpen(false)}>
            لغو
          </Button>
          <Button
            variant="contained"
            onClick={handleSendReply}
            disabled={!replyText.trim()}
          >
            ارسال پاسخ
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CommentsModeration;
