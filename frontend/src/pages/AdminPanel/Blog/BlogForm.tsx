import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Autocomplete,
  Chip,
  Alert,
  CircularProgress,
  Stack,
  FormHelperText,
} from '@mui/material';
import {
  Save as SaveIcon,
  Preview as PreviewIcon,
  ArrowBack as BackIcon,
  ArrowForward as ForwardIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useSnackbar } from 'notistack';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { faIR } from 'date-fns/locale/fa-IR';
import { blogPostApi, blogCategoryApi, blogTagApi, BlogPost, BlogCategory, BlogTag, blogUtils } from '../../../services/blogAdminApi';
import RichTextEditor from '../../../components/Admin/Blog/RichTextEditor';
import ImageUploader from '../../../components/Admin/Blog/ImageUploader';

const steps = [
  'اطلاعات پایه',
  'محتوای پست',
  'رسانه',
  'تنظیمات',
  'سئو',
];

const schema = yup.object({
  title: yup.string().required('عنوان الزامی است'),
  slug: yup.string().required('نامک الزامی است'),
  excerpt: yup.string().required('خلاصه الزامی است'),
  content: yup.string().required('محتوا الزامی است'),
  category: yup.number().nullable().test('category-required', 'دسته‌بندی الزامی است', function(value) {
    return value !== undefined && value !== null && value > 0;
  }),
  tags: yup.array().of(yup.number()),
  status: yup.string().oneOf(['draft', 'published', 'archived']).required(),
  is_featured: yup.boolean(),
  allow_comments: yup.boolean(),
  published_at: yup.string(),
  meta_title: yup.string(),
  meta_description: yup.string(),
  featured_image: yup.string(),
});

type FormData = yup.InferType<typeof schema>;

const BlogForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [activeStep, setActiveStep] = useState(0);
  const [previewOpen, setPreviewOpen] = useState(false);

  const isEdit = Boolean(id);

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isDirty },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    mode: 'onBlur',
    reValidateMode: 'onChange',
    defaultValues: {
      title: '',
      slug: '',
      excerpt: '',
      content: '',
      category: undefined,
      tags: [],
      status: 'draft',
      is_featured: false,
      allow_comments: true,
      published_at: '',
      meta_title: '',
      meta_description: '',
      featured_image: '',
    },
  });

  // Debug form errors
  useEffect(() => {
    if (Object.keys(errors).length > 0) {
      console.log('Form validation errors:', errors);
      console.log('Current form values:', watch());
    }
  }, [errors, watch]);

  const watchedTitle = watch('title');
  const watchedStatus = watch('status');

  // Auto-generate slug from title
  useEffect(() => {
    if (watchedTitle && !isEdit) {
      const slug = blogUtils.generateSlug(watchedTitle);
      setValue('slug', slug);
    }
  }, [watchedTitle, setValue, isEdit]);

  // Fetch post data for editing
  const { data: postData, isLoading: isLoadingPost } = useQuery({
    queryKey: ['admin-blog-post', id],
    queryFn: () => blogPostApi.getPost(Number(id)),
    enabled: isEdit,
  });

  // Fetch categories and tags
  const { data: categoriesData = [] } = useQuery({
    queryKey: ['admin-blog-categories'],
    queryFn: () => blogCategoryApi.getCategories(),
  });

  const { data: tagsData = [] } = useQuery({
    queryKey: ['admin-blog-tags'],
    queryFn: () => blogTagApi.getTags(),
  });

  // Ensure categories and tags are always arrays
  const categories = Array.isArray(categoriesData) ? categoriesData : [];
  const tags = Array.isArray(tagsData) ? tagsData : [];

  // Populate form with post data
  useEffect(() => {
    if (postData && isEdit) {
      console.log('Populating form with post data:', postData);
      setValue('title', postData.title || '');
      setValue('slug', postData.slug || '');
      setValue('excerpt', postData.excerpt || '');
      setValue('content', postData.content || '');
      setValue('category', postData.category || undefined);
      setValue('tags', Array.isArray(postData.tags) ? postData.tags : []);
      setValue('status', postData.status || 'draft');
      setValue('is_featured', postData.is_featured || false);
      setValue('allow_comments', postData.allow_comments !== undefined ? postData.allow_comments : true);
      setValue('published_at', postData.published_at || '');
      setValue('meta_title', postData.meta_title || '');
      setValue('meta_description', postData.meta_description || '');
      setValue('featured_image', postData.featured_image || '');
    }
  }, [postData, setValue, isEdit]);

  // Create/Update mutation
  const saveMutation = useMutation({
    mutationFn: (data: FormData) => {
      console.log('Mutation called with data:', data);
      if (isEdit) {
        console.log('Updating post with ID:', id);
        return blogPostApi.updatePost(Number(id), data as any);
      } else {
        console.log('Creating new post');
        return blogPostApi.createPost(data as any);
      }
    },
    onSuccess: (data) => {
      enqueueSnackbar(
        isEdit ? 'پست با موفقیت به‌روزرسانی شد' : 'پست با موفقیت ایجاد شد',
        { variant: 'success' }
      );
      queryClient.invalidateQueries({ queryKey: ['admin-blog-posts'] });
      navigate('/admin-panel/blog');
    },
    onError: (error: any) => {
      console.error('Save mutation error:', error);
      enqueueSnackbar(
        error.response?.data?.error || 'خطا در ذخیره پست',
        { variant: 'error' }
      );
    },
  });

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSave = (data: FormData) => {
    console.log('Form submitted with data:', data);
    saveMutation.mutate(data);
  };

  const handleSaveDraft = () => {
    const currentData = watch();
    saveMutation.mutate({ ...currentData, status: 'draft' });
  };

  const handlePublish = () => {
    const currentData = watch();
    saveMutation.mutate({ 
      ...currentData, 
      status: 'published',
      published_at: new Date().toISOString(),
    });
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Controller
              name="title"
              control={control}
              render={({ field: { value, ...fieldProps } }) => (
                <TextField
                  {...fieldProps}
                  value={value || ''}
                  label="عنوان پست"
                  fullWidth
                  error={!!errors.title}
                  helperText={errors.title?.message}
                  placeholder="عنوان جذاب و واضح برای پست خود بنویسید"
                />
              )}
            />

            <Controller
              name="slug"
              control={control}
              render={({ field: { value, ...fieldProps } }) => (
                <TextField
                  {...fieldProps}
                  value={value || ''}
                  label="نامک (URL)"
                  fullWidth
                  error={!!errors.slug}
                  helperText={errors.slug?.message || 'آدرس اینترنتی پست شما'}
                  placeholder="post-url-slug"
                />
              )}
            />

            <Controller
              name="excerpt"
              control={control}
              render={({ field: { value, ...fieldProps } }) => (
                <TextField
                  {...fieldProps}
                  value={value ?? ''}
                  label="خلاصه"
                  fullWidth
                  multiline
                  rows={3}
                  error={!!errors.excerpt}
                  helperText={errors.excerpt?.message || 'خلاصه کوتاه از محتوای پست'}
                  placeholder="خلاصه‌ای از محتوای پست بنویسید..."
                />
              )}
            />
          </Box>
        );

      case 1:
        return (
          <Box>
            <Controller
              name="content"
              control={control}
              render={({ field: { value, onChange } }) => (
                <RichTextEditor
                  value={value || ''}
                  onChange={onChange}
                  error={!!errors.content}
                  helperText={errors.content?.message}
                />
              )}
            />
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              تصویر شاخص
            </Typography>
            <Controller
              name="featured_image"
              control={control}
              render={({ field: { value, onChange } }) => (
                <ImageUploader
                  value={value || ''}
                  onChange={onChange}
                />
              )}
            />
          </Box>
        );

      case 3:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Controller
              name="category"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth error={!!errors.category}>
                  <InputLabel>دسته‌بندی</InputLabel>
                  <Select 
                    {...field} 
                    label="دسته‌بندی"
                    value={field.value ?? ''}
                    error={!!errors.category}
                    displayEmpty
                  >
                    <MenuItem value="" disabled>
                      <em>انتخاب دسته‌بندی</em>
                    </MenuItem>
                    {(categories || []).map((category: BlogCategory) => (
                      <MenuItem key={category.id} value={category.id}>
                        {category.name}
                      </MenuItem>
                    ))}
                  </Select>
                  {errors.category && (
                    <FormHelperText error>
                      {errors.category.message}
                    </FormHelperText>
                  )}
                </FormControl>
              )}
            />

            <Controller
              name="tags"
              control={control}
              render={({ field }) => (
                <Autocomplete
                  multiple
                  options={tags || []}
                  getOptionLabel={(option) => option.name}
                  value={(tags || []).filter((tag: BlogTag) => (Array.isArray(field.value) ? field.value : []).includes(tag.id!))}
                  onChange={(_, newValue) => {
                    field.onChange(newValue.map((tag: BlogTag) => tag.id!));
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
                      placeholder="انتخاب برچسب‌ها"
                    />
                  )}
                />
              )}
            />

            <Controller
              name="status"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth>
                  <InputLabel>وضعیت</InputLabel>
                  <Select {...field} label="وضعیت">
                    <MenuItem value="draft">پیش‌نویس</MenuItem>
                    <MenuItem value="published">منتشر شده</MenuItem>
                    <MenuItem value="archived">بایگانی</MenuItem>
                  </Select>
                </FormControl>
              )}
            />

            <Controller
              name="published_at"
              control={control}
              render={({ field }) => (
                <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={faIR}>
                  <DatePicker
                    label="تاریخ انتشار"
                    value={field.value ? new Date(field.value) : null}
                    onChange={(date: any) => field.onChange(date ? date.toISOString() : '')}
                    slotProps={{
                      textField: {
                        fullWidth: true
                      }
                    }}
                  />
                </LocalizationProvider>
              )}
            />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Controller
                name="is_featured"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={
                      <Switch
                        checked={field.value}
                        onChange={field.onChange}
                      />
                    }
                    label="پست ویژه"
                  />
                )}
              />

              <Controller
                name="allow_comments"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={
                      <Switch
                        checked={field.value}
                        onChange={field.onChange}
                      />
                    }
                    label="اجازه نظر دادن"
                  />
                )}
              />
            </Box>
          </Box>
        );

      case 4:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Controller
              name="meta_title"
              control={control}
              render={({ field: { value, ...fieldProps } }) => (
                <TextField
                  {...fieldProps}
                  value={value ?? ''}
                  label="عنوان متا (SEO)"
                  fullWidth
                  helperText="عنوانی که در نتایج جستجو نمایش داده می‌شود"
                  placeholder="عنوان بهینه برای موتورهای جستجو"
                />
              )}
            />

            <Controller
              name="meta_description"
              control={control}
              render={({ field: { value, ...fieldProps } }) => (
                <TextField
                  {...fieldProps}
                  value={value ?? ''}
                  label="توضیحات متا (SEO)"
                  fullWidth
                  multiline
                  rows={3}
                  helperText="توضیح کوتاه که در نتایج جستجو نمایش داده می‌شود"
                  placeholder="توضیح مختصر و جذاب از محتوای پست"
                />
              )}
            />
          </Box>
        );

      default:
        return null;
    }
  };

  if (isLoadingPost) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {isEdit ? 'ویرایش پست' : 'پست جدید'}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<PreviewIcon />}
            onClick={() => setPreviewOpen(true)}
          >
            پیش‌نمایش
          </Button>
          <Button
            variant="outlined"
            onClick={handleSaveDraft}
            disabled={saveMutation.isPending}
          >
            ذخیره پیش‌نویس
          </Button>
          <Button
            variant="contained"
            onClick={handlePublish}
            disabled={saveMutation.isPending}
          >
            انتشار
          </Button>
        </Box>
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
          <form onSubmit={handleSubmit(handleSave)}>
            {renderStepContent(activeStep)}

            {/* Navigation Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
              <Button
                disabled={activeStep === 0}
                onClick={handleBack}
                startIcon={<BackIcon />}
              >
                قبلی
              </Button>

              <Box sx={{ display: 'flex', gap: 1 }}>
                {activeStep === steps.length - 1 ? (
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<SaveIcon />}
                    disabled={saveMutation.isPending}
                    onClick={() => console.log('Update button clicked')}
                  >
                    {saveMutation.isPending ? (
                      <CircularProgress size={20} />
                    ) : (
                      isEdit ? 'به‌روزرسانی' : 'ایجاد'
                    )}
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    onClick={handleNext}
                    endIcon={<ForwardIcon />}
                  >
                    بعدی
                  </Button>
                )}
              </Box>
            </Box>
          </form>
        </CardContent>
      </Card>

      {/* Unsaved Changes Warning */}
      {isDirty && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          تغییرات ذخیره نشده‌ای دارید. لطفاً قبل از ترک صفحه، تغییرات را ذخیره کنید.
        </Alert>
      )}
    </Box>
  );
};

export default BlogForm;
