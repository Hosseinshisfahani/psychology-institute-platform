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
  checkAuthStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Configure axios defaults (Django-compatible CSRF names)
// Default to production URL for safety, but can be overridden via REACT_APP_API_URL env var
// Development: start_frontend.sh sets REACT_APP_API_URL=http://localhost:8001
// Production: deploy.sh sets REACT_APP_API_URL=https://sarmadclinic.ir
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://sarmadclinic.ir';
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

// Add request interceptor for debugging (only in development)
if (process.env.NODE_ENV === 'development') {
  axios.interceptors.request.use(
    (config) => {
      console.log('🚀 API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        fullURL: `${config.baseURL}${config.url}`,
        headers: config.headers,
      });
      return config;
    },
    (error) => {
      console.error('❌ Request Error:', error);
      return Promise.reject(error);
    }
  );

  axios.interceptors.response.use(
    (response) => {
      console.log('✅ API Response:', {
        status: response.status,
        url: response.config.url,
        data: response.data,
      });
      return response;
    },
    (error) => {
      console.error('❌ Response Error:', {
        status: error.response?.status,
        url: error.config?.url,
        message: error.message,
        data: error.response?.data,
      });
      return Promise.reject(error);
    }
  );
}

// Cache for CSRF token fetch to prevent multiple simultaneous requests
let csrfFetchPromise: Promise<void> | null = null;

// Helper to get CSRF token from cookie
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

// Add request interceptor to ensure CSRF token is included
axios.interceptors.request.use(
  async (config) => {
    try {
      // Skip CSRF for the CSRF endpoint itself
      if (config.url?.includes('/csrf/')) {
        return config;
      }

      let csrfToken = getCsrfToken();
      
      // If no CSRF token, fetch it (with caching to prevent duplicate requests)
      if (!csrfToken) {
        // If a fetch is already in progress, wait for it
        if (csrfFetchPromise) {
          await csrfFetchPromise;
          // Re-check token after waiting
          csrfToken = getCsrfToken();
        } else {
          // Atomically create and assign the promise to prevent race conditions
          // Multiple requests checking simultaneously will all see the same promise
          const fetchPromise = (async () => {
            try {
              await axios.get('/csrf/');
              // Give browser a moment to set the cookie
              await new Promise(resolve => setTimeout(resolve, 10));
            } catch (error) {
              console.warn('Failed to fetch CSRF token:', error);
            } finally {
              // Clear cache after a delay to allow cookie to be set
              setTimeout(() => {
                csrfFetchPromise = null;
              }, 500);
            }
          })();
          
          // Set the promise BEFORE awaiting to prevent race conditions
          csrfFetchPromise = fetchPromise;
          await fetchPromise;
          
          // Re-check token after fetch
          csrfToken = getCsrfToken();
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
    // CSRF token will be fetched automatically by the interceptor when needed
    // No need to fetch it explicitly here to avoid duplicate requests
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

  const getCsrf = async () => {
    // Only fetch if we don't already have a token
    const existingToken = getCsrfToken();
    if (!existingToken) {
      // Use the same caching mechanism as the interceptor
      if (csrfFetchPromise) {
        await csrfFetchPromise;
      } else {
        const fetchPromise = (async () => {
          try {
            await axios.get('/csrf/');
            await new Promise(resolve => setTimeout(resolve, 10));
          } catch (_) {
            // no-op: endpoint sets cookie via middleware
          } finally {
            setTimeout(() => {
              csrfFetchPromise = null;
            }, 500);
          }
        })();
        csrfFetchPromise = fetchPromise;
        await fetchPromise;
      }
    }
  };

  const login = async (email: string, password: string, otpCode?: string, phoneNumber?: string) => {
    try {
      // Ensure CSRF cookie exists before POST
      await getCsrf();
      
      // Get CSRF token from cookie
      const csrfToken = getCsrfToken();
      
      // Build request data - email and phone_number are optional (at least one required)
      const requestData: any = {
        password,
      };
      
      // Add email if provided (non-empty)
      if (email && email.trim()) {
        requestData.email = email.trim();
      }
      
      // Add phone_number if provided (non-empty)
      if (phoneNumber && phoneNumber.trim()) {
        requestData.phone_number = phoneNumber.trim();
      }
      
      // Add OTP code if provided
      if (otpCode) {
        requestData.otp_code = otpCode;
      }
      
      const response = await axios.post('/api/dashboard/login/', requestData, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
      
      if (response.data.success) {
        // Set user directly from login response to avoid extra API call
        // and ensure state updates immediately
        if (response.data.user) {
          setUser(response.data.user);
        } else {
          // Fallback to checkAuthStatus if user data not in response
          await checkAuthStatus();
        }
      } else {
        throw new Error(response.data.message || 'ورود ناموفق بود');
      }
    } catch (error: any) {
      // Enhanced error handling with better Persian messages
      let errorMessage = 'خطا در ورود. لطفاً دوباره تلاش کنید.';
      
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data;
        
        // Extract error message from response
        if (data?.message) {
          const msg = data.message;
          // Filter out numeric-only messages (likely transaction IDs)
          if (typeof msg === 'string' && !/^\d+$/.test(msg.trim())) {
            errorMessage = msg;
          } else if (typeof msg === 'string' && msg.trim().length > 0) {
            // If it's a number, use generic message
            errorMessage = 'خطا در ورود. لطفاً دوباره تلاش کنید.';
          }
        } else if (data?.detail) {
          // DRF default error format
          errorMessage = typeof data.detail === 'string' && !/^\d+$/.test(data.detail.trim()) 
            ? data.detail 
            : 'خطا در ورود. لطفاً دوباره تلاش کنید.';
        } else if (data && typeof data === 'string' && !/^\d+$/.test(data.trim())) {
          errorMessage = data;
        } else if (Array.isArray(data)) {
          // Array of errors
          errorMessage = data.filter(msg => typeof msg === 'string' && !/^\d+$/.test(msg.trim())).join(', ') || errorMessage;
        }
        
        // Map HTTP status codes to Persian messages if no specific message
        if (errorMessage === 'خطا در ورود. لطفاً دوباره تلاش کنید.' || !data?.message) {
          switch (status) {
            case 400:
              errorMessage = 'اطلاعات وارد شده صحیح نیست. لطفاً فیلدها را بررسی کنید.';
              break;
            case 401:
              errorMessage = 'ایمیل یا رمز عبور اشتباه است.';
              break;
            case 403:
              errorMessage = 'دسترسی شما محدود است. لطفاً با پشتیبانی تماس بگیرید.';
              break;
            case 404:
              errorMessage = 'درخواست شما یافت نشد.';
              break;
            case 500:
              errorMessage = 'خطای سرور. لطفاً لحظاتی بعد دوباره تلاش کنید.';
              break;
            default:
              errorMessage = 'خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.';
          }
        }
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'خطا در ارتباط با سرور. لطفاً اتصال اینترنت خود را بررسی کنید.';
      } else if (error.message && !/^\d+$/.test(error.message.trim())) {
        // Error in setting up the request
        errorMessage = error.message;
      }
      
      console.error('[AuthContext] Login error:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      
      throw new Error(errorMessage);
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
        // Set user directly from signup response to avoid extra API call
        // and ensure state updates immediately
        if (response.data.user) {
          setUser(response.data.user);
        } else {
          // Fallback to checkAuthStatus if user data not in response
          await checkAuthStatus();
        }
      } else {
        throw new Error(response.data.message || 'Signup failed');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Signup failed');
    }
  };

  const sendOTP = async (phoneNumber: string, purpose: string = 'signup') => {
    console.log('[AuthContext] sendOTP called', { phoneNumber, purpose });
    try {
      console.log('[AuthContext] Fetching CSRF token...');
      await getCsrf();
      const csrfToken = getCsrfToken();
      console.log('[AuthContext] CSRF token obtained', { hasToken: !!csrfToken });
      
      const requestData = {
        phone_number: phoneNumber,
        purpose,
      };
      console.log('[AuthContext] Making POST request to /api/dashboard/otp/send/', requestData);
      
      const response = await axios.post('/api/dashboard/otp/send/', requestData, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
      
      console.log('[AuthContext] OTP send response', { status: response.status, data: response.data });
      
      if (!response.data.success) {
        const errorMsg = response.data.message || 'Failed to send OTP';
        console.error('[AuthContext] OTP send failed', errorMsg);
        throw new Error(typeof errorMsg === 'string' ? errorMsg : 'Failed to send OTP');
      }
      
      console.log('[AuthContext] OTP sent successfully');
    } catch (error: any) {
      console.error('[AuthContext] Error in sendOTP', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        stack: error.stack,
      });
      
      // Better error message handling
      let errorMessage = 'Failed to send OTP';
      
      if (error.response?.data?.message) {
        const msg = error.response.data.message;
        // Filter out numeric-only messages (likely transaction IDs incorrectly treated as errors)
        if (typeof msg === 'string' && !/^\d+$/.test(msg.trim())) {
          errorMessage = msg;
        } else if (typeof msg === 'string' && msg.trim().length > 0) {
          // If it's a number, it might be a transaction ID - use generic message
          errorMessage = 'خطا در ارسال کد تایید. لطفاً دوباره تلاش کنید.';
        }
      } else if (error.response?.data) {
        // If response.data exists but no message, try to extract meaningful error
        const data = error.response.data;
        if (typeof data === 'string' && !/^\d+$/.test(data.trim())) {
          errorMessage = data;
        } else if (Array.isArray(data)) {
          errorMessage = data.join(', ');
        } else if (data.detail && typeof data.detail === 'string' && !/^\d+$/.test(data.detail.trim())) {
          errorMessage = data.detail;
        }
      } else if (error.message && !/^\d+$/.test(error.message.trim())) {
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
        code: otpCode,
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
    checkAuthStatus,
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
