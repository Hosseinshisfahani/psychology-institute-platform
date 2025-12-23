import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://185.8.175.241:8000';

// Create axios instance with default config for public course API
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/courses`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for CSRF and session
});

// Types
export interface Course {
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
  is_free: boolean;
  difficulty: string;
  duration_hours: number;
  thumbnail?: string;
  rating: number;
  review_count: number;
  like_count: number;
  enrollment_count: number;
  instructor_name: string;
}

export interface CourseComment {
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

// Public Course API
export const courseApi = {
  // Get all courses
  getCourses: async (params?: {
    category?: string;
    difficulty?: string;
    is_free?: boolean;
    search?: string;
    page?: number;
    page_size?: number;
    ordering?: string;
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

  // Get single course
  getCourse: async (slug: string) => {
    const response = await api.get(`/${slug}/`);
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get('/categories/');
    return response.data;
  },

  // Get comments for a course
  getComments: async (courseSlug: string) => {
    const response = await api.get(`/${courseSlug}/comments/`);
    return response.data;
  },

  // Create comment for a course
  createComment: async (courseSlug: string, content: string, parentId?: number) => {
    const response = await api.post(`/${courseSlug}/comments/`, {
      content,
      parent: parentId,
    });
    return response.data;
  },

  // Toggle like for a course
  toggleLike: async (courseSlug: string): Promise<LikeResponse> => {
    const response = await api.post(`/${courseSlug}/like/`);
    return response.data;
  },
};

export default courseApi;

