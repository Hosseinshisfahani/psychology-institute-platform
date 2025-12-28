import axios from 'axios';

// Default to production, overridden by REACT_APP_API_URL env var in development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://sarmadclinic.ir';

// Create axios instance with default config for public blog API
// Note: CSRF token is handled by the global axios interceptor in AuthContext
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/blog`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for CSRF and session
});

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
  parent?: number;
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
    search_title?: string;
    search_content?: string;
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

  // Create comment for a post
  createComment: async (postSlug: string, content: string, parentId?: number) => {
    const payload: { content: string; parent?: number } = { content };
    if (parentId !== undefined) {
      payload.parent = parentId;
    }
    const response = await api.post(`/posts/${postSlug}/comments/`, payload);
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
