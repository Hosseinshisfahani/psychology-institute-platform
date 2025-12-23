import React, { useState, useEffect } from 'react';
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
  Tooltip,
  Skeleton,
  Alert,
  Pagination,
  Stack,
  Collapse,
  Badge,
  Divider,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Preview as PreviewIcon,
  Check as ApproveIcon,
  Close as RejectIcon,
  Comment as CommentIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { useAuth } from '../../../contexts/AuthContext';
import { blogPostApi, blogCategoryApi, blogTagApi, blogCommentApi, BlogPost, BlogFilters as BlogFiltersType, BlogComment } from '../../../services/blogAdminApi';
import StatusBadge from '../../../components/Admin/Blog/StatusBadge';
import CategoryChip from '../../../components/Admin/Blog/CategoryChip';
import TagChip from '../../../components/Admin/Blog/TagChip';
import BlogFilters from '../../../components/Admin/Blog/BlogFilters';
import BulkActionBar from '../../../components/Admin/Blog/BulkActionBar';

const BlogList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [selectedPosts, setSelectedPosts] = useState<number[]>([]);
  const [filters, setFilters] = useState<BlogFiltersType>({});
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [showCommentsSection, setShowCommentsSection] = useState(true);

  // Fetch posts
  const { data: postsData, isLoading, error } = useQuery({
    queryKey: ['admin-blog-posts', filters, page],
    queryFn: () => blogPostApi.getPosts({ ...filters, page, page_size: 10 }),
  });

  // Fetch categories and tags for filters
  const { data: categoriesData = [] } = useQuery({
    queryKey: ['admin-blog-categories'],
    queryFn: () => blogCategoryApi.getCategories(),
  });

  const { data: tagsData = [] } = useQuery({
    queryKey: ['admin-blog-tags'],
    queryFn: () => blogTagApi.getTags(),
  });

  // Fetch pending comments for approval
  const { data: pendingCommentsData, refetch: refetchPendingComments } = useQuery({
    queryKey: ['admin-blog-pending-comments'],
    queryFn: () => blogCommentApi.getComments({ is_approved: false }),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const pendingComments = pendingCommentsData?.results || [];
  const pendingCount = pendingComments.length;

  // Ensure categories and tags are always arrays
  const categories = Array.isArray(categoriesData) ? categoriesData : [];
  const tags = Array.isArray(tagsData) ? tagsData : [];

  // Bulk action mutation
  const bulkActionMutation = useMutation({
    mutationFn: ({ action, postIds }: { action: string; postIds: number[] }) =>
      blogPostApi.bulkAction(action, postIds),
    onSuccess: (data) => {
      enqueueSnackbar(data.message, { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-posts'] });
      setSelectedPosts([]);
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در انجام عملیات', { variant: 'error' });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => blogPostApi.deletePost(id),
    onSuccess: () => {
      enqueueSnackbar('پست با موفقیت حذف شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-posts'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در حذف پست', { variant: 'error' });
    },
  });

  // Approve comment mutation
  const approveCommentMutation = useMutation({
    mutationFn: (id: number) => blogCommentApi.updateComment(id, { is_approved: true }),
    onSuccess: () => {
      enqueueSnackbar('نظر تایید شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-pending-comments'] });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در تایید نظر', { variant: 'error' });
    },
  });

  // Reject comment mutation
  const rejectCommentMutation = useMutation({
    mutationFn: (id: number) => blogCommentApi.updateComment(id, { is_approved: false }),
    onSuccess: () => {
      enqueueSnackbar('نظر رد شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-pending-comments'] });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-comments'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در رد نظر', { variant: 'error' });
    },
  });

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedPosts(postsData?.results?.map((post: BlogPost) => post.id!) || []);
    } else {
      setSelectedPosts([]);
    }
  };

  const handleSelectPost = (postId: number, checked: boolean) => {
    if (checked) {
      setSelectedPosts(prev => [...prev, postId]);
    } else {
      setSelectedPosts(prev => prev.filter(id => id !== postId));
    }
  };

  const handleBulkAction = (action: string) => {
    if (selectedPosts.length === 0) return;
    bulkActionMutation.mutate({ action, postIds: selectedPosts });
  };

  const handleDelete = (postId: number) => {
    if (window.confirm('آیا از حذف این پست اطمینان دارید؟')) {
      deleteMutation.mutate(postId);
    }
  };

  const handlePreview = (post: BlogPost) => {
    // Open preview in a new tab/window
    const previewUrl = `/blog/post/${post.slug}`;
    window.open(previewUrl, '_blank');
  };

  const handleFiltersChange = (newFilters: BlogFiltersType) => {
    setFilters(newFilters);
    setPage(1);
  };

  const handleClearFilters = () => {
    setFilters({});
    setPage(1);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  // Get unique authors from posts
  const authors = React.useMemo(() => {
    const authorMap = new Map();
    postsData?.results?.forEach((post: BlogPost) => {
      if (post.author_name && post.author_email) {
        authorMap.set(post.author, {
          id: post.author,
          name: post.author_name,
          email: post.author_email,
        });
      }
    });
    return Array.from(authorMap.values());
  }, [postsData?.results]);

  const handleApproveComment = (commentId: number) => {
    approveCommentMutation.mutate(commentId);
  };

  const handleRejectComment = (commentId: number) => {
    rejectCommentMutation.mutate(commentId);
  };

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        خطا در بارگذاری پست‌ها
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          مدیریت بلاگ
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
          >
            فیلترها
          </Button>
          <Button
            variant="outlined"
            startIcon={<CommentIcon />}
            onClick={() => navigate('/admin-panel/blog/comments')}
          >
            مدیریت نظرات
          </Button>
        </Box>
      </Box>

      {/* Pending Comments Section */}
      {pendingCount > 0 && (
        <Card sx={{ mb: 3, border: '2px solid', borderColor: 'warning.main' }}>
          <CardContent>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
              }}
              onClick={() => setShowCommentsSection(!showCommentsSection)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Badge badgeContent={pendingCount} color="error">
                  <CommentIcon color="warning" sx={{ fontSize: 32 }} />
                </Badge>
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    نظرات در انتظار تایید
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {pendingCount} نظر نیاز به بررسی دارد
                  </Typography>
                </Box>
              </Box>
              <IconButton>
                {showCommentsSection ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>

            <Collapse in={showCommentsSection}>
              <Divider sx={{ my: 2 }} />
              {pendingComments.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
                  هیچ نظری در انتظار تایید نیست
                </Typography>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>نظر</TableCell>
                        <TableCell>نویسنده</TableCell>
                        <TableCell>پست</TableCell>
                        <TableCell>تاریخ</TableCell>
                        <TableCell align="center">عملیات</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {pendingComments.slice(0, 5).map((comment: BlogComment) => (
                        <TableRow key={comment.id} hover>
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
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                                {comment.author_name?.charAt(0)}
                              </Avatar>
                              <Typography variant="body2">{comment.author_name}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography
                              variant="body2"
                              sx={{
                                maxWidth: 200,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              {comment.post_title}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {comment.created_at_persian}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                              <Tooltip title="تایید">
                                <IconButton
                                  size="small"
                                  color="success"
                                  onClick={() => handleApproveComment(comment.id!)}
                                  disabled={approveCommentMutation.isPending}
                                >
                                  <ApproveIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="رد">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => handleRejectComment(comment.id!)}
                                  disabled={rejectCommentMutation.isPending}
                                >
                                  <RejectIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
              {pendingCount > 5 && (
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/admin-panel/blog/comments', { state: { filterPending: true } })}
                  >
                    مشاهده همه نظرات ({pendingCount})
                  </Button>
                </Box>
              )}
            </Collapse>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      {showFilters && (
        <BlogFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          categories={Array.isArray(categories) ? categories : []}
          tags={Array.isArray(tags) ? tags : []}
          authors={Array.isArray(authors) ? authors : []}
          onClear={handleClearFilters}
        />
      )}

      {/* Posts Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedPosts.length === postsData?.results?.length && postsData?.results?.length > 0}
                      indeterminate={selectedPosts.length > 0 && selectedPosts.length < (postsData?.results?.length || 0)}
                      onChange={(e) => handleSelectAll(e.target.checked)}
                    />
                  </TableCell>
                  <TableCell>عنوان</TableCell>
                  <TableCell>نویسنده</TableCell>
                  <TableCell>دسته‌بندی</TableCell>
                  <TableCell>برچسب‌ها</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>بازدید</TableCell>
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
                        <Skeleton variant="rectangular" width={80} height={24} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width={120} height={24} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width={80} height={24} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width={40} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width={80} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width={120} height={32} />
                      </TableCell>
                    </TableRow>
                  ))
                ) : postsData?.results?.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        هیچ پستی یافت نشد
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  postsData?.results?.map((post: BlogPost) => (
                    <TableRow key={post.id} hover>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedPosts.includes(post.id!)}
                          onChange={(e) => handleSelectPost(post.id!, e.target.checked)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight={600} noWrap>
                            {post.title}
                          </Typography>
                          {post.excerpt && (
                            <Typography variant="caption" color="text.secondary" noWrap>
                              {post.excerpt.substring(0, 50)}...
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                            {post.author_name?.charAt(0)}
                          </Avatar>
                          <Typography variant="body2">
                            {post.author_name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <CategoryChip
                          name={post.category_name || ''}
                          color={post.category_color}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {post.tags_data?.slice(0, 2).map((tag) => (
                            <TagChip
                              key={tag.id}
                              name={tag.name}
                              size="small"
                            />
                          ))}
                          {post.tags_data && post.tags_data.length > 2 && (
                            <Chip
                              label={`+${post.tags_data.length - 2}`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={post.status} />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {post.view_count}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {post.created_at_persian}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="پیش‌نمایش">
                            <IconButton
                              size="small"
                              onClick={() => handlePreview(post)}
                            >
                              <PreviewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="حذف">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDelete(post.id!)}
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

      {/* Pagination */}
      {postsData?.total_pages && postsData.total_pages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={postsData.total_pages}
            page={page}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}

      {/* Bulk Action Bar */}
      <BulkActionBar
        selectedCount={selectedPosts.length}
        onBulkAction={handleBulkAction}
        onClearSelection={() => setSelectedPosts([])}
        disabled={bulkActionMutation.isPending}
      />
    </Box>
  );
};

export default BlogList;
