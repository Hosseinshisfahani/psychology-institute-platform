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
  Chip,
  Avatar,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ArrowBack as BackIcon,
  Palette as PaletteIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useSnackbar } from 'notistack';

interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  is_active: boolean;
  package_count: number;
  created_at: string;
  created_at_persian: string;
}

const PackageCategoriesManager: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  
  const [categoryDialog, setCategoryDialog] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<Category | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    icon: '',
    color: '#007bff',
    is_active: true,
  });

  // Fetch categories
  const { data: categories = [], isLoading } = useQuery({
    queryKey: ['admin-package-categories'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/packages/categories/');
      return response.data.results || response.data;
    },
  });

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      if (editingCategory) {
        const response = await axios.put(`/api/admin/packages/categories/${editingCategory.id}/`, data);
        return response.data;
      } else {
        const response = await axios.post('/api/admin/packages/categories/', data);
        return response.data;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-package-categories'] });
      enqueueSnackbar(
        editingCategory ? 'دسته‌بندی با موفقیت بروزرسانی شد' : 'دسته‌بندی با موفقیت ایجاد شد',
        { variant: 'success' }
      );
      handleCloseDialog();
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'خطا در ذخیره دسته‌بندی';
      enqueueSnackbar(message, { variant: 'error' });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (categoryId: number) => {
      const response = await axios.delete(`/api/admin/packages/categories/${categoryId}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-package-categories'] });
      enqueueSnackbar('دسته‌بندی با موفقیت حذف شد', { variant: 'success' });
      setDeleteDialog(false);
      setCategoryToDelete(null);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'خطا در حذف دسته‌بندی';
      enqueueSnackbar(message, { variant: 'error' });
    },
  });

  const handleOpenDialog = (category?: Category) => {
    if (category) {
      setEditingCategory(category);
      setFormData({
        name: category.name,
        description: category.description,
        icon: category.icon,
        color: category.color,
        is_active: category.is_active,
      });
    } else {
      setEditingCategory(null);
      setFormData({
        name: '',
        description: '',
        icon: '',
        color: '#007bff',
        is_active: true,
      });
    }
    setCategoryDialog(true);
  };

  const handleCloseDialog = () => {
    setCategoryDialog(false);
    setEditingCategory(null);
    setFormData({
      name: '',
      description: '',
      icon: '',
      color: '#007bff',
      is_active: true,
    });
  };

  const handleSave = () => {
    saveMutation.mutate(formData);
  };

  const handleDelete = (category: Category) => {
    setCategoryToDelete(category);
    setDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (categoryToDelete) {
      deleteMutation.mutate(categoryToDelete.id);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const predefinedColors = [
    '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
    '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
  ];

  const predefinedIcons = [
    'fas fa-graduation-cap', 'fas fa-book', 'fas fa-laptop-code', 'fas fa-paint-brush',
    'fas fa-music', 'fas fa-camera', 'fas fa-heart', 'fas fa-star', 'fas fa-lightbulb',
    'fas fa-rocket', 'fas fa-globe', 'fas fa-users', 'fas fa-chart-line'
  ];

  if (isLoading) {
    return <Typography>در حال بارگذاری...</Typography>;
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
          مدیریت دسته‌بندی‌های پکیج
        </Typography>
        <Box sx={{ ml: 'auto' }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            افزودن دسته‌بندی
          </Button>
        </Box>
      </Box>

      {/* Categories Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>نام</TableCell>
                  <TableCell>توضیحات</TableCell>
                  <TableCell>آیکون</TableCell>
                  <TableCell>رنگ</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>تعداد پکیج</TableCell>
                  <TableCell>تاریخ ایجاد</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {categories.map((category: Category) => (
                  <TableRow key={category.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar
                          sx={{
                            width: 32,
                            height: 32,
                            backgroundColor: category.color,
                            fontSize: '0.875rem',
                          }}
                        >
                          {category.icon ? (
                            <i className={category.icon} />
                          ) : (
                            <PaletteIcon fontSize="small" />
                          )}
                        </Avatar>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {category.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {category.description || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {category.icon && (
                        <i className={category.icon} style={{ fontSize: '1.25rem', color: category.color }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 20,
                            height: 20,
                            borderRadius: '50%',
                            backgroundColor: category.color,
                            border: '1px solid #ddd',
                          }}
                        />
                        <Typography variant="body2">
                          {category.color}
                        </Typography>
                      </Box>
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
                        {category.package_count}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {category.created_at_persian}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="ویرایش">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => handleOpenDialog(category)}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="حذف">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDelete(category)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Category Dialog */}
      <Dialog open={categoryDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingCategory ? 'ویرایش دسته‌بندی' : 'افزودن دسته‌بندی جدید'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              fullWidth
              label="نام دسته‌بندی"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              required
            />
            
            <TextField
              fullWidth
              label="توضیحات"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              multiline
              rows={3}
            />
            
            <FormControl fullWidth>
              <InputLabel>آیکون</InputLabel>
              <Select
                value={formData.icon}
                onChange={(e) => handleInputChange('icon', e.target.value)}
                label="آیکون"
              >
                <MenuItem value="">بدون آیکون</MenuItem>
                {predefinedIcons.map((icon) => (
                  <MenuItem key={icon} value={icon}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <i className={icon} style={{ fontSize: '1.25rem', color: formData.color }} />
                      {icon}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Box>
              <Typography variant="body2" sx={{ mb: 1 }}>
                رنگ
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {predefinedColors.map((color) => (
                  <Box
                    key={color}
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      backgroundColor: color,
                      cursor: 'pointer',
                      border: formData.color === color ? '3px solid #000' : '1px solid #ddd',
                      '&:hover': {
                        transform: 'scale(1.1)',
                      },
                    }}
                    onClick={() => handleInputChange('color', color)}
                  />
                ))}
              </Box>
              <TextField
                fullWidth
                label="کد رنگ سفارشی"
                value={formData.color}
                onChange={(e) => handleInputChange('color', e.target.value)}
                sx={{ mt: 1 }}
                placeholder="#007bff"
              />
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => handleInputChange('is_active', e.target.checked)}
              />
              <Typography variant="body2">فعال</Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>انصراف</Button>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={saveMutation.isPending}
          >
            {saveMutation.isPending ? 'در حال ذخیره...' : 'ذخیره'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>تأیید حذف</DialogTitle>
        <DialogContent>
          <Typography>
            آیا از حذف دسته‌بندی "{categoryToDelete?.name}" اطمینان دارید؟
            {categoryToDelete?.package_count && categoryToDelete.package_count > 0 && (
              <Typography color="error" sx={{ mt: 1 }}>
                این دسته‌بندی {categoryToDelete.package_count} پکیج دارد.
              </Typography>
            )}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>انصراف</Button>
          <Button
            color="error"
            onClick={confirmDelete}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'در حال حذف...' : 'حذف'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PackageCategoriesManager;
