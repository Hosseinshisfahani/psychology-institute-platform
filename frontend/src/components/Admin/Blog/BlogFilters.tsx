import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  Autocomplete,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { faIR } from 'date-fns/locale/fa-IR';
import { BlogFilters as BlogFiltersType, BlogCategory, BlogTag } from '../../../services/blogAdminApi';

interface BlogFiltersProps {
  filters: BlogFiltersType;
  onFiltersChange: (filters: BlogFiltersType) => void;
  categories: BlogCategory[];
  tags: BlogTag[];
  authors: Array<{ id: number; name: string; email: string }>;
  onClear: () => void;
}

const BlogFilters: React.FC<BlogFiltersProps> = ({
  filters,
  onFiltersChange,
  categories,
  tags,
  authors,
  onClear,
}) => {
  const [expanded, setExpanded] = useState(false);

  const handleFilterChange = (key: keyof BlogFiltersType, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    });
  };

  const handleClear = () => {
    onClear();
    setExpanded(false);
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.status) count++;
    if (filters.category) count++;
    if (filters.author) count++;
    if (filters.is_featured !== undefined) count++;
    if (filters.tags && filters.tags.length > 0) count++;
    if (filters.date_from) count++;
    if (filters.date_to) count++;
    if (filters.search) count++;
    return count;
  };

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterIcon />
            <Typography variant="h6">
              فیلترها
              {activeFiltersCount > 0 && (
                <Chip
                  label={activeFiltersCount}
                  size="small"
                  color="primary"
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
          </Box>
          <Box>
            <IconButton
              onClick={() => setExpanded(!expanded)}
              size="small"
            >
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
            {activeFiltersCount > 0 && (
              <IconButton onClick={handleClear} size="small" color="error">
                <ClearIcon />
              </IconButton>
            )}
          </Box>
        </Box>

        <Collapse in={expanded}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* First Row */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {/* Search */}
              <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
                <TextField
                  fullWidth
                  label="جستجو"
                  placeholder="جستجو در عنوان، محتوا و خلاصه..."
                  value={filters.search || ''}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  size="small"
                />
              </Box>

              {/* Status */}
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <FormControl fullWidth size="small">
                  <InputLabel>وضعیت</InputLabel>
                  <Select
                    value={filters.status || ''}
                    onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
                    label="وضعیت"
                  >
                    <MenuItem value="">همه</MenuItem>
                    <MenuItem value="draft">پیش‌نویس</MenuItem>
                    <MenuItem value="published">منتشر شده</MenuItem>
                    <MenuItem value="archived">بایگانی</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              {/* Category */}
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <FormControl fullWidth size="small">
                  <InputLabel>دسته‌بندی</InputLabel>
                  <Select
                    value={filters.category || ''}
                    onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
                    label="دسته‌بندی"
                  >
                    <MenuItem value="">همه</MenuItem>
                    {categories?.map((category) => (
                      <MenuItem key={category.id} value={category.id}>
                        {category.name}
                      </MenuItem>
                    )) || []}
                  </Select>
                </FormControl>
              </Box>
            </Box>

            {/* Second Row */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {/* Author */}
              <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
                <FormControl fullWidth size="small">
                  <InputLabel>نویسنده</InputLabel>
                  <Select
                    value={filters.author || ''}
                    onChange={(e) => handleFilterChange('author', e.target.value || undefined)}
                    label="نویسنده"
                  >
                    <MenuItem value="">همه</MenuItem>
                    {authors?.map((author) => (
                      <MenuItem key={author.id} value={author.id}>
                        {author.name}
                      </MenuItem>
                    )) || []}
                  </Select>
                </FormControl>
              </Box>

              {/* Tags */}
              <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
                <Autocomplete
                  multiple
                  options={tags || []}
                  getOptionLabel={(option) => option.name}
                  value={(tags || []).filter(tag => (Array.isArray(filters.tags) ? filters.tags : []).includes(tag.id!))}
                  onChange={(_, newValue) => {
                    handleFilterChange('tags', newValue.map(tag => tag.id));
                  }}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        {...getTagProps({ index })}
                        key={option.id}
                        label={option.name}
                        size="small"
                      />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="برچسب‌ها"
                      size="small"
                      placeholder="انتخاب برچسب‌ها"
                    />
                  )}
                />
              </Box>

              {/* Featured */}
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <FormControl fullWidth size="small">
                  <InputLabel>ویژه</InputLabel>
                  <Select
                    value={filters.is_featured === undefined ? '' : filters.is_featured}
                    onChange={(e) => handleFilterChange('is_featured', e.target.value === '' ? undefined : e.target.value === 'true')}
                    label="ویژه"
                  >
                    <MenuItem value="">همه</MenuItem>
                    <MenuItem value="true">بله</MenuItem>
                    <MenuItem value="false">خیر</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>

            {/* Date Range Row */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {/* Date From */}
              <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
                <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={faIR}>
                  <DatePicker
                    label="از تاریخ"
                    value={filters.date_from ? new Date(filters.date_from) : null}
                    onChange={(date: any) => handleFilterChange('date_from', date ? date.toISOString().split('T')[0] : undefined)}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        size: 'small'
                      }
                    }}
                  />
                </LocalizationProvider>
              </Box>

              {/* Date To */}
              <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
                <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={faIR}>
                  <DatePicker
                    label="تا تاریخ"
                    value={filters.date_to ? new Date(filters.date_to) : null}
                    onChange={(date: any) => handleFilterChange('date_to', date ? date.toISOString().split('T')[0] : undefined)}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        size: 'small'
                      }
                    }}
                  />
                </LocalizationProvider>
              </Box>
            </Box>

            {/* Clear Button */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
              <Button
                variant="outlined"
                onClick={handleClear}
                startIcon={<ClearIcon />}
                disabled={activeFiltersCount === 0}
              >
                پاک کردن فیلترها
              </Button>
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default BlogFilters;
