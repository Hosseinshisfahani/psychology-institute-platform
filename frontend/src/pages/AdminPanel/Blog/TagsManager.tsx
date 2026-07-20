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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Alert,
  Skeleton,
  Tooltip,
  Avatar,
  LinearProgress,
  Toolbar,
  InputAdornment,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  MoreVert as MoreVertIcon,
  TrendingUp as TrendingUpIcon,
  Merge as MergeIcon,
  Cloud as CloudIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useSnackbar } from 'notistack';
import { blogTagApi, blogUtils, BlogTag } from '../../../services/blogAdminApi';
import TagChip from '../../../components/Admin/Blog/TagChip';

const schema = yup.object({
  name: yup.string().required('نام برچسب الزامی است'),
  slug: yup.string()
    .required('نامک الزامی است')
    .matches(
      /^[a-z0-9_-]+$/,
      'نامک باید فقط شامل حروف انگلیسی، اعداد، خط تیره و زیرخط باشد'
    ),
});

type FormData = yup.InferType<typeof schema>;

const TagsManager: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<BlogTag | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'table' | 'cloud'>('table');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedTag, setSelectedTag] = useState<BlogTag | null>(null);

  const {
    control,
    handleSubmit: formHandleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    defaultValues: {
      name: '',
      slug: '',
    },
  });

  // Fetch tags
  const { data: tagsData = [], isLoading, error } = useQuery({
    queryKey: ['admin-blog-tags'],
    queryFn: () => blogTagApi.getTags(),
  });

  // Ensure tags is always an array
  const tags = Array.isArray(tagsData) ? tagsData : [];

  // Filter tags based on search
  const filteredTags = tags.filter((tag: BlogTag) =>
    tag.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Create tag mutation
  const createMutation = useMutation({
    mutationFn: (data: FormData) => blogTagApi.createTag(data),
    onSuccess: () => {
      enqueueSnackbar('برچسب با موفقیت ایجاد شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-tags'] });
      setDialogOpen(false);
      reset();
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در ایجاد برچسب', { variant: 'error' });
    },
  });

  // Update tag mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: FormData }) =>
      blogTagApi.updateTag(id, data),
    onSuccess: () => {
      enqueueSnackbar('برچسب با موفقیت به‌روزرسانی شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-tags'] });
      setDialogOpen(false);
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در به‌روزرسانی برچسب', { variant: 'error' });
    },
  });

  // Delete tag mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => blogTagApi.deleteTag(id),
    onSuccess: () => {
      enqueueSnackbar('برچسب با موفقیت حذف شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-tags'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در حذف برچسب', { variant: 'error' });
    },
  });

  const handleCreate = () => {
    setEditingTag(null);
    reset({
      name: '',
      slug: '',
    });
    setDialogOpen(true);
  };

  const handleEdit = (tag: BlogTag) => {
    setEditingTag(tag);
    reset({
      name: tag.name,
      slug: tag.slug,
    });
    setDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    if (window.confirm('آیا از حذف این برچسب اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  const onSubmit = (data: FormData) => {
    if (editingTag) {
      updateMutation.mutate({ id: editingTag.id!, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingTag(null);
    reset();
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, tag: BlogTag) => {
    setAnchorEl(event.currentTarget);
    setSelectedTag(tag);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedTag(null);
  };

  const handleMerge = () => {
    // TODO: Implement tag merge functionality
    enqueueSnackbar('قابلیت ادغام برچسب‌ها به زودی اضافه خواهد شد', { variant: 'info' });
    handleMenuClose();
  };

  // Sort tags by usage count
  const sortedTags = [...filteredTags].sort((a, b) => (b.usage_count || 0) - (a.usage_count || 0));

  // Get max usage count for cloud sizing
  const maxUsage = Math.max(...tags.map((tag: BlogTag) => tag.usage_count || 0));

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        خطا در بارگذاری برچسب‌ها
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          مدیریت برچسب‌ها
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          برچسب جدید
        </Button>
      </Box>

      {/* Toolbar */}
      <Card sx={{ mb: 3 }}>
        <Toolbar>
          <TextField
            placeholder="جستجو در برچسب‌ها..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ flexGrow: 1, mr: 2 }}
          />
          <Button
            variant={viewMode === 'table' ? 'contained' : 'outlined'}
            onClick={() => setViewMode('table')}
            startIcon={<EditIcon />}
            sx={{ mr: 1 }}
          >
            جدول
          </Button>
          <Button
            variant={viewMode === 'cloud' ? 'contained' : 'outlined'}
            onClick={() => setViewMode('cloud')}
            startIcon={<CloudIcon />}
          >
            ابر برچسب‌ها
          </Button>
        </Toolbar>
      </Card>

      {/* Tags Content */}
      {viewMode === 'table' ? (
        <Card>
          <CardContent sx={{ p: 0 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>نام</TableCell>
                    <TableCell>نامک</TableCell>
                    <TableCell>استفاده</TableCell>
                    <TableCell>تاریخ ایجاد</TableCell>
                    <TableCell>عملیات</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading ? (
                    Array.from({ length: 5 }).map((_, index) => (
                      <TableRow key={index}>
                        <TableCell><Skeleton variant="text" width="80%" /></TableCell>
                        <TableCell><Skeleton variant="text" width="60%" /></TableCell>
                        <TableCell><Skeleton variant="text" width={40} /></TableCell>
                        <TableCell><Skeleton variant="text" width={80} /></TableCell>
                        <TableCell><Skeleton variant="rectangular" width={80} height={32} /></TableCell>
                      </TableRow>
                    ))
                  ) : filteredTags.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                        <Typography variant="body1" color="text.secondary">
                          {searchTerm ? 'هیچ برچسبی یافت نشد' : 'هیچ برچسبی وجود ندارد'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredTags.map((tag: BlogTag) => (
                      <TableRow key={tag.id} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <TagChip name={tag.name} size="small" />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {tag.slug}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" fontWeight={600}>
                              {tag.usage_count || 0}
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={((tag.usage_count || 0) / Math.max(maxUsage, 1)) * 100}
                              sx={{ width: 60, height: 4 }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {tag.created_at_persian}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5 }}>
                            <Tooltip title="ویرایش">
                              <IconButton
                                size="small"
                                onClick={() => handleEdit(tag)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="بیشتر">
                              <IconButton
                                size="small"
                                onClick={(e) => handleMenuOpen(e, tag)}
                              >
                                <MoreVertIcon fontSize="small" />
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
      ) : (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              {isLoading ? (
                Array.from({ length: 12 }).map((_, index) => (
                  <Skeleton key={index} variant="rectangular" width={120} height={32} />
                ))
              ) : filteredTags.length === 0 ? (
                <Box sx={{ width: '100%', textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    {searchTerm ? 'هیچ برچسبی یافت نشد' : 'هیچ برچسبی وجود ندارد'}
                  </Typography>
                </Box>
              ) : (
                sortedTags.map((tag: BlogTag) => {
                  const size = Math.max(12, Math.min(24, 12 + ((tag.usage_count || 0) / maxUsage) * 12));
                  return (
                    <Chip
                      key={tag.id}
                      label={tag.name}
                      size="medium"
                      sx={{
                        fontSize: `${size}px`,
                        height: 'auto',
                        padding: '8px 12px',
                        '& .MuiChip-label': {
                          padding: '4px 8px',
                        },
                      }}
                      onClick={() => handleEdit(tag)}
                      onDelete={() => handleDelete(tag.id!)}
                      deleteIcon={<DeleteIcon />}
                    />
                  );
                })
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Statistics */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            آمار برچسب‌ها
          </Typography>
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Box sx={{ flex: '1 1 300px', minWidth: 200 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <TrendingUpIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {tags.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    کل برچسب‌ها
                  </Typography>
                </Box>
              </Box>
            </Box>
            <Box sx={{ flex: '1 1 300px', minWidth: 200 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <TrendingUpIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {tags.reduce((sum: number, tag: BlogTag) => sum + (tag.usage_count || 0), 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    کل استفاده‌ها
                  </Typography>
                </Box>
              </Box>
            </Box>
            <Box sx={{ flex: '1 1 300px', minWidth: 200 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <TrendingUpIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" component="div">
                    {tags.length > 0 ? Math.round(tags.reduce((sum: number, tag: BlogTag) => sum + (tag.usage_count || 0), 0) / tags.length) : 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    میانگین استفاده
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingTag ? 'ویرایش برچسب' : 'برچسب جدید'}
        </DialogTitle>
        <form onSubmit={formHandleSubmit(onSubmit)}>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
              <Controller
                name="name"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="نام برچسب"
                    fullWidth
                    error={!!errors.name}
                    helperText={errors.name?.message}
                    onChange={(e) => {
                      field.onChange(e);
                      // Auto-generate slug using the utility function
                      const slug = blogUtils.generateSlug(e.target.value);
                      if (slug) {
                        setValue('slug', slug);
                      }
                    }}
                  />
                )}
              />

              <Controller
                name="slug"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    value={typeof field.value === 'string' ? field.value : ''}
                    label="نامک"
                    fullWidth
                    error={!!errors.slug}
                    helperText={errors.slug?.message || 'آدرس اینترنتی برچسب (فقط حروف انگلیسی، اعداد، خط تیره و زیرخط)'}
                    onChange={(e) => {
                      // Sanitize slug input: only allow ASCII letters, numbers, hyphens, and underscores
                      const sanitized = e.target.value
                        .toLowerCase()
                        .replace(/[^a-z0-9_-]/g, '') // Remove invalid characters
                        .replace(/-+/g, '-') // Replace multiple hyphens with single
                        .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
                      field.onChange(sanitized);
                    }}
                  />
                )}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>
              لغو
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {createMutation.isPending || updateMutation.isPending ? (
                <CircularProgress size={20} />
              ) : (
                editingTag ? 'به‌روزرسانی' : 'ایجاد'
              )}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => selectedTag && handleEdit(selectedTag)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>ویرایش</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleMerge}>
          <ListItemIcon>
            <MergeIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>ادغام</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => selectedTag && handleDelete(selectedTag.id!)}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>حذف</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default TagsManager;
