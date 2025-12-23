import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  Autocomplete,
  Chip,
  FormControlLabel,
  Switch,
  Paper,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Save as SaveIcon,
  ArrowBack as BackIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useSnackbar } from 'notistack';

interface Course {
  id: number;
  title: string;
  instructor_name: string;
  current_price: number;
  thumbnail?: string;
}

interface Category {
  id: number;
  name: string;
  color: string;
}

interface PackageFormData {
  title: string;
  slug: string;
  description: string;
  short_description: string;
  category: number | null;
  status: string;
  price: number;
  discount_price?: number;
  is_featured: boolean;
  duration_months: number;
  language: string;
  prerequisites: string;
  learning_objectives: string;
  meta_title: string;
  meta_description: string;
  course_ids: number[];
  thumbnail?: File;
  intro_video?: File;
}

const steps = [
  'اطلاعات پایه',
  'قیمت‌گذاری',
  'انتخاب دوره‌ها',
  'جزئیات',
  'رسانه',
  'سئو'
];

const PackageForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<PackageFormData>({
    title: '',
    slug: '',
    description: '',
    short_description: '',
    category: null,
    status: 'draft',
    price: 0,
    discount_price: 0,
    is_featured: false,
    duration_months: 1,
    language: 'fa',
    prerequisites: '',
    learning_objectives: '',
    meta_title: '',
    meta_description: '',
    course_ids: [],
  });
  
  const [courseSearch, setCourseSearch] = useState('');
  const [courseDialog, setCourseDialog] = useState(false);

  const isEdit = Boolean(id);

  // Fetch package data for editing
  const { data: packageData, isLoading: packageLoading } = useQuery({
    queryKey: ['admin-package', id],
    queryFn: async () => {
      const response = await axios.get(`/api/admin/packages/${id}/`);
      return response.data;
    },
    enabled: isEdit,
  });

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ['admin-package-categories'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/packages/categories/');
      return response.data.results || response.data;
    },
  });

  // Fetch courses for selection
  const { data: courses = [] } = useQuery({
    queryKey: ['admin-courses', courseSearch],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (courseSearch) params.append('search', courseSearch);
      const response = await axios.get(`/api/admin/courses/?${params}`);
      return response.data.results || response.data;
    },
  });

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: async (data: PackageFormData) => {
      const formDataToSend = new FormData();
      
      // Add all form fields
      Object.entries(data).forEach(([key, value]) => {
        if (key === 'thumbnail' || key === 'intro_video') {
          if (value) formDataToSend.append(key, value);
        } else if (key === 'course_ids') {
          if (Array.isArray(value)) {
            value.forEach((id: any, index: number) => formDataToSend.append(`course_ids[${index}]`, id.toString()));
          }
        } else if (value !== null && value !== undefined) {
          formDataToSend.append(key, value.toString());
        }
      });

      if (isEdit) {
        const response = await axios.put(`/api/admin/packages/${id}/`, formDataToSend, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
      } else {
        const response = await axios.post('/api/admin/packages/', formDataToSend, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
      }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['admin-packages'] });
      enqueueSnackbar(
        isEdit ? 'پکیج با موفقیت بروزرسانی شد' : 'پکیج با موفقیت ایجاد شد',
        { variant: 'success' }
      );
      navigate('/admin-panel/packages');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'خطا در ذخیره پکیج';
      enqueueSnackbar(message, { variant: 'error' });
    },
  });

  // Load package data for editing
  useEffect(() => {
    if (packageData) {
      setFormData({
        title: packageData.title || '',
        slug: packageData.slug || '',
        description: packageData.description || '',
        short_description: packageData.short_description || '',
        category: packageData.category?.id || null,
        status: packageData.status || 'draft',
        price: packageData.price || 0,
        discount_price: packageData.discount_price || 0,
        is_featured: packageData.is_featured || false,
        duration_months: packageData.duration_months || 1,
        language: packageData.language || 'fa',
        prerequisites: packageData.prerequisites || '',
        learning_objectives: packageData.learning_objectives || '',
        meta_title: packageData.meta_title || '',
        meta_description: packageData.meta_description || '',
        course_ids: packageData.courses?.map((c: Course) => c.id) || [],
      });
    }
  }, [packageData]);

  const handleInputChange = (field: keyof PackageFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleSave = () => {
    saveMutation.mutate(formData);
  };

  const handleFileUpload = (field: 'thumbnail' | 'intro_video', file: File) => {
    setFormData(prev => ({ ...prev, [field]: file }));
  };

  const handleAddCourse = (course: Course) => {
    if (!formData.course_ids.includes(course.id)) {
      setFormData(prev => ({
        ...prev,
        course_ids: [...prev.course_ids, course.id]
      }));
    }
    setCourseDialog(false);
  };

  const handleRemoveCourse = (courseId: number) => {
    setFormData(prev => ({
      ...prev,
      course_ids: prev.course_ids.filter(id => id !== courseId)
    }));
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              id="package-title"
              fullWidth
              label="عنوان پکیج"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              required
              InputLabelProps={{
                htmlFor: 'package-title'
              }}
            />
            <TextField
              id="package-slug"
              fullWidth
              label="نامک (Slug)"
              value={formData.slug}
              onChange={(e) => handleInputChange('slug', e.target.value)}
              helperText="برای URL استفاده می‌شود"
              InputLabelProps={{
                htmlFor: 'package-slug'
              }}
            />
            <TextField
              id="package-short-description"
              fullWidth
              label="توضیحات کوتاه"
              value={formData.short_description}
              onChange={(e) => handleInputChange('short_description', e.target.value)}
              multiline
              rows={3}
              InputLabelProps={{
                htmlFor: 'package-short-description'
              }}
            />
            <TextField
              id="package-description"
              fullWidth
              label="توضیحات کامل"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              multiline
              rows={5}
              InputLabelProps={{
                htmlFor: 'package-description'
              }}
            />
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 3 }}>
              <FormControl fullWidth>
                <InputLabel>دسته‌بندی</InputLabel>
                <Select
                  value={formData.category || ''}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  label="دسته‌بندی"
                >
                  {categories.map((category: Category) => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>وضعیت</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                  label="وضعیت"
                >
                  <MenuItem value="draft">پیش‌نویس</MenuItem>
                  <MenuItem value="published">منتشر شده</MenuItem>
                  <MenuItem value="archived">بایگانی شده</MenuItem>
                </Select>
              </FormControl>
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_featured}
                  onChange={(e) => handleInputChange('is_featured', e.target.checked)}
                />
              }
              label="پکیج ویژه"
            />
          </Box>
        );

      case 1:
        return (
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 3 }}>
            <TextField
              id="package-price"
              fullWidth
              label="قیمت (تومان)"
              type="number"
              value={formData.price}
              onChange={(e) => handleInputChange('price', parseFloat(e.target.value) || 0)}
              required
              InputLabelProps={{
                htmlFor: 'package-price'
              }}
            />
            <TextField
              id="package-discount-price"
              fullWidth
              label="قیمت تخفیف (تومان)"
              type="number"
              value={formData.discount_price || ''}
              onChange={(e) => handleInputChange('discount_price', parseFloat(e.target.value) || 0)}
              InputLabelProps={{
                htmlFor: 'package-discount-price'
              }}
            />
            <TextField
              id="package-duration"
              fullWidth
              label="مدت زمان (ماه)"
              type="number"
              value={formData.duration_months}
              onChange={(e) => handleInputChange('duration_months', parseInt(e.target.value) || 1)}
              required
              InputLabelProps={{
                htmlFor: 'package-duration'
              }}
            />
            <FormControl fullWidth>
              <InputLabel>زبان</InputLabel>
              <Select
                value={formData.language}
                onChange={(e) => handleInputChange('language', e.target.value)}
                label="زبان"
              >
                <MenuItem value="fa">فارسی</MenuItem>
                <MenuItem value="en">انگلیسی</MenuItem>
              </Select>
            </FormControl>
          </Box>
        );

      case 2:
        return (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">دوره‌های پکیج</Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setCourseDialog(true)}
              >
                افزودن دوره
              </Button>
            </Box>
            
            {formData.course_ids.length > 0 ? (
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 2 }}>
                {formData.course_ids.map(courseId => {
                  const course = courses.find((c: Course) => c.id === courseId);
                  if (!course) return null;
                  
                  return (
                    <Paper key={courseId} sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar src={course.thumbnail} sx={{ width: 40, height: 40 }}>
                        <SchoolIcon />
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle2">{course.title}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {course.instructor_name}
                        </Typography>
                        <Typography variant="body2" color="primary">
                          {new Intl.NumberFormat('fa-IR').format(course.current_price)} تومان
                        </Typography>
                      </Box>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleRemoveCourse(courseId)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Paper>
                  );
                })}
              </Box>
            ) : (
              <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
                هیچ دوره‌ای انتخاب نشده است
              </Typography>
            )}
          </Box>
        );

      case 3:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              id="package-prerequisites"
              fullWidth
              label="پیش‌نیازها"
              value={formData.prerequisites}
              onChange={(e) => handleInputChange('prerequisites', e.target.value)}
              multiline
              rows={4}
              InputLabelProps={{
                htmlFor: 'package-prerequisites'
              }}
            />
            <TextField
              id="package-learning-objectives"
              fullWidth
              label="اهداف یادگیری"
              value={formData.learning_objectives}
              onChange={(e) => handleInputChange('learning_objectives', e.target.value)}
              multiline
              rows={4}
              required
              InputLabelProps={{
                htmlFor: 'package-learning-objectives'
              }}
            />
          </Box>
        );

      case 4:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>تصویر کوچک</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<UploadIcon />}
                >
                  انتخاب تصویر
                  <input
                    type="file"
                    hidden
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload('thumbnail', file);
                    }}
                  />
                </Button>
                {formData.thumbnail && (
                  <Typography variant="body2">
                    {formData.thumbnail.name}
                  </Typography>
                )}
              </Box>
            </Box>
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>ویدیو معرفی</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<UploadIcon />}
                >
                  انتخاب ویدیو
                  <input
                    type="file"
                    hidden
                    accept="video/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload('intro_video', file);
                    }}
                  />
                </Button>
                {formData.intro_video && (
                  <Typography variant="body2">
                    {formData.intro_video.name}
                  </Typography>
                )}
              </Box>
            </Box>
          </Box>
        );

      case 5:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              id="package-meta-title"
              fullWidth
              label="عنوان متا"
              value={formData.meta_title}
              onChange={(e) => handleInputChange('meta_title', e.target.value)}
              helperText="برای موتورهای جستجو"
              InputLabelProps={{
                htmlFor: 'package-meta-title'
              }}
            />
            <TextField
              id="package-meta-description"
              fullWidth
              label="توضیحات متا"
              value={formData.meta_description}
              onChange={(e) => handleInputChange('meta_description', e.target.value)}
              multiline
              rows={3}
              helperText="برای موتورهای جستجو"
              InputLabelProps={{
                htmlFor: 'package-meta-description'
              }}
            />
          </Box>
        );

      default:
        return null;
    }
  };

  if (packageLoading) {
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
          {isEdit ? 'ویرایش پکیج' : 'ایجاد پکیج جدید'}
        </Typography>
      </Box>

      {/* Stepper */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>

      {/* Form Content */}
      <Card>
        <CardContent>
          {getStepContent(activeStep)}
        </CardContent>
      </Card>

      {/* Navigation */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button
          disabled={activeStep === 0}
          onClick={handleBack}
        >
          قبلی
        </Button>
        <Box>
          {activeStep === steps.length - 1 ? (
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              disabled={saveMutation.isPending}
            >
              {saveMutation.isPending ? 'در حال ذخیره...' : 'ذخیره'}
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleNext}
            >
              بعدی
            </Button>
          )}
        </Box>
      </Box>

      {/* Course Selection Dialog */}
      <Dialog open={courseDialog} onClose={() => setCourseDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>انتخاب دوره</DialogTitle>
        <DialogContent>
          <TextField
            id="course-search"
            fullWidth
            label="جستجو دوره"
            value={courseSearch}
            onChange={(e) => setCourseSearch(e.target.value)}
            sx={{ mb: 2 }}
            InputLabelProps={{
              htmlFor: 'course-search'
            }}
          />
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 2 }}>
            {courses.map((course: Course) => (
              <Paper
                key={course.id}
                sx={{
                  p: 2,
                  cursor: 'pointer',
                  '&:hover': { backgroundColor: 'action.hover' },
                }}
                onClick={() => handleAddCourse(course)}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar src={course.thumbnail} sx={{ width: 40, height: 40 }}>
                    <SchoolIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle2">{course.title}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {course.instructor_name}
                    </Typography>
                    <Typography variant="body2" color="primary">
                      {new Intl.NumberFormat('fa-IR').format(course.current_price)} تومان
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCourseDialog(false)}>انصراف</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PackageForm;
