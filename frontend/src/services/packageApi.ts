import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://185.8.175.241:8000';

// Create axios instance with default config for public package API
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/packages`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for CSRF and session
});

// Types
export interface Package {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  category: {
    id: number;
    name: string;
    slug: string;
  };
  price: number;
  discount_price?: number;
  current_price: number;
  discount_percentage: number;
  is_featured: boolean;
  total_courses: number;
  total_hours: number;
  duration_months: number;
  thumbnail?: string;
  rating: number;
  review_count: number;
  like_count: number;
  purchase_count: number;
  savings_amount: number;
  savings_percentage: number;
}

export interface PackageComment {
  id: number;
  content: string;
  author: {
    id: number;
    full_name: string;
    email: string;
  };
  author_name: string;
  author_email: string;
  created_at: string;
  created_at_persian: string;
  is_approved: boolean;
  parent?: number;
  replies_count: number;
}

export interface LikeResponse {
  liked: boolean;
  like_count: number;
}

// Public Package API
export const packageApi = {
  // Get all packages
  getPackages: async (params?: {
    category?: string;
    featured?: boolean;
    limit?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await api.get(`/?${queryParams.toString()}`);
    return response.data;
  },

  // Get single package
  getPackage: async (slug: string) => {
    const response = await api.get(`/${slug}/`);
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/categories/');
    return response.data;
  },

  // Get comments for a package
  getComments: async (packageSlug: string) => {
    const response = await api.get(`/${packageSlug}/comments/`);
    return response.data;
  },

  // Create comment for a package
  createComment: async (packageSlug: string, content: string, parentId?: number) => {
    const response = await api.post(`/${packageSlug}/comments/`, {
      content,
      parent: parentId,
    });
    return response.data;
  },

  // Toggle like for a package
  toggleLike: async (packageSlug: string): Promise<LikeResponse> => {
    const response = await api.post(`/${packageSlug}/like/`);
    return response.data;
  },
};

export default packageApi;

