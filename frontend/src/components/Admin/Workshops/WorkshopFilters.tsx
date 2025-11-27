import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Typography,
} from '@mui/material';
import { Clear as ClearIcon, FilterList as FilterIcon } from '@mui/icons-material';
import { WorkshopFilters, WorkshopCategory } from '../../../services/workshopAdminApi';

interface WorkshopFiltersProps {
  filters: WorkshopFilters;
  onFiltersChange: (filters: WorkshopFilters) => void;
  onClear: () => void;
  categories?: WorkshopCategory[];
  instructors?: Array<{ id: number; name: string; email: string }>;
}

const WorkshopFiltersComponent: React.FC<WorkshopFiltersProps> = ({
  filters,
  onFiltersChange,
  onClear,
  categories = [],
  instructors = [],
}) => {
  const [showFilters, setShowFilters] = useState(false);

  const handleFilterChange = (key: keyof WorkshopFilters, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const getActiveFiltersCount = () => {
    return Object.values(filters).filter(value => value !== undefined && value !== '').length;
  };

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Button
          variant="outlined"
          startIcon={<FilterIcon />}
          onClick={() => setShowFilters(!showFilters)}
          sx={{ position: 'relative' }}
        >
          فیلترها
          {activeFiltersCount > 0 && (
            <Chip
              label={activeFiltersCount}
              size="small"
              color="primary"
              sx={{ ml: 1, minWidth: 20, height: 20 }}
            />
          )}
        </Button>
        {activeFiltersCount > 0 && (
          <Button
            variant="text"
            startIcon={<ClearIcon />}
            onClick={onClear}
            color="error"
          >
            پاک کردن فیلترها
          </Button>
        )}
      </Box>

      {showFilters && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 2 }}>
              <Box>
                <TextField
                  fullWidth
                  label="جستجو"
                  placeholder="عنوان، توضیحات، مدرس..."
                  value={filters.search || ''}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                />
              </Box>

              <Box>
                <FormControl fullWidth>
                  <InputLabel>وضعیت</InputLabel>
                  <Select
                    value={filters.status || ''}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    label="وضعیت"
                  >
                    <MenuItem value="">همه</MenuItem>
                    <MenuItem value="draft">پیش‌نویس</MenuItem>
                    <MenuItem value="published">منتشر شده</MenuItem>
                    <MenuItem value="registration_open">ثبت‌نام باز</MenuItem>
                    <MenuItem value="in_progress">در حال برگزاری</MenuItem>
                    <MenuItem value="completed">تکمیل شده</MenuItem>
                    <MenuItem value="cancelled">لغو شده</MenuItem>
                    <MenuItem value="archived">بایگانی</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box>
                <FormControl fullWidth>
                  <InputLabel>دسته‌بندی</InputLabel>
                  <Select
                    value={filters.category || ''}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    label="دسته‌بندی"
                  >
                    <MenuItem value="">همه</MenuItem>
                    {categories.map((category) => (
                      <MenuItem key={category.id} value={category.id}>
                        {category.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Box>
                <FormControl fullWidth>
                  <InputLabel>سطح دشواری</InputLabel>
                  <Select
                    value={filters.difficulty || ''}
                    onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                    label="سطح دشواری"
                  >
                    <MenuItem value="">همه</MenuItem>
                    <MenuItem value="beginner">مبتدی</MenuItem>
                    <MenuItem value="intermediate">متوسط</MenuItem>
                    <MenuItem value="advanced">پیشرفته</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box>
                <FormControl fullWidth>
                  <InputLabel>مدرس</InputLabel>
                  <Select
                    value={filters.instructor || ''}
                    onChange={(e) => handleFilterChange('instructor', e.target.value)}
                    label="مدرس"
                  >
                    <MenuItem value="">همه</MenuItem>
                    {instructors.map((instructor) => (
                      <MenuItem key={instructor.id} value={instructor.id}>
                        {instructor.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Box>
                <FormControl fullWidth>
                  <InputLabel>نوع پرداخت</InputLabel>
                  <Select
                    value={filters.payment_type || ''}
                    onChange={(e) => handleFilterChange('payment_type', e.target.value)}
                    label="نوع پرداخت"
                  >
                    <MenuItem value="">همه</MenuItem>
                    <MenuItem value="full_payment">پرداخت کامل</MenuItem>
                    <MenuItem value="installment">قسطی</MenuItem>
                    <MenuItem value="both">هر دو</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box>
                <TextField
                  fullWidth
                  label="تاریخ شروع از"
                  type="date"
                  value={filters.date_from || ''}
                  onChange={(e) => handleFilterChange('date_from', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Box>

              <Box>
                <TextField
                  fullWidth
                  label="تاریخ پایان تا"
                  type="date"
                  value={filters.date_to || ''}
                  onChange={(e) => handleFilterChange('date_to', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Box>

              <Box>
                <FormControl fullWidth>
                  <InputLabel>مرتب‌سازی</InputLabel>
                  <Select
                    value={filters.ordering || ''}
                    onChange={(e) => handleFilterChange('ordering', e.target.value)}
                    label="مرتب‌سازی"
                  >
                    <MenuItem value="">پیش‌فرض</MenuItem>
                    <MenuItem value="created_at">جدیدترین</MenuItem>
                    <MenuItem value="-created_at">قدیمی‌ترین</MenuItem>
                    <MenuItem value="start_date">تاریخ شروع</MenuItem>
                    <MenuItem value="-start_date">تاریخ شروع (نزولی)</MenuItem>
                    <MenuItem value="price">قیمت</MenuItem>
                    <MenuItem value="-price">قیمت (نزولی)</MenuItem>
                    <MenuItem value="current_participants">تعداد شرکت‌کنندگان</MenuItem>
                    <MenuItem value="-current_participants">تعداد شرکت‌کنندگان (نزولی)</MenuItem>
                    <MenuItem value="rating">امتیاز</MenuItem>
                    <MenuItem value="-rating">امتیاز (نزولی)</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>

            {activeFiltersCount > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  فیلترهای فعال:
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {filters.search && (
                    <Chip
                      label={`جستجو: ${filters.search}`}
                      onDelete={() => handleFilterChange('search', '')}
                      size="small"
                    />
                  )}
                  {filters.status && (
                    <Chip
                      label={`وضعیت: ${filters.status}`}
                      onDelete={() => handleFilterChange('status', '')}
                      size="small"
                    />
                  )}
                  {filters.category && (
                    <Chip
                      label={`دسته‌بندی: ${categories.find(c => c.id === filters.category)?.name || filters.category}`}
                      onDelete={() => handleFilterChange('category', '')}
                      size="small"
                    />
                  )}
                  {filters.difficulty && (
                    <Chip
                      label={`سطح: ${filters.difficulty}`}
                      onDelete={() => handleFilterChange('difficulty', '')}
                      size="small"
                    />
                  )}
                  {filters.instructor && (
                    <Chip
                      label={`مدرس: ${instructors.find(i => i.id === filters.instructor)?.name || filters.instructor}`}
                      onDelete={() => handleFilterChange('instructor', '')}
                      size="small"
                    />
                  )}
                  {filters.payment_type && (
                    <Chip
                      label={`پرداخت: ${filters.payment_type}`}
                      onDelete={() => handleFilterChange('payment_type', '')}
                      size="small"
                    />
                  )}
                  {filters.date_from && (
                    <Chip
                      label={`از: ${filters.date_from}`}
                      onDelete={() => handleFilterChange('date_from', '')}
                      size="small"
                    />
                  )}
                  {filters.date_to && (
                    <Chip
                      label={`تا: ${filters.date_to}`}
                      onDelete={() => handleFilterChange('date_to', '')}
                      size="small"
                    />
                  )}
                </Stack>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default WorkshopFiltersComponent;
