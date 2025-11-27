import axios from 'axios';

export interface WorkshopSession {
  id: number;
  session_number: number;
  title: string;
  description: string;
  scheduled_datetime: string;
  scheduled_datetime_persian: string;
  duration_minutes: number;
  has_recording: boolean;
  can_join: boolean;
  is_completed: boolean;
}

export interface Workshop {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  category?: {
    name: string;
  };
  category_name?: string;
  instructor_name: string;
  status: string;
  difficulty: string;
  price: string;
  current_price: string;
  payment_type: string;
  start_date_persian: string;
  end_date_persian: string;
  total_hours: number;
  thumbnail: string | null;
  rating: number;
  review_count: number;
  sessions: WorkshopSession[];
}

export interface WorkshopRegistration {
  id: number;
  workshop: Workshop;
  status: string;
  payment_type: string;
  amount_paid: string;
  total_amount: string;
  progress_percentage: number;
  registered_at: string;
  installment_plan?: {
    id: number;
    total_amount: string;
    number_of_installments: number;
    installment_amount: string;
    total_paid: string;
    remaining_amount: string;
    is_fully_paid: boolean;
    payments: Array<{
      id: number;
      installment_number: number;
      amount: string;
      due_date: string;
      status: string;
    }>;
  };
}

export interface SessionAccessData {
  session: WorkshopSession;
  meeting_link: string;
  recording_url: string;
  can_join: boolean;
  attendance: {
    id: number;
    attended: boolean;
    joined_at: string;
    left_at: string;
  };
}

export const workshopApi = {
  // Get user's registered workshops
  getUserWorkshops: async (): Promise<WorkshopRegistration[]> => {
    try {
      const response = await axios.get('/api/workshops/my/workshops/');
      console.log('API Response:', response.data);
      console.log('Response type:', typeof response.data);
      console.log('Is array:', Array.isArray(response.data));
      
      // Handle paginated response
      if (response.data && response.data.results) {
        console.log('Paginated response detected, returning results array');
        return response.data.results;
      }
      
      // Handle direct array response
      if (Array.isArray(response.data)) {
        console.log('Direct array response');
        return response.data;
      }
      
      console.log('Unexpected response format:', response.data);
      return [];
    } catch (error) {
      console.error('Error fetching user workshops:', error);
      throw error;
    }
  },

  // Get workshop detail
  getWorkshopDetail: async (slug: string): Promise<Workshop> => {
    const response = await axios.get(`/api/workshops/${slug}/`);
    return response.data;
  },

  // Register for a workshop
  registerWorkshop: async (slug: string, paymentType: string = 'full_payment') => {
    const response = await axios.post(`/api/workshops/${slug}/register/`, {
      payment_type: paymentType
    });
    return response.data;
  },

  // Add workshop to cart
  addToCart: async (slug: string) => {
    const response = await axios.post(`/api/workshops/${slug}/add-to-cart/`);
    return response.data;
  },

  // Get session access details
  getSessionAccess: async (sessionId: number): Promise<SessionAccessData> => {
    const response = await axios.get(`/api/workshops/sessions/${sessionId}/access/`);
    return response.data;
  },

  // Mark session attendance
  markAttendance: async (sessionId: number) => {
    const response = await axios.post(`/api/workshops/sessions/${sessionId}/attendance/`);
    return response.data;
  },

  // Get workshop installments
  getWorkshopInstallments: async (slug: string) => {
    const response = await axios.get(`/api/workshops/${slug}/installments/`);
    return response.data;
  },

  // Create workshop review
  createReview: async (slug: string, rating: number, comment: string) => {
    const response = await axios.post(`/api/workshops/${slug}/review/`, {
      rating,
      comment
    });
    return response.data;
  },

  // Get workshop reviews
  getWorkshopReviews: async (slug: string) => {
    const response = await axios.get(`/api/workshops/${slug}/reviews/`);
    return response.data;
  }
};

export default workshopApi;
