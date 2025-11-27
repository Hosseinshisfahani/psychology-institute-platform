import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config for public blog API
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/blog`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for CSRF and session
});

// Add request interceptor to include CSRF token
api.interceptors.request.use(
  async (config) => {
    try {
      // Get CSRF token from cookie
      const getCsrfToken = () => {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      };

      let csrfToken = getCsrfToken();
      
      // If no CSRF token, fetch it first
      if (!csrfToken) {
        try {
          await axios.get(`${API_BASE_URL}/csrf/`);
          csrfToken = getCsrfToken();
        } catch (error) {
          console.warn('Failed to fetch CSRF token:', error);
        }
      }
      
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    } catch (error) {
      console.warn('Failed to get CSRF token:', error);
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Types
export interface Post {
  id: number;
  title: string;
  slug: string;
  content: string;
  excerpt: string;
  featured_image?: string;
  category: {
    id: number;
    name: string;
    slug: string;
  };
  tags: Array<{
    id: number;
    name: string;
    slug: string;
  }>;
  author_name: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  created_at_persian: string;
  published_at_persian?: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  color: string;
  icon?: string;
}

export interface Tag {
  id: number;
  name: string;
  slug: string;
}

export interface Comment {
  id: number;
  content: string;
  author: {
    id: number;
    full_name: string;
  };
  created_at: string;
  created_at_persian: string;
  is_approved: boolean;
}

export interface LikeResponse {
  liked: boolean;
  like_count: number;
}

// Public Blog API
export const blogApi = {
  // Get all blog posts
  getPosts: async (params?: {
    category?: string;
    tag?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await api.get(`/posts/?${queryParams.toString()}`);
    return response.data;
  },

  // Get single blog post
  getPost: async (slug: string) => {
    const response = await api.get(`/posts/${slug}/`);
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/categories/');
    return response.data;
  },

  // Get tags
  getTags: async () => {
    const response = await api.get('/tags/');
    return response.data;
  },

  // Get comments for a post
  getComments: async (postSlug: string) => {
    const response = await api.get(`/posts/${postSlug}/comments/`);
    return response.data;
  },

  // Toggle like for a post
  toggleLike: async (postSlug: string): Promise<LikeResponse> => {
    const response = await api.post(`/posts/${postSlug}/like/`);
    return response.data;
  },

  // Subscribe to newsletter
  subscribeNewsletter: async (email: string) => {
    const response = await api.post('/newsletter/subscribe/', { email });
    return response.data;
  },

  // Unsubscribe from newsletter
  unsubscribeNewsletter: async (email: string) => {
    const response = await api.post('/newsletter/unsubscribe/', { email });
    return response.data;
  },
};

export default blogApi;
