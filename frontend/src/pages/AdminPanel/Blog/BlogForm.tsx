import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
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
  Divider,
  FormHelperText,
} from '@mui/material';
import {
  Save as SaveIcon,
  Preview as PreviewIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useSnackbar } from 'notistack';
import DatePicker from 'react-multi-date-picker';
import DateObject from 'react-date-object';
import persian from 'react-date-object/calendars/persian';
import persian_fa from 'react-date-object/locales/persian_fa';
import gregorian from 'react-date-object/calendars/gregorian';
import gregorian_en from 'react-date-object/locales/gregorian_en';
import { blogPostApi, blogCategoryApi, blogTagApi, BlogPost, BlogCategory, BlogTag, blogUtils } from '../../../services/blogAdminApi';
import RichTextEditor from '../../../components/Admin/Blog/RichTextEditor';
import ImageUploader from '../../../components/Admin/Blog/ImageUploader';
import { useAuth } from '../../../contexts/AuthContext';

const schema = yup.object({
  title: yup.string().trim().required('عنوان الزامی است').min(1, 'عنوان نمی‌تواند خالی باشد'),
  slug: yup.string()
    .trim()
    .required('نامک الزامی است')
    .min(1, 'نامک نمی‌تواند خالی باشد')
    .matches(
      /^[a-z0-9_-]+$/,
      'نامک باید فقط شامل حروف انگلیسی، اعداد، خط تیره و زیرخط باشد'
    ),
  excerpt: yup.string().trim().required('خلاصه الزامی است').min(1, 'خلاصه نمی‌تواند خالی باشد'),
  content: yup.string().required('محتوا الزامی است').test('content-not-empty', 'محتوا نمی‌تواند خالی باشد', function(value) {
    if (!value) return false;
    // Check if content is just empty HTML tags
    const stripped = value.replace(/<[^>]*>/g, '').trim();
    return stripped.length > 0;
  }),
  category: yup.number().nullable().test('category-required', 'دسته‌بندی الزامی است', function(value) {
    return value !== undefined && value !== null && value > 0;
  }),
  tags: yup.array().of(yup.number()),
  status: yup.string().oneOf(['draft', 'published', 'archived']).required(),
  is_featured: yup.boolean(),
  allow_comments: yup.boolean(),
  published_at: yup.string().nullable(),
  meta_title: yup.string().nullable(),
  meta_description: yup.string().nullable(),
  featured_image: yup.string().nullable(),
});

type FormData = yup.InferType<typeof schema>;

const BlogForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const { user } = useAuth();
  const [previewOpen, setPreviewOpen] = useState(false);
  const [savedPostId, setSavedPostId] = useState<number | null>(null);

  const isEdit = Boolean(id) || Boolean(savedPostId);

  // localStorage key for draft data
  const DRAFT_STORAGE_KEY = `blog-draft-${id || 'new'}`;

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    trigger,
    getValues,
    formState: { errors, isDirty },
  } = useForm<FormData>({
    resolver: yupResolver(schema),
    mode: 'onChange',
    reValidateMode: 'onChange',
    shouldUnregister: false,
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

  // Save form data to localStorage on every change (debounced)
  useEffect(() => {
    if (!isEdit || !id) {
      // Only save drafts to localStorage, not when editing existing posts
      let timeoutId: NodeJS.Timeout;
      const subscription = watch((value) => {
        // Debounce: save after 1 second of no changes
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          try {
            localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(value));
          } catch (error) {
            console.warn('Failed to save draft to localStorage:', error);
          }
        }, 1000);
      });
      return () => {
        subscription.unsubscribe();
        clearTimeout(timeoutId);
      };
    }
  }, [watch, isEdit, id, DRAFT_STORAGE_KEY]);

  // Load draft from localStorage on mount (for new posts only)
  useEffect(() => {
    if (!isEdit && !id) {
      try {
        const savedDraft = localStorage.getItem(DRAFT_STORAGE_KEY);
        if (savedDraft) {
          const draftData = JSON.parse(savedDraft);
          // Restore form values from localStorage
          Object.keys(draftData).forEach((key) => {
            if (draftData[key] !== undefined && draftData[key] !== null && draftData[key] !== '') {
              setValue(key as keyof FormData, draftData[key]);
            }
          });
          enqueueSnackbar('پیش‌نویس قبلی بازیابی شد', { variant: 'info', autoHideDuration: 3000 });
        }
      } catch (error) {
        console.warn('Failed to load draft from localStorage:', error);
      }
    }
  }, [isEdit, id, setValue, DRAFT_STORAGE_KEY, enqueueSnackbar]);

  // Clear localStorage after successful save
  useEffect(() => {
    if (savedPostId || id) {
      try {
        localStorage.removeItem(DRAFT_STORAGE_KEY);
      } catch (error) {
        console.warn('Failed to clear draft from localStorage:', error);
      }
    }
  }, [savedPostId, id, DRAFT_STORAGE_KEY]);

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
    if (watchedTitle && typeof watchedTitle === 'string' && !isEdit) {
      const slug = blogUtils.generateSlug(watchedTitle);
      if (slug) {
      setValue('slug', slug);
      }
    }
  }, [watchedTitle, setValue, isEdit]);

  // Fetch post data for editing
  const { data: postData, isLoading: isLoadingPost } = useQuery({
    queryKey: ['admin-blog-post', id],
    queryFn: () => blogPostApi.getPost(Number(id)),
    enabled: isEdit,
  });

  // Fetch categories and tags with error handling
  const { data: categoriesData = [], error: categoriesError } = useQuery({
    queryKey: ['admin-blog-categories'],
    queryFn: () => blogCategoryApi.getCategories(),
    retry: 1,
  });

  const { data: tagsData = [], error: tagsError } = useQuery({
    queryKey: ['admin-blog-tags'],
    queryFn: () => blogTagApi.getTags(),
    retry: 1,
  });

  // Ensure categories and tags are always arrays
  const categories = Array.isArray(categoriesData) ? categoriesData : [];
  const tags = Array.isArray(tagsData) ? tagsData : [];

  // Show error alert if permissions are missing
  useEffect(() => {
    if (categoriesError) {
      const error = categoriesError as any;
      if (error?.response?.status === 403) {
        console.warn('403 Forbidden: No permission to access categories. User may need admin access.');
        enqueueSnackbar('خطا در دسترسی به دسته‌بندی‌ها. لطفاً دسترسی‌های خود را بررسی کنید.', {
          variant: 'error',
          autoHideDuration: 6000,
        });
      }
    }
    if (tagsError) {
      const error = tagsError as any;
      if (error?.response?.status === 403) {
        console.warn('403 Forbidden: No permission to access tags. User may need admin access.');
        enqueueSnackbar('خطا در دسترسی به برچسب‌ها. لطفاً دسترسی‌های خود را بررسی کنید.', {
          variant: 'error',
          autoHideDuration: 6000,
        });
      }
    }
  }, [categoriesError, tagsError, enqueueSnackbar]);

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
      // Prepare the data with author field for new posts
      const postData: any = { ...data };
      
      // Determine which ID to use
      const postId = id ? Number(id) : savedPostId;
      
      if (!postId && user?.id) {
        // New post - add author
        postData.author = user.id;
      }
      
      if (postId) {
        console.log('Updating post with ID:', postId);
        return blogPostApi.updatePost(postId, postData);
      } else {
        console.log('Creating new post');
        return blogPostApi.createPost(postData);
      }
    },
    onSuccess: (data) => {
      // Save the post ID if it's a new post
      if (data?.id && !savedPostId && !id) {
        setSavedPostId(data.id);
      }
      
      // Clear localStorage after successful save
      try {
        localStorage.removeItem(DRAFT_STORAGE_KEY);
      } catch (error) {
        console.warn('Failed to clear localStorage:', error);
      }
      
      enqueueSnackbar(
        isEdit ? 'پست با موفقیت به‌روزرسانی شد' : 'پست با موفقیت ایجاد شد',
        { variant: 'success' }
      );
      queryClient.invalidateQueries({ queryKey: ['admin-blog-posts'] });
      navigate('/admin-panel/blog');
    },
    onError: (error: any) => {
      console.error('Save mutation error:', error);
      const errorMessage = error.response?.data?.error 
        || error.response?.data?.message 
        || (typeof error.response?.data === 'object' && error.response?.data !== null
          ? JSON.stringify(error.response.data)
          : 'خطا در ذخیره پست');
      enqueueSnackbar(
        errorMessage,
        { variant: 'error', autoHideDuration: 6000 }
      );
    },
  });


  // Helper function to process featured_image
  // ImageUploader already uploads the file and returns a URL.
  // The backend serializer now handles URL strings for featured_image.
  // We just need to ensure it's in the correct format.
  const processFeaturedImage = (imageValue: any): string | null => {
    // If it's a URL string (already uploaded), send it as is
    // Backend serializer will handle it
    if (imageValue && typeof imageValue === 'string' && imageValue.trim() !== '') {
      return imageValue; // Send the URL string
    }
    // No image or empty, return null
    return null;
  };

  const handleSave = (data: FormData) => {
    console.log('Form submitted with data:', data);
    const postData: any = { ...data };
    const processedImage = processFeaturedImage(postData.featured_image);
    postData.featured_image = processedImage; // Can be URL string or null
    saveMutation.mutate(postData);
  };

  const handleSaveDraft = async () => {
    // Save draft without validation - allow incomplete data
    const currentData = watch();
    
    const postData: any = { ...currentData, status: 'draft' };
    const processedImage = processFeaturedImage(postData.featured_image);
    postData.featured_image = processedImage; // Can be URL string or null
    
    // Show warning if critical fields are missing but still save
    const hasCriticalFields = currentData.title && currentData.category;
    if (!hasCriticalFields) {
      enqueueSnackbar('پیش‌نویس ذخیره شد. لطفاً عنوان و دسته‌بندی را قبل از انتشار تکمیل کنید.', { 
        variant: 'info',
        autoHideDuration: 5000 
      });
    }
    
    saveMutation.mutate(postData);
  };

  // Wrap publish in handleSubmit to let React Hook Form handle validation properly
  const onPublishSubmit = (data: FormData) => {
    console.log('Publishing with validated data:', data);
    
    const postData: any = { ...data, status: 'published' };
    
    // Process featured_image - send URL string if available
    const processedImage = processFeaturedImage(postData.featured_image);
    postData.featured_image = processedImage; // Can be URL string or null
    
    // Add author if new post
    if (!savedPostId && !id && user?.id) {
      postData.author = user.id;
    }
    
    // Set published_at if not already set
    if (!postData.published_at) {
      postData.published_at = new Date().toISOString();
    }
    
    saveMutation.mutate(postData);
  };
  
  const onPublishError = (formErrors: any) => {
    console.log('Publish validation errors:', formErrors);
    
    const missingFields: string[] = [];
    
    if (formErrors.title) missingFields.push('عنوان (مرحله 1)');
    if (formErrors.slug) missingFields.push('نامک (مرحله 1)');
    if (formErrors.excerpt) missingFields.push('خلاصه (مرحله 1)');
    if (formErrors.content) missingFields.push('محتوا (مرحله 2)');
    if (formErrors.category) missingFields.push('دسته‌بندی (مرحله 4)');
    
    if (missingFields.length > 0) {
      enqueueSnackbar(`برای انتشار باید این فیلدها را تکمیل کنید: ${missingFields.join('، ')}`, { 
        variant: 'error',
        autoHideDuration: 5000 
      });
      
      // Scroll to top to show errors
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      enqueueSnackbar('لطفاً خطاهای فرم را برطرف کنید', { 
        variant: 'error',
        autoHideDuration: 5000 
      });
    }
  };
  
  const handlePublish = handleSubmit(onPublishSubmit, onPublishError);


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
        </Box>
      </Box>

      {/* Form Content */}
      <Card>
        <CardContent>
          {/* Validation Errors Alert */}
          {Object.keys(errors).length > 0 && (
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
                ⚠️ برای انتشار پست، این فیلدها را تکمیل کنید:
              </Typography>
              <ul style={{ margin: '0.5rem 0', paddingRight: '1.5rem' }}>
                {errors.title && <li>{errors.title.message}</li>}
                {errors.slug && <li>{errors.slug.message}</li>}
                {errors.excerpt && <li>{errors.excerpt.message}</li>}
                {errors.content && <li>{errors.content.message}</li>}
                {errors.category && <li>{errors.category.message}</li>}
              </ul>
            </Alert>
          )}
          
          <form onSubmit={handleSubmit(handleSave)}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {/* Section 1: Basic Information */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
                  اطلاعات پایه
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <Controller
                    name="title"
                    control={control}
                    render={({ field: { value, ...fieldProps } }) => (
                      <TextField
                        {...fieldProps}
                        value={typeof value === 'string' ? value : ''}
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
                    render={({ field }) => (
                      <TextField
                        {...field}
                        value={typeof field.value === 'string' ? field.value : ''}
                        label="نامک (URL)"
                        fullWidth
                        error={!!errors.slug}
                        helperText={errors.slug?.message || 'آدرس اینترنتی پست شما (فقط حروف انگلیسی، اعداد، خط تیره و زیرخط)'}
                        placeholder="post-url-slug"
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

                  <Controller
                    name="excerpt"
                    control={control}
                    render={({ field: { value, ...fieldProps } }) => (
                      <TextField
                        {...fieldProps}
                        value={typeof value === 'string' ? value : ''}
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
              </Box>

              {/* Section 2: Content */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
                  محتوای پست
                </Typography>
                <Divider sx={{ mb: 3 }} />
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

              {/* Section 3: Media */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
                  رسانه
                </Typography>
                <Divider sx={{ mb: 3 }} />
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

              {/* Section 4: Settings */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
                  تنظیمات
                </Typography>
                <Divider sx={{ mb: 3 }} />
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
                          disabled={!!(categoriesError && (categoriesError as any).response?.status === 403)}
                          onChange={(e) => {
                            const value = e.target.value;
                            if (typeof value === 'string' && value === '') {
                              field.onChange(undefined);
                            } else {
                              const numValue = typeof value === 'number' ? value : Number(value);
                              field.onChange(isNaN(numValue) ? undefined : numValue);
                            }
                          }}
                        >
                          <MenuItem value="" disabled>
                            <em>انتخاب دسته‌بندی</em>
                          </MenuItem>
                          {categoriesError && (categoriesError as any).response?.status === 403 ? (
                            <MenuItem value="" disabled>
                              <em>خطا در بارگذاری دسته‌بندی‌ها</em>
                            </MenuItem>
                          ) : (
                            (categories || []).map((category: BlogCategory) => (
                            <MenuItem key={category.id} value={category.id}>
                              {category.name}
                            </MenuItem>
                            ))
                          )}
                        </Select>
                        {errors.category && (
                          <FormHelperText error>
                            {errors.category.message}
                          </FormHelperText>
                        )}
                        {categoriesError && (categoriesError as any).response?.status === 403 && (
                          <FormHelperText error>
                            دسترسی به دسته‌بندی‌ها امکان‌پذیر نیست. لطفاً با مدیر سیستم تماس بگیرید.
                          </FormHelperText>
                        )}
                      </FormControl>
                    )}
                  />

                  <Controller
                    name="tags"
                    control={control}
                    render={({ field }) => (
                      <Box>
                      <Autocomplete
                        multiple
                          disabled={!!(tagsError && (tagsError as any).response?.status === 403)}
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
                              placeholder={tagsError && (tagsError as any).response?.status === 403 
                                ? "خطا در بارگذاری برچسب‌ها" 
                                : "انتخاب برچسب‌ها"}
                              error={!!tagsError && (tagsError as any).response?.status === 403}
                          />
                        )}
                      />
                        {tagsError && (tagsError as any).response?.status === 403 && (
                          <FormHelperText error sx={{ mt: 0.5 }}>
                            دسترسی به برچسب‌ها امکان‌پذیر نیست. لطفاً با مدیر سیستم تماس بگیرید.
                          </FormHelperText>
                        )}
                      </Box>
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
                      <Box>
                        <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary', fontWeight: 500 }}>
                          تاریخ انتشار
                        </Typography>
                        <Box
                          sx={{
                            border: '1px solid rgba(0, 0, 0, 0.23)',
                            borderRadius: '4px',
                            '&:hover': {
                              borderColor: 'text.primary',
                            },
                            '&:focus-within': {
                              borderColor: 'primary.main',
                              borderWidth: '2px',
                            },
                          }}
                        >
                        <DatePicker
                            calendar={persian}
                            locale={persian_fa}
                            value={
                              field.value
                                ? new DateObject({ date: field.value, calendar: gregorian, locale: gregorian_en })
                                : null
                            }
                            onChange={(date: any) => {
                              if (date) {
                                const dateObj = date instanceof DateObject ? date : new DateObject(date);
                                const gregorianDate = dateObj.convert(gregorian, gregorian_en);
                                field.onChange(gregorianDate.toDate().toISOString());
                              } else {
                                field.onChange('');
                              }
                            }}
                            format="YYYY/MM/DD"
                            inputClass="MuiInputBase-input MuiInput-input"
                            containerClassName="custom-date-picker"
                            style={{
                              width: '100%',
                              height: '56px',
                              padding: '16.5px 14px',
                              background: 'transparent',
                              border: 'none',
                            }}
                            placeholder="تاریخ انتشار را انتخاب کنید"
                        />
                        </Box>
                      </Box>
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
              </Box>

              {/* Section 5: SEO */}
              <Box>
                <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
                  سئو (SEO)
                </Typography>
                <Divider sx={{ mb: 3 }} />
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
                        value={typeof value === 'string' ? value : ''}
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
              </Box>
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 4 }}>
              <Button
                variant="outlined"
                onClick={handleSaveDraft}
                disabled={saveMutation.isPending}
              >
                ذخیره پیش‌نویس
              </Button>
              <Button
                variant="contained"
                color="success"
                onClick={handlePublish}
                disabled={saveMutation.isPending}
                startIcon={saveMutation.isPending ? <CircularProgress size={20} /> : <SaveIcon />}
              >
                {saveMutation.isPending ? 'در حال انتشار...' : 'انتشار'}
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default BlogForm;
