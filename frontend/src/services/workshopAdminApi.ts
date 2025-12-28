import axios from 'axios';
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://sarmadclinic.ir';

// Create axios instance with default config
// Note: CSRF token is handled by the global axios interceptor in AuthContext
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/admin`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for session authentication
});

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
export interface Workshop {
  id?: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  category: number;
  category_name?: string;
  category_color?: string;
  instructor: number;
  instructor_name?: string;
  instructor_email?: string;
  status: 'draft' | 'published' | 'registration_open' | 'in_progress' | 'completed' | 'cancelled' | 'archived';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  price: number;
  price_persian?: string;
  discount_price?: number;
  discount_price_persian?: string;
  current_price: number;
  current_price_persian?: string;
  discount_percentage: number;
  payment_type: 'full_payment' | 'installment' | 'both';
  installment_months: number;
  installment_amount: number;
  installment_amount_persian?: string;
  start_date: string;
  start_date_persian?: string;
  end_date: string;
  end_date_persian?: string;
  registration_deadline: string;
  registration_deadline_persian?: string;
  total_hours: number;
  language: string;
  prerequisites?: string;
  learning_objectives: string;
  current_participants: number;
  max_participants: number;
  is_full: boolean;
  available_seats: number;
  thumbnail?: string;
  intro_video?: string;
  rating: number;
  review_count: number;
  registration_count: number;
  attendance_rate: number;
  revenue: number;
  created_at?: string;
  created_at_persian?: string;
  published_at?: string;
  published_at_persian?: string;
  sessions?: WorkshopSession[];
  registrations?: WorkshopRegistration[];
}

export interface WorkshopSession {
  id?: number;
  session_number: number;
  title: string;
  description?: string;
  scheduled_datetime: string;
  scheduled_datetime_persian?: string;
  duration_minutes: number;
  duration_display?: string;
  session_video?: string;
  croom_platform_link?: string;
  materials?: string;
  homework?: string;
  is_completed: boolean;
  attendance_count?: number;
  created_at?: string;
}

export interface WorkshopRegistration {
  id?: number;
  user: number;
  user_name?: string;
  user_email?: string;
  workshop: number;
  workshop_title?: string;
  status: 'pending_payment' | 'active' | 'completed' | 'cancelled' | 'suspended';
  payment_type: 'full_payment' | 'installment';
  amount_paid: number;
  total_amount: number;
  progress_percentage: number;
  registered_at: string;
  registered_at_persian?: string;
  completed_at?: string;
  completed_at_persian?: string;
  last_accessed?: string;
  last_accessed_persian?: string;
  payment_status?: string;
}

export interface WorkshopCategory {
  id?: number;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  color: string;
  is_active: boolean;
  workshop_count?: number;
  created_at?: string;
  created_at_persian?: string;
}

export interface WorkshopFilters {
  search?: string;
  status?: string;
  category?: number;
  difficulty?: string;
  instructor?: number;
  payment_type?: string;
  date_from?: string;
  date_to?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface SessionFilters {
  is_completed?: boolean;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface RegistrationFilters {
  status?: string;
  payment_type?: string;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

// Workshop API
export const workshopApi = {
  // Get all workshops with filters
  getWorkshops: async (filters: WorkshopFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`/workshops/?${params.toString()}`);
    return response.data;
  },

  // Get single workshop
  getWorkshop: async (id: number) => {
    const response = await api.get(`/workshops/${id}/`);
    return response.data;
  },

  // Create new workshop
  createWorkshop: async (data: Partial<Workshop>) => {
    const response = await api.post('/workshops/', data);
    return response.data;
  },

  // Update workshop
  updateWorkshop: async (id: number, data: Partial<Workshop>) => {
    const response = await api.put(`/workshops/${id}/`, data);
    return response.data;
  },

  // Delete workshop
  deleteWorkshop: async (id: number) => {
    const response = await api.delete(`/workshops/${id}/`);
    return response.data;
  },

  // Bulk actions on workshops
  bulkAction: async (action: string, workshopIds: number[]) => {
    const response = await api.post('/workshops/bulk-action/', {
      action,
      workshop_ids: workshopIds,
    });
    return response.data;
  },
};

// Workshop Sessions API
export const workshopSessionApi = {
  // Get sessions for a workshop
  getSessions: async (workshopId: number, filters: SessionFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`/workshops/${workshopId}/sessions/?${params.toString()}`);
    return response.data;
  },

  // Get single session
  getSession: async (workshopId: number, sessionId: number) => {
    const response = await api.get(`/workshops/${workshopId}/sessions/${sessionId}/`);
    return response.data;
  },

  // Create new session
  createSession: async (workshopId: number, data: Partial<WorkshopSession>) => {
    const response = await api.post(`/workshops/${workshopId}/sessions/`, data);
    return response.data;
  },

  // Update session
  updateSession: async (workshopId: number, sessionId: number, data: Partial<WorkshopSession>) => {
    const response = await api.put(`/workshops/${workshopId}/sessions/${sessionId}/`, data);
    return response.data;
  },

  // Delete session
  deleteSession: async (workshopId: number, sessionId: number) => {
    const response = await api.delete(`/workshops/${workshopId}/sessions/${sessionId}/`);
    return response.data;
  },

};

// Workshop Registrations API
export const workshopRegistrationApi = {
  // Get registrations for a workshop
  getRegistrations: async (workshopId: number, filters: RegistrationFilters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`/workshops/${workshopId}/registrations/?${params.toString()}`);
    return response.data;
  },

  // Approve registration
  approveRegistration: async (registrationId: number) => {
    const response = await api.post(`/workshops/registrations/${registrationId}/approve/`);
    return response.data;
  },

  // Reject registration
  rejectRegistration: async (registrationId: number, rejectionReason?: string) => {
    const response = await api.post(`/workshops/registrations/${registrationId}/reject/`, {
      rejection_reason: rejectionReason,
    });
    return response.data;
  },
};

// Workshop Categories API
export const workshopCategoryApi = {
  // Get all categories
  getCategories: async () => {
    const response = await api.get('/workshops/categories/');
    return response.data;
  },

  // Get single category
  getCategory: async (id: number) => {
    const response = await api.get(`/workshops/categories/${id}/`);
    return response.data;
  },

  // Create new category
  createCategory: async (data: Partial<WorkshopCategory>) => {
    const response = await api.post('/workshops/categories/', data);
    return response.data;
  },

  // Update category
  updateCategory: async (id: number, data: Partial<WorkshopCategory>) => {
    const response = await api.put(`/workshops/categories/${id}/`, data);
    return response.data;
  },

  // Delete category
  deleteCategory: async (id: number) => {
    const response = await api.delete(`/workshops/categories/${id}/`);
    return response.data;
  },
};

// Utility functions
export const workshopUtils = {
  // Get status color
  getStatusColor: (status: string): string => {
    const colors = {
      draft: '#f57c00',
      published: '#2e7d32',
      registration_open: '#1976d2',
      in_progress: '#7b1fa2',
      completed: '#388e3c',
      cancelled: '#d32f2f',
      archived: '#757575',
    };
    return colors[status as keyof typeof colors] || '#757575';
  },

  // Get status label
  getStatusLabel: (status: string): string => {
    const labels = {
      draft: 'پیش‌نویس',
      published: 'منتشر شده',
      registration_open: 'ثبت‌نام باز',
      in_progress: 'در حال برگزاری',
      completed: 'تکمیل شده',
      cancelled: 'لغو شده',
      archived: 'بایگانی',
    };
    return labels[status as keyof typeof labels] || status;
  },

  // Get difficulty label
  getDifficultyLabel: (difficulty: string): string => {
    const labels = {
      beginner: 'مبتدی',
      intermediate: 'متوسط',
      advanced: 'پیشرفته',
    };
    return labels[difficulty as keyof typeof labels] || difficulty;
  },

  // Get payment type label
  getPaymentTypeLabel: (paymentType: string): string => {
    const labels = {
      full_payment: 'پرداخت کامل',
      installment: 'قسطی',
      both: 'هر دو',
    };
    return labels[paymentType as keyof typeof labels] || paymentType;
  },

  // Format price
  formatPrice: (price: number): string => {
    return new Intl.NumberFormat('fa-IR').format(price);
  },

  // Format date
  formatDate: (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
  },

  // Generate slug from title
  generateSlug: (title: string): string => {
    return title
      .toLowerCase()
      .replace(/[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  },
};

export default {
  workshopApi,
  workshopSessionApi,
  workshopRegistrationApi,
  workshopCategoryApi,
  workshopUtils,
};
