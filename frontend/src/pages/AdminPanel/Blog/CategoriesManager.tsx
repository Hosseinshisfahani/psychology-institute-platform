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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  Skeleton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Palette as PaletteIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useSnackbar } from 'notistack';
import { blogCategoryApi, BlogCategory } from '../../../services/blogAdminApi';
import CategoryChip from '../../../components/Admin/Blog/CategoryChip';

const schema = yup.object({
  name: yup.string().required('نام دسته‌بندی الزامی است'),
  slug: yup.string().required('نامک الزامی است'),
  description: yup.string(),
  color: yup.string().required('رنگ الزامی است'),
  icon: yup.string(),
  is_active: yup.boolean(),
});

type FormData = yup.InferType<typeof schema>;

const CategoriesManager: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<BlogCategory | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);

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
      description: '',
      color: '#007bff',
      icon: '',
      is_active: true,
    },
  });

  // Fetch categories
  const { data: categoriesData = [], isLoading, error } = useQuery({
    queryKey: ['admin-blog-categories'],
    queryFn: () => blogCategoryApi.getCategories(),
  });

  // Ensure categories is always an array
  const categories = Array.isArray(categoriesData) ? categoriesData : [];

  // Create category mutation
  const createMutation = useMutation({
    mutationFn: (data: FormData) => blogCategoryApi.createCategory(data),
    onSuccess: () => {
      enqueueSnackbar('دسته‌بندی با موفقیت ایجاد شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-categories'] });
      setDialogOpen(false);
      reset();
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در ایجاد دسته‌بندی', { variant: 'error' });
    },
  });

  // Update category mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: FormData }) =>
      blogCategoryApi.updateCategory(id, data),
    onSuccess: () => {
      enqueueSnackbar('دسته‌بندی با موفقیت به‌روزرسانی شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-categories'] });
      setEditingId(null);
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در به‌روزرسانی دسته‌بندی', { variant: 'error' });
    },
  });

  // Delete category mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => blogCategoryApi.deleteCategory(id),
    onSuccess: () => {
      enqueueSnackbar('دسته‌بندی با موفقیت حذف شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-blog-categories'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در حذف دسته‌بندی', { variant: 'error' });
    },
  });

  const handleCreate = () => {
    setEditingCategory(null);
    reset({
      name: '',
      slug: '',
      description: '',
      color: '#007bff',
      icon: '',
      is_active: true,
    });
    setDialogOpen(true);
  };

  const handleEdit = (category: BlogCategory) => {
    setEditingCategory(category);
    reset({
      name: category.name,
      slug: category.slug,
      description: category.description || '',
      color: category.color,
      icon: category.icon || '',
      is_active: category.is_active,
    });
    setDialogOpen(true);
  };

  const handleInlineEdit = (category: BlogCategory) => {
    setEditingId(category.id!);
    reset({
      name: category.name,
      slug: category.slug,
      description: category.description || '',
      color: category.color,
      icon: category.icon || '',
      is_active: category.is_active,
    });
  };

  const handleInlineSave = (data: FormData) => {
    if (editingId) {
      updateMutation.mutate({ id: editingId, data });
    }
  };

  const handleInlineCancel = () => {
    setEditingId(null);
    reset();
  };

  const handleDelete = (id: number) => {
    if (window.confirm('آیا از حذف این دسته‌بندی اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  const onSubmit = (data: FormData) => {
    if (editingCategory) {
      updateMutation.mutate({ id: editingCategory.id!, data });
      setDialogOpen(false);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingCategory(null);
    reset();
  };

  const predefinedColors = [
    '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
    '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
  ];

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        خطا در بارگذاری دسته‌بندی‌ها
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          مدیریت دسته‌بندی‌ها
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreate}
        >
          دسته‌بندی جدید
        </Button>
      </Box>

      {/* Categories Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>نام</TableCell>
                  <TableCell>نامک</TableCell>
                  <TableCell>توضیحات</TableCell>
                  <TableCell>رنگ</TableCell>
                  <TableCell>آیکون</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>تعداد پست‌ها</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, index) => (
                    <TableRow key={index}>
                      <TableCell><Skeleton variant="text" width="80%" /></TableCell>
                      <TableCell><Skeleton variant="text" width="60%" /></TableCell>
                      <TableCell><Skeleton variant="text" width="100%" /></TableCell>
                      <TableCell><Skeleton variant="rectangular" width={40} height={24} /></TableCell>
                      <TableCell><Skeleton variant="text" width="40%" /></TableCell>
                      <TableCell><Skeleton variant="rectangular" width={60} height={24} /></TableCell>
                      <TableCell><Skeleton variant="text" width={40} /></TableCell>
                      <TableCell><Skeleton variant="rectangular" width={80} height={32} /></TableCell>
                    </TableRow>
                  ))
                ) : categories.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        هیچ دسته‌بندی‌ای یافت نشد
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  categories.map((category: BlogCategory) => (
                    <TableRow key={category.id} hover>
                      {editingId === category.id ? (
                        <>
                          <TableCell>
                            <Controller
                              name="name"
                              control={control}
                              render={({ field }) => (
                                <TextField
                                  {...field}
                                  size="small"
                                  error={!!errors.name}
                                  helperText={errors.name?.message}
                                />
                              )}
                            />
                          </TableCell>
                          <TableCell>
                            <Controller
                              name="slug"
                              control={control}
                              render={({ field }) => (
                                <TextField
                                  {...field}
                                  size="small"
                                  error={!!errors.slug}
                                  helperText={errors.slug?.message}
                                />
                              )}
                            />
                          </TableCell>
                          <TableCell>
                            <Controller
                              name="description"
                              control={control}
                              render={({ field }) => (
                                <TextField
                                  {...field}
                                  size="small"
                                  multiline
                                  rows={2}
                                />
                              )}
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Controller
                                name="color"
                                control={control}
                                render={({ field }) => (
                                  <TextField
                                    {...field}
                                    size="small"
                                    type="color"
                                    sx={{ width: 60 }}
                                  />
                                )}
                              />
                              <Box sx={{ display: 'flex', gap: 0.5 }}>
                                {predefinedColors.map((color) => (
                                  <Box
                                    key={color}
                                    sx={{
                                      width: 20,
                                      height: 20,
                                      backgroundColor: color,
                                      borderRadius: '50%',
                                      cursor: 'pointer',
                                      border: '2px solid transparent',
                                      '&:hover': {
                                        border: '2px solid #000',
                                      },
                                    }}
                                    onClick={() => setValue('color', color)}
                                  />
                                ))}
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Controller
                              name="icon"
                              control={control}
                              render={({ field }) => (
                                <TextField
                                  {...field}
                                  size="small"
                                  placeholder="fa fa-icon"
                                />
                              )}
                            />
                          </TableCell>
                          <TableCell>
                            <Controller
                              name="is_active"
                              control={control}
                              render={({ field }) => (
                                <Switch
                                  checked={field.value}
                                  onChange={field.onChange}
                                  size="small"
                                />
                              )}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {category.post_count}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                              <Tooltip title="ذخیره">
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={formHandleSubmit(handleInlineSave)}
                                  disabled={updateMutation.isPending}
                                >
                                  <SaveIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="لغو">
                                <IconButton
                                  size="small"
                                  onClick={handleInlineCancel}
                                >
                                  <CancelIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </>
                      ) : (
                        <>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <CategoryChip
                                name={category.name}
                                color={category.color}
                                size="small"
                              />
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {category.slug}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" noWrap>
                              {category.description || '-'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Box
                                sx={{
                                  width: 24,
                                  height: 24,
                                  backgroundColor: category.color,
                                  borderRadius: 1,
                                }}
                              />
                              <Typography variant="caption" fontFamily="monospace">
                                {category.color}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {category.icon || '-'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={category.is_active ? 'فعال' : 'غیرفعال'}
                              color={category.is_active ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {category.post_count}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                              <Tooltip title="ویرایش">
                                <IconButton
                                  size="small"
                                  onClick={() => handleInlineEdit(category)}
                                >
                                  <EditIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="حذف">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => handleDelete(category.id!)}
                                  disabled={deleteMutation.isPending}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </>
                      )}
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingCategory ? 'ویرایش دسته‌بندی' : 'دسته‌بندی جدید'}
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
                    label="نام دسته‌بندی"
                    fullWidth
                    error={!!errors.name}
                    helperText={errors.name?.message}
                  />
                )}
              />

              <Controller
                name="slug"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="نامک"
                    fullWidth
                    error={!!errors.slug}
                    helperText={errors.slug?.message || 'آدرس اینترنتی دسته‌بندی'}
                  />
                )}
              />

              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="توضیحات"
                    fullWidth
                    multiline
                    rows={3}
                  />
                )}
              />

              <Box>
                <Typography variant="body2" gutterBottom>
                  رنگ دسته‌بندی
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Controller
                    name="color"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        type="color"
                        sx={{ width: 80 }}
                      />
                    )}
                  />
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {predefinedColors.map((color) => (
                      <Box
                        key={color}
                        sx={{
                          width: 32,
                          height: 32,
                          backgroundColor: color,
                          borderRadius: 1,
                          cursor: 'pointer',
                          border: '2px solid transparent',
                          '&:hover': {
                            border: '2px solid #000',
                          },
                        }}
                        onClick={() => setValue('color', color)}
                      />
                    ))}
                  </Box>
                </Box>
              </Box>

              <Controller
                name="icon"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="آیکون (Font Awesome)"
                    fullWidth
                    placeholder="fa fa-folder"
                    helperText="نام کلاس آیکون Font Awesome"
                  />
                )}
              />

              <Controller
                name="is_active"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={
                      <Switch
                        checked={field.value}
                        onChange={field.onChange}
                      />
                    }
                    label="فعال"
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
                editingCategory ? 'به‌روزرسانی' : 'ایجاد'
              )}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default CategoriesManager;
