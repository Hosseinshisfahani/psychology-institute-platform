import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  first_name_en?: string;
  last_name_en?: string;
  full_name: string;
  user_type: string;
  phone_number?: string;
  national_id?: string;
  birth_date?: string;
  gender?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  profile_image?: string;
  bio?: string;
  is_active: boolean;
  is_verified?: boolean;
  is_staff?: boolean;
  date_joined: string;
  last_login: string | null;
  profile?: {
    id: number;
    emergency_contact_name?: string;
    emergency_contact_phone?: string;
    medical_conditions?: string;
    medications?: string;
    therapy_goals?: string;
    preferred_language?: string;
    timezone?: string;
    notification_preferences?: any;
    created_at: string;
    updated_at: string;
  };
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, otpCode?: string, phoneNumber?: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (email: string, password1: string, password2: string, first_name: string, last_name: string, phone_number: string, otp_code: string) => Promise<void>;
  sendOTP: (phoneNumber: string, purpose?: string) => Promise<void>;
  verifyOTP: (phoneNumber: string, otpCode: string, purpose?: string) => Promise<void>;
  updateProfile: (data: Partial<User['profile']>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Configure axios defaults (Django-compatible CSRF names)
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

// Add request interceptor to ensure CSRF token is included
axios.interceptors.request.use(
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
          await axios.get('/csrf/');
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

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    // Ensure CSRF token is available before any requests
    getCsrf();
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('/api/dashboard/auth-check/');
      if (response.data.authenticated) {
        setUser(response.data.user);
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

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

  const getCsrf = async () => {
    try {
      await axios.get('/csrf/');
    } catch (_) {
      // no-op: endpoint sets cookie via middleware
    }
  };

  const login = async (email: string, password: string, otpCode?: string, phoneNumber?: string) => {
    try {
      // Ensure CSRF cookie exists before POST
      await getCsrf();
      
      // Get CSRF token from cookie
      const csrfToken = getCsrfToken();
      
      const response = await axios.post('/api/dashboard/login/', {
        email,
        password,
        otp_code: otpCode,
        phone_number: phoneNumber,
      }, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
      
      if (response.data.success) {
        await checkAuthStatus();
      } else {
        throw new Error(response.data.message || 'Login failed');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  };

  const logout = async () => {
    try {
      await getCsrf();
      const csrfToken = getCsrfToken();
      await axios.post('/api/dashboard/logout/', {}, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const signup = async (
    email: string, 
    password1: string, 
    password2: string, 
    first_name: string, 
    last_name: string,
    phone_number: string,
    otp_code: string
  ) => {
    try {
      // Ensure CSRF cookie exists before POST
      await getCsrf();
      const csrfToken = getCsrfToken();
      const response = await axios.post('/api/dashboard/signup/', {
        email,
        password1,
        password2,
        first_name,
        last_name,
        phone_number,
        otp_code,
      }, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
      
      if (response.data.success) {
        await checkAuthStatus();
      } else {
        throw new Error(response.data.message || 'Signup failed');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Signup failed');
    }
  };

  const sendOTP = async (phoneNumber: string, purpose: string = 'signup') => {
    try {
      await getCsrf();
      const csrfToken = getCsrfToken();
      const response = await axios.post('/api/dashboard/otp/send/', {
        phone_number: phoneNumber,
        purpose,
      }, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
      
      if (!response.data.success) {
        const errorMsg = response.data.message || 'Failed to send OTP';
        throw new Error(typeof errorMsg === 'string' ? errorMsg : 'Failed to send OTP');
      }
    } catch (error: any) {
      // Better error message handling
      let errorMessage = 'Failed to send OTP';
      
      if (error.response?.data?.message) {
        const msg = error.response.data.message;
        errorMessage = typeof msg === 'string' ? msg : errorMessage;
      } else if (error.response?.data) {
        // If response.data exists but no message, try to extract meaningful error
        const data = error.response.data;
        if (typeof data === 'string') {
          errorMessage = data;
        } else if (Array.isArray(data)) {
          errorMessage = data.join(', ');
        } else if (data.detail) {
          errorMessage = typeof data.detail === 'string' ? data.detail : errorMessage;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      throw new Error(errorMessage);
    }
  };

  const verifyOTP = async (phoneNumber: string, otpCode: string, purpose: string = 'signup') => {
    try {
      await getCsrf();
      const csrfToken = getCsrfToken();
      const response = await axios.post('/api/dashboard/otp/verify/', {
        phone_number: phoneNumber,
        otp_code: otpCode,
        purpose,
      }, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
      
      if (!response.data.success) {
        throw new Error(response.data.message || 'Invalid OTP code');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Invalid OTP code');
    }
  };

  const updateProfile = async (data: Partial<User['profile']>) => {
    try {
      const response = await axios.patch('/api/dashboard/profile/', data);
      setUser(response.data);
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Profile update failed');
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    signup,
    sendOTP,
    verifyOTP,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
