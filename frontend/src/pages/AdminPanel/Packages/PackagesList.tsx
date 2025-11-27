import React, { useState } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Checkbox,
  FormControlLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  School as SchoolIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
  MoreVert as MoreVertIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useSnackbar } from 'notistack';

interface Package {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  description: string;
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
  total_courses: number;
  total_hours: number;
  savings_amount: number;
  savings_percentage: number;
  purchase_count: number;
  revenue: number;
  rating: number;
  thumbnail?: string;
  courses: Array<{
    id: number;
    title: string;
    instructor_name: string;
    current_price: number;
  }>;
  created_at: string;
  created_at_persian: string;
}

const PackagesList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    category: '',
    is_featured: '',
  });
  
  const [selectedPackages, setSelectedPackages] = useState<number[]>([]);
  const [bulkActionDialog, setBulkActionDialog] = useState(false);
  const [bulkAction, setBulkAction] = useState('');

  // Fetch packages
  const { data: packages = [], isLoading } = useQuery({
    queryKey: ['admin-packages', filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        ...(filters.search && { search: filters.search }),
        ...(filters.status && { status: filters.status }),
        ...(filters.category && { category: filters.category }),
        ...(filters.is_featured && { is_featured: filters.is_featured }),
      });
      const response = await axios.get(`/api/admin/packages/?${params}`);
      return response.data.results || response.data;
    },
  });

  // Fetch categories for filter
  const { data: categories = [] } = useQuery({
    queryKey: ['admin-package-categories'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/packages/categories/');
      return response.data.results || response.data;
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (packageId: number) => {
      const response = await axios.delete(`/api/admin/packages/${packageId}/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-packages'] });
      enqueueSnackbar('پکیج با موفقیت حذف شد', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('خطا در حذف پکیج', { variant: 'error' });
    },
  });

  // Bulk action mutation
  const bulkActionMutation = useMutation({
    mutationFn: async ({ action, package_ids }: { action: string; package_ids: number[] }) => {
      const response = await axios.post('/api/admin/packages/bulk-action/', {
        action,
        package_ids,
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['admin-packages'] });
      setSelectedPackages([]);
      setBulkActionDialog(false);
      enqueueSnackbar(data.message, { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('خطا در انجام عملیات گروهی', { variant: 'error' });
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

  const handleDelete = (packageId: number) => {
    if (window.confirm('آیا از حذف این پکیج اطمینان دارید؟')) {
      deleteMutation.mutate(packageId);
    }
  };

  const handleBulkAction = () => {
    if (selectedPackages.length === 0) {
      enqueueSnackbar('لطفاً حداقل یک پکیج انتخاب کنید', { variant: 'warning' });
      return;
    }
    if (!bulkAction) {
      enqueueSnackbar('لطفاً عملیات مورد نظر را انتخاب کنید', { variant: 'warning' });
      return;
    }
    bulkActionMutation.mutate({ action: bulkAction, package_ids: selectedPackages });
  };

  const handleSelectPackage = (packageId: number) => {
    setSelectedPackages(prev => 
      prev.includes(packageId) 
        ? prev.filter(id => id !== packageId)
        : [...prev, packageId]
    );
  };

  const handleSelectAll = () => {
    if (selectedPackages.length === packages.length) {
      setSelectedPackages([]);
    } else {
      setSelectedPackages(packages.map((pkg: Package) => pkg.id));
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            مدیریت پکیج‌ها
          </Typography>
          <Typography variant="body1" color="text.secondary">
            مشاهده و مدیریت پکیج‌های آموزشی
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {selectedPackages.length > 0 && (
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => setBulkActionDialog(true)}
            >
              عملیات گروهی ({selectedPackages.length})
            </Button>
          )}
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            size="large"
            onClick={() => navigate('/admin-panel/packages/new')}
          >
            افزودن پکیج جدید
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Box sx={{ mb: 3, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(4, 1fr)' }, gap: 2 }}>
        <TextField
          id="search-filter"
          fullWidth
          placeholder="جستجو بر اساس عنوان..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <FormControl fullWidth>
          <InputLabel>وضعیت</InputLabel>
          <Select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            label="وضعیت"
          >
            <MenuItem value="">همه</MenuItem>
            <MenuItem value="published">منتشر شده</MenuItem>
            <MenuItem value="draft">پیش‌نویس</MenuItem>
            <MenuItem value="archived">بایگانی شده</MenuItem>
          </Select>
        </FormControl>
        <FormControl fullWidth>
          <InputLabel>دسته‌بندی</InputLabel>
          <Select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            label="دسته‌بندی"
          >
            <MenuItem value="">همه</MenuItem>
            {categories.map((category: any) => (
              <MenuItem key={category.id} value={category.id}>
                {category.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl fullWidth>
          <InputLabel>ویژه</InputLabel>
          <Select
            value={filters.is_featured}
            onChange={(e) => setFilters({ ...filters, is_featured: e.target.value })}
            label="ویژه"
          >
            <MenuItem value="">همه</MenuItem>
            <MenuItem value="true">ویژه</MenuItem>
            <MenuItem value="false">عادی</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Packages Grid */}
      {isLoading ? (
        <Typography>در حال بارگذاری...</Typography>
      ) : packages.length === 0 ? (
        <Typography align="center" color="text.secondary" sx={{ py: 4 }}>
          هیچ پکیجی یافت نشد
        </Typography>
      ) : (
        <Box>
          {/* Select All */}
          <Box sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={selectedPackages.length === packages.length}
                  indeterminate={selectedPackages.length > 0 && selectedPackages.length < packages.length}
                  onChange={handleSelectAll}
                />
              }
              label={`انتخاب همه (${selectedPackages.length}/${packages.length})`}
            />
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
            {packages.map((pkg: Package) => (
                <Card
                  key={pkg.id}
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
                  <Box sx={{ position: 'relative' }}>
                    <CardMedia
                      component="img"
                      height="200"
                      image={pkg.thumbnail || '/static/images/package-placeholder.png'}
                      alt={pkg.title}
                      sx={{ objectFit: 'cover' }}
                    />
                    <Box sx={{ position: 'absolute', top: 8, left: 8, display: 'flex', gap: 1 }}>
                      <Chip
                        label={getStatusLabel(pkg.status)}
                        color={getStatusColor(pkg.status)}
                        size="small"
                      />
                      {pkg.is_featured && (
                        <Chip label="ویژه" color="secondary" size="small" />
                      )}
                    </Box>
                    <Box sx={{ position: 'absolute', top: 8, right: 8 }}>
                      <Checkbox
                        checked={selectedPackages.includes(pkg.id)}
                        onChange={() => handleSelectPackage(pkg.id)}
                        sx={{ color: 'white' }}
                      />
                    </Box>
                  </Box>
                  
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h6" component="div" sx={{ fontWeight: 600 }}>
                      {pkg.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {pkg.short_description?.substring(0, 100)}
                      {pkg.short_description?.length > 100 ? '...' : ''}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: pkg.category?.color || '#007bff',
                        }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {pkg.category?.name || 'بدون دسته‌بندی'}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <SchoolIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {pkg.total_courses} دوره
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <PeopleIcon fontSize="small" color="action" />
                      <Typography variant="body2" color="text.secondary">
                        {pkg.purchase_count} خرید
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="h6" color="primary" sx={{ fontWeight: 700 }}>
                        {pkg.discount_price ? (
                          <>
                            <Typography
                              component="span"
                              variant="body2"
                              sx={{ textDecoration: 'line-through', ml: 1, color: 'text.secondary' }}
                            >
                              {formatPrice(pkg.price)}
                            </Typography>
                            {formatPrice(pkg.discount_price)} تومان
                          </>
                        ) : (
                          `${formatPrice(pkg.price)} تومان`
                        )}
                      </Typography>
                      {pkg.savings_amount > 0 && (
                        <Chip
                          label={`صرفه‌جویی ${formatPrice(pkg.savings_amount)} تومان`}
                          color="success"
                          size="small"
                        />
                      )}
                    </Box>
                  </CardContent>
                  
                  <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="مشاهده">
                        <IconButton 
                          size="small" 
                          color="info"
                          onClick={() => navigate(`/admin-panel/packages/${pkg.id}`)}
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="ویرایش">
                        <IconButton 
                          size="small" 
                          color="primary"
                          onClick={() => navigate(`/admin-panel/packages/${pkg.id}/edit`)}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="حذف">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDelete(pkg.id)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </CardActions>
                </Card>
            ))}
          </Box>
        </Box>
      )}

      {/* Bulk Action Dialog */}
      <Dialog open={bulkActionDialog} onClose={() => setBulkActionDialog(false)}>
        <DialogTitle>عملیات گروهی</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>عملیات</InputLabel>
            <Select
              value={bulkAction}
              onChange={(e) => setBulkAction(e.target.value)}
              label="عملیات"
            >
              <MenuItem value="publish">انتشار</MenuItem>
              <MenuItem value="archive">بایگانی</MenuItem>
              <MenuItem value="delete">حذف</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkActionDialog(false)}>انصراف</Button>
          <Button 
            onClick={handleBulkAction} 
            variant="contained"
            disabled={bulkActionMutation.isPending}
          >
            {bulkActionMutation.isPending ? 'در حال انجام...' : 'انجام عملیات'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PackagesList;
