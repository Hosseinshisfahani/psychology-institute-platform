import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://sarmadclinic.ir';

// Create axios instance with default config
// Note: CSRF token is handled by the global axios interceptor in AuthContext
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/admin`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for sending cookies
  xsrfCookieName: 'csrftoken', // CSRF cookie name
  xsrfHeaderName: 'X-CSRFToken', // CSRF header name
});

// Helper to get CSRF token from cookie
const getCsrfToken = () => {
  const name = 'csrftoken=';
  const cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length);
    }
  }
  return '';
};

// Add request interceptor to include CSRF token
api.interceptors.request.use(
  async (config) => {
    // Skip CSRF for the CSRF endpoint itself
    if (config.url?.includes('/csrf/')) {
      return config;
    }

    // If data is FormData, remove Content-Type header to let browser set it with boundary
    if (config.data instanceof FormData) {
      if (config.headers) {
        delete config.headers['Content-Type'];
      }
    }

    // Get CSRF token from cookie
    let csrfToken = getCsrfToken();
    
    // If no CSRF token, try to fetch it first
    if (!csrfToken && typeof window !== 'undefined') {
      try {
        // Use the global axios instance to fetch CSRF token
        await axios.get('/csrf/', {
          baseURL: API_BASE_URL,
          withCredentials: true,
        });
        // Give browser a moment to set the cookie
        await new Promise(resolve => setTimeout(resolve, 10));
        csrfToken = getCsrfToken();
      } catch (error) {
        console.warn('Failed to fetch CSRF token:', error);
      }
    }

    // Add CSRF token to headers if available
    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface BlogPost {
  id?: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  featured_image?: string;
  category: number;
  tags: number[];
  status: 'draft' | 'published' | 'archived';
  author: number;
  author_name?: string;
  author_email?: string;
  category_name?: string;
  category_color?: string;
  tags_data?: Array<{ id: number; name: string; slug: string }>;
  is_featured: boolean;
  allow_comments: boolean;
  view_count: number;
  like_count: number;
  created_at?: string;
  updated_at?: string;
  published_at?: string;
  created_at_persian?: string;
  updated_at_persian?: string;
  published_at_persian?: string;
  status_display?: string;
  post_count?: number;
  meta_title?: string;
  meta_description?: string;
}

export interface BlogCategory {
  id?: number;
  name: string;
  slug: string;
  description?: string;
  color: string;
  icon?: string;
  is_active: boolean;
  post_count?: number;
  created_at?: string;
  updated_at?: string;
  created_at_persian?: string;
  updated_at_persian?: string;
}

export interface BlogTag {
  id?: number;
  name: string;
  slug: string;
  usage_count?: number;
  created_at?: string;
  created_at_persian?: string;
}

export interface BlogComment {
  id?: number;
  post: number;
  post_title?: string;
  post_slug?: string;
  author: number;
  author_name?: string;
  author_email?: string;
  content: string;
  is_approved: boolean;
  is_approved_display?: string;
  parent?: number;
  replies_count?: number;
  created_at?: string;
  updated_at?: string;
  created_at_persian?: string;
  updated_at_persian?: string;
}

export interface BlogFilters {
  status?: string;
  category?: number;
  author?: number;
  is_featured?: boolean;
  tags?: number[];
  date_from?: string;
  date_to?: string;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface CommentFilters {
  is_approved?: boolean;
  post?: number;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

// Blog Posts API
export const blogPostApi = {
  // Get all blog posts with filters
  getPosts: async (filters: BlogFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(item => params.append(key, item.toString()));
        } else {
          params.append(key, value.toString());
        }
      }
    });

    const response = await api.get(`/blog/posts/?${params.toString()}`);
    return response.data;
  },

  // Get single blog post
  getPost: async (id: number) => {
    const response = await api.get(`/blog/posts/${id}/`);
    return response.data;
  },

  // Create new blog post
  createPost: async (data: Partial<BlogPost>) => {
    const response = await api.post('/blog/posts/', data);
    return response.data;
  },

  // Update blog post
  updatePost: async (id: number, data: Partial<BlogPost>) => {
    const response = await api.put(`/blog/posts/${id}/`, data);
    return response.data;
  },

  // Delete blog post
  deletePost: async (id: number) => {
    const response = await api.delete(`/blog/posts/${id}/`);
    return response.data;
  },

  // Bulk actions on posts
  bulkAction: async (action: string, postIds: number[]) => {
    const response = await api.post('/blog/posts/bulk-action/', {
      action,
      post_ids: postIds,
    });
    return response.data;
  },
};

// Blog Categories API
export const blogCategoryApi = {
  // Get all categories
  getCategories: async () => {
    const response = await api.get('/blog/categories/');
    // Handle paginated response - extract results if it exists, otherwise return data directly
    return response.data.results || response.data;
  },

  // Get single category
  getCategory: async (id: number) => {
    const response = await api.get(`/blog/categories/${id}/`);
    return response.data;
  },

  // Create new category
  createCategory: async (data: Partial<BlogCategory>) => {
    const response = await api.post('/blog/categories/', data);
    return response.data;
  },

  // Update category
  updateCategory: async (id: number, data: Partial<BlogCategory>) => {
    const response = await api.put(`/blog/categories/${id}/`, data);
    return response.data;
  },

  // Delete category
  deleteCategory: async (id: number) => {
    const response = await api.delete(`/blog/categories/${id}/`);
    return response.data;
  },
};

// Blog Tags API
export const blogTagApi = {
  // Get all tags
  getTags: async () => {
    const response = await api.get('/blog/tags/');
    // Handle paginated response - extract results if it exists, otherwise return data directly
    return response.data.results || response.data;
  },

  // Get single tag
  getTag: async (id: number) => {
    const response = await api.get(`/blog/tags/${id}/`);
    return response.data;
  },

  // Create new tag
  createTag: async (data: Partial<BlogTag>) => {
    const response = await api.post('/blog/tags/', data);
    return response.data;
  },

  // Update tag
  updateTag: async (id: number, data: Partial<BlogTag>) => {
    const response = await api.put(`/blog/tags/${id}/`, data);
    return response.data;
  },

  // Delete tag
  deleteTag: async (id: number) => {
    const response = await api.delete(`/blog/tags/${id}/`);
    return response.data;
  },
};

// Blog Comments API
export const blogCommentApi = {
  // Get all comments with filters
  getComments: async (filters: CommentFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`/blog/comments/?${params.toString()}`);
    return response.data;
  },

  // Get single comment
  getComment: async (id: number) => {
    const response = await api.get(`/blog/comments/${id}/`);
    return response.data;
  },

  // Update comment (approve/reject)
  updateComment: async (id: number, data: Partial<BlogComment>) => {
    // Use PATCH for partial updates (only send fields that need to be updated)
    const response = await api.patch(`/blog/comments/${id}/`, data);
    return response.data;
  },

  // Delete comment
  deleteComment: async (id: number) => {
    const response = await api.delete(`/blog/comments/${id}/`);
    return response.data;
  },

  // Bulk actions on comments
  bulkAction: async (action: string, commentIds: number[]) => {
    const response = await api.post('/blog/comments/bulk-action/', {
      action,
      comment_ids: commentIds,
    });
    return response.data;
  },
};

// File Upload API
export const fileUploadApi = {
  // Upload file and get URL
  uploadFile: async (file: File): Promise<string> => {
    console.log('📤 Starting file upload:', {
      name: file.name,
      size: file.size,
      type: file.type,
    });
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Ensure CSRF token is available
    let csrfToken = getCsrfToken();
    if (!csrfToken) {
      // Fetch CSRF token if not available
      try {
        console.log('🔑 Fetching CSRF token...');
        await axios.get('/csrf/', {
          baseURL: API_BASE_URL,
          withCredentials: true,
        });
        await new Promise(resolve => setTimeout(resolve, 10));
        csrfToken = getCsrfToken();
        console.log('✅ CSRF token fetched:', csrfToken ? 'Yes' : 'No');
      } catch (error) {
        console.warn('❌ Failed to fetch CSRF token for upload:', error);
      }
    } else {
      console.log('✅ CSRF token already available');
    }
    
    // Don't set Content-Type manually - let axios/browser set it with boundary
    // Only set CSRF token header
    const headers: Record<string, string> = {};
    
    // Explicitly add CSRF token
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
      console.log('🔑 CSRF token added to headers');
    } else {
      console.warn('⚠️ No CSRF token available!');
    }
    
    try {
      console.log('📡 Sending upload request...');
      const response = await api.post('/upload/', formData, {
        headers,
      });
      console.log('✅ Upload successful:', response.data);
      return response.data.url;
    } catch (error: any) {
      console.error('❌ Upload failed:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
      throw error;
    }
  },
};

// Utility functions
export const blogUtils = {
  // Generate slug from title
  // Django SlugField only accepts ASCII letters, numbers, underscores, and hyphens
  generateSlug: (title: string): string => {
    if (!title || typeof title !== 'string') {
      return '';
    }
    
    // Basic Persian to Latin transliteration map for common characters
    const persianToLatin: { [key: string]: string } = {
      'آ': 'a', 'ا': 'a', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ث': 's',
      'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'z',
      'ر': 'r', 'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
      'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f',
      'ق': 'gh', 'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm', 'ن': 'n',
      'و': 'v', 'ه': 'h', 'ی': 'y', 'ي': 'y', 'ئ': 'y', 'ء': '',
      '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
      '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
    };
    
    let slug = title;
    
    // Transliterate Persian characters
    slug = slug.split('').map(char => persianToLatin[char] || char).join('');
    
    // Convert to lowercase and keep only ASCII letters, numbers, spaces, hyphens, and underscores
    slug = slug
      .toLowerCase()
      .replace(/[^a-z0-9\s_-]/g, '') // Remove all non-ASCII characters except spaces, hyphens, underscores
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
      .replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens
      .trim();
    
    return slug;
  },

  // Format date for display
  formatDate: (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
  },

  // Get status color
  getStatusColor: (status: string): string => {
    const colors = {
      draft: '#f57c00',
      published: '#2e7d32',
      archived: '#757575',
    };
    return colors[status as keyof typeof colors] || '#757575';
  },

  // Get status label
  getStatusLabel: (status: string): string => {
    const labels = {
      draft: 'پیش‌نویس',
      published: 'منتشر شده',
      archived: 'بایگانی',
    };
    return labels[status as keyof typeof labels] || status;
  },
};

export default {
  blogPostApi,
  blogCategoryApi,
  blogTagApi,
  blogCommentApi,
  fileUploadApi,
  blogUtils,
};
