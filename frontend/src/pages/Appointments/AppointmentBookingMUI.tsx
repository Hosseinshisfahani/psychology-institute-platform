'use client';
import React, { useState, useCallback, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, InputGroup, Badge, Alert } from 'react-bootstrap';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import BookingTimeSelectorMUI from '../../components/BookingTimeSelectorMUI';

interface Therapist {
  id: number;
  name: string;
  specialization: string;
  experience_years: number;
  hourly_rate: number;
  profile_image?: string;
}

interface AppointmentType {
  id: number;
  name: string;
  description: string;
  default_duration_minutes: number;
  price?: number;
  requires_deposit?: boolean;
  deposit_amount?: number;
}

interface ClinicLocation {
  id: number;
  name: string;
  address: string;
  city: string;
  phone: string;
  capacity: number;
}

interface BookingData {
  therapist: number;
  appointment_type: number;
  location: number;
  scheduled_datetime: string;
  duration_minutes: number;
  notes?: string;
}

const AppointmentBookingMUI: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [selectedTherapist, setSelectedTherapist] = useState<number | null>(null);
  const [selectedType, setSelectedType] = useState<number | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<number | null>(null);
  const [notes, setNotes] = useState<string>('');
  const [step, setStep] = useState<number>(1);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [isRescheduling, setIsRescheduling] = useState<boolean>(false);
  const [existingAppointment, setExistingAppointment] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const formatCurrency = (amount?: number) => {
    const numericAmount = Number(amount || 0);
    if (!Number.isFinite(numericAmount) || numericAmount <= 0) {
      return '0 تومان';
    }
    return `${numericAmount.toLocaleString('fa-IR')} تومان`;
  };

  // Check if rescheduling
  const rescheduleId = searchParams.get('reschedule');
  
  // Fetch existing appointment for rescheduling
  const { data: existingAppointmentData } = useQuery({
    queryKey: ['appointment', rescheduleId],
    queryFn: async () => {
      if (!rescheduleId) return null;
      const response = await axios.get(`/api/appointments/${rescheduleId}/`);
      return response.data;
    },
    enabled: !!rescheduleId,
  });

  // Fetch therapists
  const { data: therapists = [], isLoading: therapistsLoading } = useQuery<Therapist[]>({
    queryKey: ['therapists'],
    queryFn: async () => {
      const response = await axios.get('/api/appointments/therapists/');
      return response.data;
    },
  });

  // Fetch appointment types (filtered by selected therapist if available)
  const { data: appointmentTypes = [], isLoading: typesLoading } = useQuery<AppointmentType[]>({
    queryKey: ['appointment-types', selectedTherapist],
    queryFn: async () => {
      const url = selectedTherapist 
        ? `/api/appointments/types/?therapist_id=${selectedTherapist}`
        : '/api/appointments/types/';
      const response = await axios.get(url);
      const data = response.data.results || response.data;
      return data.map((item: any) => ({
        ...item,
        price: Number(item.price ?? 0),
        requires_deposit: Boolean(item.requires_deposit),
        deposit_amount: Number(item.deposit_amount ?? 0),
      }));
    },
    enabled: step >= 3, // Only fetch when we need appointment types
  });

  // Fetch clinic locations
  const { data: locations = [], isLoading: locationsLoading } = useQuery<ClinicLocation[]>({
    queryKey: ['clinic-locations'],
    queryFn: async () => {
      const response = await axios.get('/api/appointments/locations/');
      return response.data.results || response.data;
    },
  });

  // Memoize fetchAvailability to prevent infinite loops
  // Defined after appointmentTypes query so it's available
  const fetchAvailability = useCallback(async (dateISO: string): Promise<{ booked: string[] }> => {
    try {
      // Build query parameters
      const params: any = { date: dateISO };
      if (selectedTherapist) {
        params.therapist_id = selectedTherapist.toString();
      }
      if (selectedLocation) {
        params.location_id = selectedLocation.toString();
      }
      // Use appointment type duration if available, otherwise default to 60 minutes
      const appointmentType = selectedType ? appointmentTypes.find(type => type.id === selectedType) : null;
      const duration = appointmentType?.default_duration_minutes || 60;
      params.duration_minutes = duration.toString();
      
      // Use axios instead of fetch to use the configured baseURL
      const response = await axios.get('/api/appointments/availability/', { params });
      const bookedTimes = response.data.booked_times || [];
      console.log('Availability response for', dateISO, ':', bookedTimes);
      return { booked: bookedTimes };
    } catch (error: any) {
      console.error('Error fetching availability:', error);
      console.error('Error details:', error.response?.data);
      // Return empty array on error so all times appear available (better UX than blocking everything)
      return { booked: [] };
    }
  }, [selectedTherapist, selectedLocation, selectedType, appointmentTypes]); // Include dependencies

  // Filter and sort therapists
  const filteredTherapists = therapists
    .filter(therapist => {
      const matchesSearch = therapist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           therapist.specialization.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesSpecialization = !selectedSpecialization || 
                                  therapist.specialization.includes(selectedSpecialization);
      return matchesSearch && matchesSpecialization;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'experience':
          return b.experience_years - a.experience_years;
        case 'rate':
          return a.hourly_rate - b.hourly_rate;
        case 'name':
        default:
          return a.name.localeCompare(b.name);
      }
    });

  // Get unique specializations for filter
  const specializations = Array.from(
    new Set(therapists.map(t => t.specialization).filter(Boolean))
  );

  const selectedAppointmentTypeData = selectedType
    ? appointmentTypes.find(type => type.id === selectedType) || null
    : null;

  const selectedDepositAmount = selectedAppointmentTypeData?.deposit_amount || 0;
  const requiresDeposit = Boolean(!isRescheduling && selectedAppointmentTypeData?.requires_deposit && selectedDepositAmount > 0);

  // Handle rescheduling logic
  useEffect(() => {
    if (rescheduleId && existingAppointmentData && therapists.length > 0) {
      setIsRescheduling(true);
      setExistingAppointment(existingAppointmentData);
      
      // Pre-populate form with existing appointment data
      setSelectedTherapist(existingAppointmentData.therapist);
      setSelectedType(existingAppointmentData.appointment_type);
      setSelectedLocation(existingAppointmentData.location);
      setNotes(existingAppointmentData.notes || '');
      
      // Skip to step 2 (date/time selection) for rescheduling
      setStep(2);
    }
  }, [rescheduleId, existingAppointmentData, therapists]);

  // Handle pre-selected therapist from URL parameter
  useEffect(() => {
    const therapistId = searchParams.get('therapist');
    if (therapistId && therapists.length > 0 && !isRescheduling) {
      const therapistIdNum = parseInt(therapistId, 10);
      const therapist = therapists.find(t => t.id === therapistIdNum);
      if (therapist) {
        setSelectedTherapist(therapistIdNum);
        // Skip to step 2 (date/time selection) if therapist is pre-selected
        setStep(2);
      }
    }
  }, [searchParams, therapists, isRescheduling]);

  // Validate selected time when location changes
  useEffect(() => {
    if (selectedLocation && selectedDate && selectedTime && selectedTherapist) {
      // Re-validate the selected time for the new location
      const validateTimeForLocation = async () => {
        try {
          const appointmentType = selectedType ? appointmentTypes.find(type => type.id === selectedType) : null;
          const duration = appointmentType?.default_duration_minutes || 60;
          
          const response = await axios.get('/api/appointments/availability/', {
            params: {
              date: selectedDate,
              therapist_id: selectedTherapist.toString(),
              location_id: selectedLocation.toString(),
              duration_minutes: duration.toString()
            }
          });
          
          const bookedTimes = response.data.booked_times || [];
          // If the selected time is in the booked/unavailable list, clear it
          if (bookedTimes.includes(selectedTime)) {
            setSelectedTime(null);
            setErrorMessage('زمان انتخاب شده برای این محل در دسترس نیست. لطفاً زمان دیگری انتخاب کنید.');
            // Go back to step 2 to reselect time
            setStep(2);
          }
        } catch (error) {
          // Silently fail - validation will happen on submit
          console.error('Error validating time for location:', error);
        }
      };
      
      validateTimeForLocation();
    }
  }, [selectedLocation, selectedDate, selectedTime, selectedTherapist, selectedType, appointmentTypes]);

  // Book appointment mutation
  const bookAppointmentMutation = useMutation({
    mutationFn: async (bookingData: BookingData) => {
      if (isRescheduling && rescheduleId) {
        // Update existing appointment
        const response = await axios.patch(`/api/appointments/${rescheduleId}/`, bookingData);
        return response.data;
      } else {
        // Create new appointment
        const response = await axios.post('/api/appointments/', bookingData);
        return response.data;
      }
    },
    onSuccess: (data, variables) => {
      if (!isRescheduling && data?.deposit?.required) {
        if (data.deposit.payment_url) {
          alert('برای تکمیل رزرو، لطفاً ودیعه را پرداخت کنید. اکنون به درگاه پرداخت هدایت می‌شوید.');
          window.location.href = data.deposit.payment_url;
        } else {
          alert('خطا در ایجاد پرداخت ودیعه. لطفاً بعداً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.');
        }
        return;
      }

      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      
      // Get therapist name for the banner
      const selectedTherapistData = therapists.find(t => t.id === variables.therapist);
      const therapistName = selectedTherapistData?.name || 'متخصص مربوطه';
      
      // Store success message in localStorage for the appointments page
      const message = isRescheduling 
        ? `نوبت شما با ${therapistName} با موفقیت تغییر یافت`
        : `نوبت شما با ${therapistName} با موفقیت ثبت شد`;
      
      localStorage.setItem('appointmentSuccess', JSON.stringify({
        message: message,
        therapistName: therapistName
      }));
      
      // Redirect to appointments page
      navigate('/appointments');
    },
    onError: (error: any) => {
      // Extract error message from various possible locations in the response
      let errorMsg = '';
      
      if (error.response?.data) {
        // Check for non_field_errors (array)
        if (error.response.data.non_field_errors && Array.isArray(error.response.data.non_field_errors)) {
          errorMsg = error.response.data.non_field_errors[0];
        }
        // Check for error field (string)
        else if (error.response.data.error) {
          errorMsg = error.response.data.error;
        }
        // Check for message field
        else if (error.response.data.message) {
          errorMsg = error.response.data.message;
        }
        // Check for detail field
        else if (error.response.data.detail) {
          errorMsg = error.response.data.detail;
        }
        // If it's an object with field-specific errors, get the first one
        else if (typeof error.response.data === 'object') {
          const firstKey = Object.keys(error.response.data)[0];
          const firstError = error.response.data[firstKey];
          if (Array.isArray(firstError)) {
            errorMsg = firstError[0];
          } else if (typeof firstError === 'string') {
            errorMsg = firstError;
          }
        }
      }
      
      // Fallback to generic error message
      if (!errorMsg) {
        errorMsg = isRescheduling ? 'خطای نامشخص در تغییر نوبت' : 'خطای نامشخص در رزرو نوبت';
      }
      
      setErrorMessage(errorMsg);
      
      // Scroll to top to show error banner
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
  });


  const handleConfirm = (payload: { date: string; time: string }) => {
    // Clear any previous error messages
    setErrorMessage(null);
    
    if (!user) {
      setErrorMessage('لطفاً ابتدا وارد حساب کاربری خود شوید');
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    if (!selectedTherapist || !selectedType || !selectedLocation) {
      setErrorMessage('لطفاً تمام فیلدهای الزامی را پر کنید');
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    const scheduledDateTime = `${payload.date}T${payload.time}:00`;
    
    const bookingData: BookingData = {
      therapist: selectedTherapist,
      appointment_type: selectedType,
      location: selectedLocation,
      scheduled_datetime: scheduledDateTime,
      duration_minutes: selectedAppointmentTypeData?.default_duration_minutes || 60,
      notes: notes || undefined,
    };

    bookAppointmentMutation.mutate(bookingData);
  };

  return (
    <>
      <Helmet>
        <title>رزرو نوبت - موسسه روانشناسی</title>
        <meta name="description" content="رزرو نوبت آنلاین با بهترین متخصصان روانشناسی" />
      </Helmet>

      {/* Hero Section */}
      <section 
        className="py-5" 
        style={{ 
          background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
          color: 'white'
        }}
      >
        <Container>
          <Row className="align-items-center">
            <Col lg={8}>
              <h1 className="display-4 fw-bold mb-4">
                <i className="fas fa-calendar-check me-3"></i>
                رزرو نوبت آنلاین
              </h1>
              <p className="lead mb-4">
                با بهترین متخصصان روانشناسی نوبت رزرو کنید و مسیر بهبود خود را آغاز کنید.
              </p>
            </Col>
            <Col lg={4} className="text-center">
              <div 
                style={{ 
                  fontSize: '8rem', 
                  opacity: 0.3,
                  marginTop: '2rem'
                }}
              >
                <i className="fas fa-calendar-alt"></i>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Search and Filter Section */}
      <section className="py-4" style={{ background: '#f8f9fa' }}>
        <Container>
          <Row className="g-3">
            <Col md={6} lg={4}>
              <InputGroup>
                <InputGroup.Text>
                  <i className="fas fa-search"></i>
                </InputGroup.Text>
                <Form.Control
                  type="text"
                  placeholder="جستجو در نام یا تخصص درمانگر..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </InputGroup>
            </Col>
            <Col md={6} lg={3}>
              <Form.Select
                value={selectedSpecialization}
                onChange={(e) => setSelectedSpecialization(e.target.value)}
              >
                <option value="">همه تخصص‌ها</option>
                {specializations.map(spec => (
                  <option key={spec} value={spec}>{spec}</option>
                ))}
              </Form.Select>
            </Col>
            <Col md={6} lg={3}>
              <Form.Select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="name">مرتب‌سازی بر اساس نام</option>
                <option value="experience">مرتب‌سازی بر اساس تجربه</option>
                <option value="rate">مرتب‌سازی بر اساس نرخ</option>
              </Form.Select>
            </Col>
            <Col md={6} lg={2}>
              <div className="d-flex align-items-center h-100">
                <small className="text-muted">
                  {filteredTherapists.length} درمانگر یافت شد
                </small>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      <Container className="py-5">
        {!user && (
          <Alert variant="warning" className="text-center mb-4">
            <h5 className="mb-3">ورود الزامی است</h5>
            <p className="mb-3">برای رزرو نوبت، ابتدا باید وارد حساب کاربری خود شوید.</p>
            <Button variant="primary" href="/login" className="mt-2">
              ورود به حساب کاربری
            </Button>
          </Alert>
        )}

        {user && (
          <Card 
            style={{ 
              borderRadius: '18px', 
              border: 'none', 
              boxShadow: '0 5px 15px rgba(0,0,0,0.08)',
              overflow: 'hidden'
            }}
          >
            <Card.Body style={{ padding: '2rem' }}>
              {/* Show error banner */}
              {errorMessage && (
                <Alert 
                  variant="danger" 
                  className="mb-4" 
                  style={{ borderRadius: '12px' }}
                  dismissible
                  onClose={() => setErrorMessage(null)}
                >
                  <Alert.Heading className="h6">
                    <i className="fas fa-exclamation-circle me-2"></i>
                    خطا در رزرو نوبت
                  </Alert.Heading>
                  <p className="mb-0">{errorMessage}</p>
                </Alert>
              )}
              
              {/* Show rescheduling banner */}
              {isRescheduling && existingAppointment && (
                <Alert variant="info" className="mb-4" style={{ borderRadius: '12px' }}>
                  <Alert.Heading className="h6">
                    <i className="fas fa-edit me-2"></i>
                    تغییر زمان نوبت
                  </Alert.Heading>
                  <p className="mb-0">
                    در حال تغییر زمان نوبت با <strong>{existingAppointment.therapist_name}</strong> هستید.
                    فقط تاریخ و زمان جدید را انتخاب کنید.
                  </p>
                </Alert>
              )}

              {/* Step 1: Select Therapist (skip if rescheduling) */}
              {step === 1 && !isRescheduling && (
                <div>
                  <h4 className="mb-4 text-center">انتخاب درمانگر</h4>
                  {therapistsLoading ? (
                    <div className="text-center py-5">
                      <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
                        <span className="visually-hidden">در حال بارگذاری...</span>
                      </div>
                      <p className="text-muted mt-3">در حال بارگذاری درمانگران...</p>
                    </div>
                  ) : filteredTherapists.length > 0 ? (
                    <Row className="g-4">
                      {filteredTherapists.map((therapist) => (
                        <Col key={therapist.id} md={6} lg={4} xl={3}>
                          <Card 
                            className="h-100"
                            style={{
                              border: selectedTherapist === therapist.id ? '2px solid #007bff' : '1px solid #dee2e6',
                              borderRadius: '18px',
                              overflow: 'hidden',
                              transition: 'all 0.4s ease',
                              cursor: 'pointer',
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.transform = 'translateY(-10px)';
                              e.currentTarget.style.boxShadow = '0 20px 50px rgba(0,0,0,0.15)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.transform = 'translateY(0)';
                              e.currentTarget.style.boxShadow = '0 5px 15px rgba(0,0,0,0.08)';
                            }}
                            onClick={() => {
                              setSelectedTherapist(therapist.id);
                              setSelectedDate(null);
                              setSelectedTime(null);
                              setStep(2);
                            }}
                          >
                            {/* Profile Image */}
                            <div 
                              className="text-center py-5"
                              style={{ 
                                background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                                position: 'relative'
                              }}
                            >
                              {therapist.profile_image ? (
                                <img
                                  src={therapist.profile_image}
                                  alt={therapist.name}
                                  style={{
                                    width: '120px',
                                    height: '120px',
                                    maxWidth: '100%',
                                    borderRadius: '50%',
                                    objectFit: 'cover',
                                    objectPosition: 'center',
                                    border: '4px solid white',
                                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                                    margin: '0 auto',
                                    display: 'block',
                                    transition: 'all 0.3s ease',
                                    cursor: 'pointer'
                                  }}
                                  loading="lazy"
                                  onError={(e) => {
                                    e.currentTarget.style.display = 'none';
                                    const placeholder = e.currentTarget.nextElementSibling;
                                    if (placeholder) {
                                      (placeholder as HTMLElement).style.display = 'flex';
                                    }
                                  }}
                                />
                              ) : null}
                              <div
                                style={{
                                  width: '120px',
                                  height: '120px',
                                  maxWidth: '100%',
                                  borderRadius: '50%',
                                  background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                                  display: therapist.profile_image ? 'none' : 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  margin: '0 auto',
                                  border: '4px solid white',
                                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                                  transition: 'all 0.3s ease'
                                }}
                              >
                                <i className="fas fa-user" style={{ fontSize: '3rem', color: 'white' }}></i>
                              </div>
                            </div>

                            <Card.Body className="d-flex flex-column" style={{ padding: '1.5rem', minHeight: '200px' }}>
                              <Card.Title className="mb-3" style={{ fontSize: '1.1rem', fontWeight: 600, lineHeight: '1.4', textAlign: 'center' }}>
                                {therapist.name}
                              </Card.Title>
                              
                              <div className="mb-3" style={{ minHeight: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Badge 
                                  bg="primary" 
                                  title={therapist.specialization}
                                  style={{ 
                                    fontSize: '0.75rem', 
                                    padding: '0.4rem 0.6rem', 
                                    borderRadius: '8px',
                                    marginBottom: '0.5rem',
                                    display: 'inline-block',
                                    maxWidth: '100%',
                                    wordWrap: 'break-word',
                                    whiteSpace: 'normal',
                                    lineHeight: '1.4',
                                    textAlign: 'center',
                                    width: '100%',
                                    cursor: 'help'
                                  }}
                                >
                                  <i className="fas fa-graduation-cap me-1"></i>
                                  {therapist.specialization}
                                </Badge>
                              </div>

                              <div className="mb-4" style={{ flex: '1' }}>
                                <div className="d-flex align-items-center mb-2" style={{ fontSize: '0.9rem' }}>
                                  <i className="fas fa-clock text-primary me-2" style={{ width: '18px' }}></i>
                                  <span>{therapist.experience_years} سال تجربه</span>
                                </div>
                                <div className="d-flex align-items-center mb-2" style={{ fontSize: '0.9rem' }}>
                                  <i className="fas fa-dollar-sign text-primary me-2" style={{ width: '18px' }}></i>
                                  <span>{therapist.hourly_rate.toLocaleString()} تومان/ساعت</span>
                                </div>
                              </div>
                            </Card.Body>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  ) : (
                    <Card style={{ borderRadius: '18px', border: 'none', background: '#f8f9fa' }}>
                      <Card.Body className="text-center" style={{ padding: '5rem 2rem' }}>
                        <div 
                          style={{ 
                            width: '120px',
                            height: '120px',
                            margin: '0 auto 2rem',
                            background: 'linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%)',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <i className="fas fa-search" style={{ fontSize: '3.5rem', color: '#6c757d' }}></i>
                        </div>
                        <h5 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1rem', color: '#495057' }}>
                          درمانگری یافت نشد
                        </h5>
                        <p className="text-muted" style={{ fontSize: '1.05rem', maxWidth: '500px', margin: '0 auto' }}>
                          با فیلترهای انتخابی شما درمانگری یافت نشد. لطفاً فیلترها را تغییر دهید.
                        </p>
                      </Card.Body>
                    </Card>
                  )}
                </div>
              )}

              {/* Step 2: Select Date and Time */}
              {step === 2 && (
                <div>
                  <h4 className="mb-4 text-center">
                    {isRescheduling ? 'تغییر تاریخ و زمان' : 'انتخاب تاریخ و زمان'}
                  </h4>
                  
                  {/* Show selected therapist info */}
                  {selectedTherapist && (
                    <Card className="mb-4" style={{ borderRadius: '12px', border: '1px solid #e9ecef', background: '#f8f9fa' }}>
                      <Card.Body>
                        <div className="d-flex align-items-center">
                          <div className="me-3">
                            {therapists.find(t => t.id === selectedTherapist)?.profile_image ? (
                              <img
                                src={therapists.find(t => t.id === selectedTherapist)?.profile_image}
                                alt={therapists.find(t => t.id === selectedTherapist)?.name || 'Therapist'}
                                loading="lazy"
                                style={{
                                  width: '60px',
                                  height: '60px',
                                  borderRadius: '50%',
                                  objectFit: 'cover',
                                  border: '3px solid white',
                                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                                }}
                              />
                            ) : (
                              <div
                                style={{
                                  width: '60px',
                                  height: '60px',
                                  borderRadius: '50%',
                                  background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  border: '3px solid white',
                                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                                }}
                              >
                                <i className="fas fa-user" style={{ fontSize: '1.5rem', color: 'white' }}></i>
                              </div>
                            )}
                          </div>
                          <div className="flex-grow-1">
                            <h6 className="mb-1">
                              <i className="fas fa-user-md me-2 text-primary"></i>
                              {therapists.find(t => t.id === selectedTherapist)?.name}
                            </h6>
                            <p className="text-muted mb-0">
                              <i className="fas fa-graduation-cap me-1"></i>
                              {therapists.find(t => t.id === selectedTherapist)?.specialization}
                            </p>
                          </div>
                          <Button 
                            variant="outline-secondary" 
                            size="sm"
                            onClick={() => setStep(1)}
                            style={{ borderRadius: '8px' }}
                          >
                            <i className="fas fa-edit me-1"></i>
                            تغییر درمانگر
                          </Button>
                        </div>
                      </Card.Body>
                    </Card>
                  )}
                  
                  {/* Integrated calendar with date and time selection */}
                  <BookingTimeSelectorMUI
                    fetchAvailability={fetchAvailability}
                    onConfirm={(payload) => {
                      setSelectedDate(payload.date);
                      setSelectedTime(payload.time);
                      setStep(3);
                    }}
                    onTimeChange={setSelectedTime}
                    initialISODate={selectedDate ?? undefined}
                    startHour={9}
                    endHour={21}
                    stepMinutes={30}
                    guardMinutesForToday={60}
                  />

                  <div className="d-flex justify-content-between mt-4">
                    <Button variant="outline-secondary" onClick={() => setStep(1)}>
                      <i className="fas fa-arrow-right me-2"></i>
                      قبلی
                    </Button>
                    {selectedDate && selectedTime && (
                      <Button variant="primary" onClick={() => setStep(3)}>
                        ادامه
                        <i className="fas fa-arrow-left ms-2"></i>
                      </Button>
                    )}
                  </div>
                </div>
              )}

              {/* Step 3: Select Type and Location */}
              {step === 3 && (
                <div>
                  <h4 className="mb-4 text-center">
                    {isRescheduling ? 'تایید جزئیات نوبت' : 'انتخاب نوع نوبت و محل'}
                  </h4>
                  
                  {typesLoading || locationsLoading ? (
                    <div className="text-center py-5">
                      <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
                        <span className="visually-hidden">در حال بارگذاری...</span>
                      </div>
                      <p className="text-muted mt-3">در حال بارگذاری...</p>
                    </div>
                  ) : (
                    <Row className="g-4">
                      <Col md={6}>
                        <Card style={{ borderRadius: '12px', border: '1px solid #e9ecef' }}>
                          <Card.Body>
                            <h6 className="text-muted mb-3">
                              <i className="fas fa-calendar-alt me-2"></i>
                              نوع نوبت
                            </h6>
                            <div className="d-grid gap-2">
                              {appointmentTypes && appointmentTypes.length > 0 ? (
                                appointmentTypes.map((type) => (
                                  <Button
                                    key={type.id}
                                    variant={selectedType === type.id ? 'primary' : 'outline-primary'}
                                    onClick={() => setSelectedType(type.id)}
                                    className="text-start"
                                    style={{ borderRadius: '8px' }}
                                  >
                                    <i className="fas fa-clock me-2"></i>
                                    {type.name} ({type.default_duration_minutes} دقیقه)
                                  </Button>
                                ))
                              ) : (
                                <p className="text-muted text-center">هیچ نوع نوبتی یافت نشد</p>
                              )}
                            </div>
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col md={6}>
                        <Card style={{ borderRadius: '12px', border: '1px solid #e9ecef' }}>
                          <Card.Body>
                            <h6 className="text-muted mb-3">
                              <i className="fas fa-map-marker-alt me-2"></i>
                              محل کلینیک
                            </h6>
                            <div className="d-grid gap-2">
                              {locations && locations.length > 0 ? (
                                locations.map((location) => (
                                  <Button
                                    key={location.id}
                                    variant={selectedLocation === location.id ? 'primary' : 'outline-primary'}
                                    onClick={() => setSelectedLocation(location.id)}
                                    className="text-start"
                                    style={{ borderRadius: '8px' }}
                                  >
                                    <i className="fas fa-building me-2"></i>
                                    {location.name} - {location.city}
                                  </Button>
                                ))
                              ) : (
                                <p className="text-muted text-center">هیچ محلی یافت نشد</p>
                              )}
                            </div>
                          </Card.Body>
                        </Card>
                      </Col>
                    </Row>
                  )}
                  
                  <div className="d-flex justify-content-between mt-4">
                    <Button variant="outline-secondary" onClick={() => setStep(2)}>
                      <i className="fas fa-arrow-right me-2"></i>
                      قبلی
                    </Button>
                    {selectedType && selectedLocation && (
                      <Button variant="primary" onClick={() => setStep(4)}>
                        ادامه
                        <i className="fas fa-arrow-left ms-2"></i>
                      </Button>
                    )}
                  </div>
                </div>
              )}

              {/* Step 4: Final Confirmation */}
              {step === 4 && (
                <div>
                  <h4 className="mb-4 text-center">تایید نهایی</h4>
                  <Row className="g-4 mb-4">
                    <Col md={6}>
                      <Card style={{ borderRadius: '12px', border: '1px solid #e9ecef', background: '#f8f9fa' }}>
                        <Card.Body>
                          <h6 className="mb-3">
                            <i className="fas fa-user-md me-2 text-primary"></i>
                            خلاصه نوبت
                          </h6>
                          <div className="mb-2">
                            <strong>درمانگر:</strong> {therapists.find(t => t.id === selectedTherapist)?.name}
                          </div>
                          <div className="mb-2">
                            <strong>تاریخ:</strong> {selectedDate ? new Date(selectedDate).toLocaleDateString('fa-IR') : 'انتخاب نشده'}
                          </div>
                          <div className="mb-2">
                            <strong>زمان:</strong> {selectedTime || 'انتخاب نشده'}
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={6}>
                      <Card style={{ borderRadius: '12px', border: '1px solid #e9ecef', background: '#f8f9fa' }}>
                        <Card.Body>
                          <h6 className="mb-3">
                            <i className="fas fa-info-circle me-2 text-primary"></i>
                            جزئیات
                          </h6>
                          <div className="mb-2">
                            <strong>نوع نوبت:</strong> {appointmentTypes?.find(t => t.id === selectedType)?.name || 'نامشخص'}
                          </div>
                          <div className="mb-2">
                            <strong>مدت زمان:</strong> {selectedAppointmentTypeData?.default_duration_minutes ?? 'نامشخص'} دقیقه
                          </div>
                          <div className="mb-2">
                            <strong>محل:</strong> {locations?.find(l => l.id === selectedLocation)?.name || 'نامشخص'}
                          </div>
                          <div className="mb-2">
                            <strong>هزینه جلسه:</strong> {formatCurrency(selectedAppointmentTypeData?.price)}
                          </div>
                          <div className="mb-0">
                            <strong>ودیعه:</strong> {requiresDeposit ? formatCurrency(selectedDepositAmount) : 'نیاز ندارد'}
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>
                  </Row>
                  
                  <Card className="mb-4" style={{ borderRadius: '12px', border: '1px solid #e9ecef' }}>
                    <Card.Body>
                      <h6 className="text-muted mb-3">
                        <i className="fas fa-sticky-note me-2"></i>
                        یادداشت‌های اضافی (اختیاری)
                      </h6>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        value={notes}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNotes(e.target.value)}
                        placeholder="در صورت نیاز، یادداشت‌های اضافی خود را اینجا بنویسید..."
                        style={{ borderRadius: '8px' }}
                      />
                    </Card.Body>
                  </Card>

                  {requiresDeposit && (
                    <Alert variant="warning" className="mb-4">
                      <div className="d-flex align-items-start">
                        <i className="fas fa-lock me-3 mt-1"></i>
                        <div>
                          <strong>توجه:</strong> برای تکمیل رزرو این نوبت، پرداخت ودیعه {formatCurrency(selectedDepositAmount)} الزامی است. پس از انتخاب دکمه زیر به درگاه پرداخت امن هدایت می‌شوید.
                        </div>
                      </div>
                    </Alert>
                  )}

                  <div className="d-flex justify-content-between">
                    <Button variant="outline-secondary" onClick={() => setStep(3)}>
                      <i className="fas fa-arrow-right me-2"></i>
                      قبلی
                    </Button>
                    <Button 
                      variant="success" 
                      size="lg"
                      disabled={bookAppointmentMutation.isPending}
                      onClick={() => {
                        if (selectedDate && selectedTime) {
                          handleConfirm({ 
                            date: selectedDate, 
                            time: selectedTime 
                          });
                        }
                      }}
                      style={{ borderRadius: '10px', padding: '0.75rem 2rem' }}
                    >
                      {bookAppointmentMutation.isPending ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          {isRescheduling ? 'در حال تغییر...' : 'در حال رزرو...'}
                        </>
                      ) : (
                        <>
                          <i className="fas fa-calendar-check me-2"></i>
                          {isRescheduling ? 'تغییر نوبت' : requiresDeposit ? 'پرداخت ودیعه و رزرو' : 'رزرو نوبت'}
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
        )}
      </Container>

      {/* Call to Action Section */}
      <section 
        className="py-5" 
        style={{ 
          background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
          color: 'white'
        }}
      >
        <Container>
          <Row className="align-items-center">
            <Col lg={8}>
              <h2 className="mb-3">آماده شروع درمان هستید؟</h2>
              <p className="lead mb-4">
                با تیم متخصص ما، مسیر بهبود و رشد شخصی خود را آغاز کنید.
              </p>
            </Col>
            <Col lg={4} className="text-lg-end">
              <div className="d-flex flex-column flex-lg-row gap-3">
                <Button variant="light" size="lg" href="/appointment/booking">
                  <i className="fas fa-calendar-check me-2"></i>
                  رزرو نوبت جدید
                </Button>
                <Button variant="outline-light" size="lg" href="/tests">
                  <i className="fas fa-brain me-2"></i>
                  تست رایگان
                </Button>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
    </>
  );
};

export default AppointmentBookingMUI;
