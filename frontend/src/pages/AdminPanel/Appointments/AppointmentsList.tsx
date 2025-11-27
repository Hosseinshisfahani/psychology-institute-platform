import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Avatar,
  Tooltip,
  Alert,
  CircularProgress,
  Pagination,
  Stack,
  Divider,
  Badge,
  useTheme,
  alpha,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Cancel as CancelIcon,
  CheckCircle as ConfirmIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  LocationOn as LocationIcon,
  AccessTime as TimeIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  CalendarToday as CalendarIcon,
  CheckCircle,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import { Helmet } from 'react-helmet-async';
import axios from 'axios';
import DatePicker from 'react-multi-date-picker';
import DateObject from 'react-date-object';
import persian from 'react-date-object/calendars/persian';
import gregorian from 'react-date-object/calendars/gregorian';
import persian_fa from 'react-date-object/locales/persian_fa';
import gregorian_en from 'react-date-object/locales/gregorian_en';

interface Appointment {
  id: number;
  client: number;
  client_name: string;
  therapist: number;
  therapist_name: string;
  appointment_type: number;
  appointment_type_name: string;
  location: number;
  location_name: string;
  scheduled_datetime: string;
  duration_minutes: number;
  status: string;
  status_display: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface AppointmentFilters {
  status: string;
  therapist: string;
  date_from: string;
  date_to: string;
  search: string;
}

const AppointmentsList: React.FC = () => {
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();
  
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [filters, setFilters] = useState<AppointmentFilters>({
    status: '',
    therapist: '',
    date_from: '',
    date_to: '',
    search: '',
  });
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [cancellationReason, setCancellationReason] = useState<string>('');
  const [requiresCancellationConfirm, setRequiresCancellationConfirm] = useState<boolean>(false);
  const [actionDialog, setActionDialog] = useState<{
    open: boolean;
    type: 'view' | 'edit' | 'cancel' | 'confirm';
    appointment: Appointment | null;
  }>({
    open: false,
    type: 'view',
    appointment: null,
  });

  // Fetch appointments
  const { data: appointmentsData, isLoading, error } = useQuery({
    queryKey: ['admin-appointments', page, filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== '')),
      });
      
      const response = await axios.get(`/api/appointments/?${params}`);
      return response.data;
    },
  });

  // Fetch appointment statistics
  const { data: statistics } = useQuery({
    queryKey: ['appointment-statistics'],
    queryFn: async () => {
      const response = await axios.get('/api/appointments/statistics/');
      return response.data;
    },
  });

  // Fetch therapists for filter
  const { data: therapists = [] } = useQuery({
    queryKey: ['therapists'],
    queryFn: async () => {
      const response = await axios.get('/api/appointments/therapists/');
      return response.data;
    },
  });

  // Update appointment status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status, notes }: { id: number; status: string; notes?: string }) => {
      const response = await axios.patch(`/api/appointments/${id}/`, { status, notes });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-appointments'] });
      enqueueSnackbar('وضعیت نوبت با موفقیت به‌روزرسانی شد', { variant: 'success' });
      setActionDialog({ open: false, type: 'view', appointment: null });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.detail || 'خطا در به‌روزرسانی وضعیت', { variant: 'error' });
    },
  });

  // Cancel appointment mutation
  const cancelAppointmentMutation = useMutation({
    mutationFn: async ({ id, reason, confirm }: { id: number; reason: string; confirm?: boolean }) => {
      const response = await axios.post(`/api/appointments/${id}/cancel/`, { reason, confirm: confirm || false });
      
      // If requires confirmation, return the response so we can handle it
      if (response.data?.requires_confirmation) {
        return response.data;
      }
      
      return response.data;
    },
    onSuccess: (data) => {
      // If confirmation is required, show warning and don't close dialog
      if (data?.requires_confirmation) {
        setRequiresCancellationConfirm(true);
        enqueueSnackbar(data.warning || 'نیاز به تأیید مجدد', { variant: 'warning' });
        return;
      }
      
      queryClient.invalidateQueries({ queryKey: ['admin-appointments'] });
      queryClient.invalidateQueries({ queryKey: ['appointment-statistics'] });
      enqueueSnackbar('نوبت با موفقیت لغو شد', { variant: 'success' });
      setActionDialog({ open: false, type: 'view', appointment: null });
      setRequiresCancellationConfirm(false);
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || error.response?.data?.detail || 'خطا در لغو نوبت', { variant: 'error' });
    },
  });

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, appointment: Appointment) => {
    setAnchorEl(event.currentTarget);
    setSelectedAppointment(appointment);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedAppointment(null);
  };

  const handleAction = (type: 'view' | 'edit' | 'cancel' | 'confirm') => {
    if (selectedAppointment) {
      setActionDialog({ open: true, type, appointment: selectedAppointment });
      if (type === 'cancel') {
        setCancellationReason('');
        setRequiresCancellationConfirm(false);
      }
    }
    handleMenuClose();
  };

  const handleFilterChange = (field: keyof AppointmentFilters, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPage(1);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'primary';
      case 'confirmed':
        return 'success';
      case 'completed':
        return 'info';
      case 'cancelled':
        return 'error';
      case 'no_show':
        return 'warning';
      case 'rescheduled':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('fa-IR', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  };

  const appointments = appointmentsData?.results || [];
  const totalPages = Math.ceil((appointmentsData?.count || 0) / pageSize);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        خطا در بارگذاری نوبت‌ها. لطفاً دوباره تلاش کنید.
      </Alert>
    );
  }

  return (
    <>
      <Helmet>
        <title>مدیریت نوبت‌ها - پنل مدیریت</title>
        <meta name="description" content="مدیریت و نظارت بر نوبت‌های سیستم" />
      </Helmet>

      <Box>
        {/* Header */}
        <Box display="flex" justifyContent="flex-start" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              مدیریت نوبت‌ها
            </Typography>
            <Typography variant="body1" color="text.secondary">
              نظارت و مدیریت نوبت‌های سیستم
            </Typography>
          </Box>
        </Box>

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
              <Box sx={{ flex: '1 1 300px', minWidth: '200px' }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="جستجو بر اساس کاربر (نام، ایمیل، تلفن، کد ملی)..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Box>
              <Box sx={{ flex: '1 1 200px', minWidth: '150px' }}>
                <FormControl fullWidth size="small">
                  <InputLabel>وضعیت</InputLabel>
                  <Select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    label="وضعیت"
                  >
                    <MenuItem value="">همه</MenuItem>
                    <MenuItem value="scheduled">رزرو شده</MenuItem>
                    <MenuItem value="confirmed">تأیید شده</MenuItem>
                    <MenuItem value="completed">تکمیل شده</MenuItem>
                    <MenuItem value="cancelled">لغو شده</MenuItem>
                    <MenuItem value="no_show">عدم حضور</MenuItem>
                    <MenuItem value="rescheduled">تغییر زمان</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              <Box sx={{ flex: '1 1 200px', minWidth: '150px' }}>
                <FormControl fullWidth size="small">
                  <InputLabel>درمانگر</InputLabel>
                  <Select
                    value={filters.therapist}
                    onChange={(e) => handleFilterChange('therapist', e.target.value)}
                    label="درمانگر"
                  >
                    <MenuItem value="">همه</MenuItem>
                    {therapists.map((therapist: any) => (
                      <MenuItem key={therapist.id} value={therapist.id}>
                        {therapist.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
              <Box sx={{ flex: '1 1 150px', minWidth: '120px' }}>
                <DatePicker
                  calendar={persian}
                  locale={persian_fa}
                  value={
                    filters.date_from
                      ? new DateObject({ date: filters.date_from, calendar: gregorian, locale: gregorian_en })
                      : null
                  }
                  onChange={(date: any) => {
                    const value = date ? (date instanceof DateObject ? date.toDate() : new Date(date)).toISOString().split('T')[0] : '';
                    handleFilterChange('date_from', value);
                  }}
                  format="YYYY/MM/DD"
                  inputClass="MuiInputBase-input MuiInput-input MuiInputBase-inputSizeSmall"
                  style={{ width: '100%', height: 40, background: 'transparent', color: 'inherit' }}
                  placeholder="از تاریخ"
                />
              </Box>
              <Box sx={{ flex: '1 1 150px', minWidth: '120px' }}>
                <DatePicker
                  calendar={persian}
                  locale={persian_fa}
                  value={
                    filters.date_to
                      ? new DateObject({ date: filters.date_to, calendar: gregorian, locale: gregorian_en })
                      : null
                  }
                  onChange={(date: any) => {
                    const value = date ? (date instanceof DateObject ? date.toDate() : new Date(date)).toISOString().split('T')[0] : '';
                    handleFilterChange('date_to', value);
                  }}
                  format="YYYY/MM/DD"
                  inputClass="MuiInputBase-input MuiInput-input MuiInputBase-inputSizeSmall"
                  style={{ width: '100%', height: 40, background: 'transparent', color: 'inherit' }}
                  placeholder="تا تاریخ"
                />
              </Box>
              <Box sx={{ flex: '0 0 auto' }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={() => {
                    setFilters({ status: '', therapist: '', date_from: '', date_to: '', search: '' });
                    setPage(1);
                  }}
                >
                  پاک کردن
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Statistics Cards */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 3 }}>
          <Box sx={{ flex: '1 1 250px', minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                    <CalendarIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      {statistics?.total_appointments || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      کل نوبت‌ها
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 250px', minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                    <CheckCircle />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      {statistics?.confirmed || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      تأیید شده
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 250px', minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                    <ScheduleIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      {statistics?.scheduled || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      رزرو شده
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
          <Box sx={{ flex: '1 1 250px', minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Avatar sx={{ bgcolor: 'error.main', mr: 2 }}>
                    <CancelIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      {statistics?.cancelled || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      لغو شده
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* Appointments Table */}
        <Card>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>مراجع</TableCell>
                  <TableCell>درمانگر</TableCell>
                  <TableCell>نوع نوبت</TableCell>
                  <TableCell>محل</TableCell>
                  <TableCell>تاریخ و زمان</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {appointments.map((appointment: Appointment) => (
                  <TableRow key={appointment.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar sx={{ width: 32, height: 32, mr: 2 }}>
                          {appointment.client_name.charAt(0)}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {appointment.client_name}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />
                        <Typography variant="body2">
                          {appointment.therapist_name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {appointment.appointment_type_name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <LocationIcon sx={{ mr: 1, color: 'text.secondary' }} />
                        <Typography variant="body2">
                          {appointment.location_name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {formatDate(appointment.scheduled_datetime)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          <TimeIcon sx={{ fontSize: 12, mr: 0.5 }} />
                          {formatTime(appointment.scheduled_datetime)} ({appointment.duration_minutes} دقیقه)
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={appointment.status_display}
                        color={getStatusColor(appointment.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        onClick={(e) => handleMenuOpen(e, appointment)}
                        size="small"
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" p={2}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, newPage) => setPage(newPage)}
                color="primary"
              />
            </Box>
          )}
        </Card>

        {/* Action Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => handleAction('view')}>
            <ViewIcon sx={{ mr: 1 }} />
            مشاهده جزئیات
          </MenuItem>
          <MenuItem onClick={() => handleAction('edit')}>
            <EditIcon sx={{ mr: 1 }} />
            ویرایش
          </MenuItem>
          {selectedAppointment?.status === 'scheduled' && (
            <MenuItem onClick={() => handleAction('confirm')}>
              <ConfirmIcon sx={{ mr: 1 }} />
              تأیید نوبت
            </MenuItem>
          )}
          {selectedAppointment?.status !== 'cancelled' && selectedAppointment?.status !== 'completed' && (
            <MenuItem onClick={() => handleAction('cancel')}>
              <CancelIcon sx={{ mr: 1 }} />
              لغو نوبت
            </MenuItem>
          )}
        </Menu>

        {/* Action Dialog */}
        <Dialog
          open={actionDialog.open}
          onClose={() => {
            setActionDialog({ open: false, type: 'view', appointment: null });
            setCancellationReason('');
            setRequiresCancellationConfirm(false);
          }}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            {actionDialog.type === 'view' && 'جزئیات نوبت'}
            {actionDialog.type === 'edit' && 'ویرایش نوبت'}
            {actionDialog.type === 'confirm' && 'تأیید نوبت'}
            {actionDialog.type === 'cancel' && 'لغو نوبت'}
          </DialogTitle>
          <DialogContent>
            {actionDialog.appointment && (
              <Box>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      مراجع: {actionDialog.appointment.client_name}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      درمانگر: {actionDialog.appointment.therapist_name}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      تاریخ: {formatDate(actionDialog.appointment.scheduled_datetime)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      زمان: {formatTime(actionDialog.appointment.scheduled_datetime)}
                    </Typography>
                  </Box>
                  {actionDialog.type === 'cancel' && (
                    <Box>
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label="دلیل لغو"
                        placeholder="دلیل لغو نوبت را وارد کنید..."
                        value={cancellationReason}
                        onChange={(e) => setCancellationReason(e.target.value)}
                      />
                    </Box>
                  )}
                </Box>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setActionDialog({ open: false, type: 'view', appointment: null })}>
              انصراف
            </Button>
            {actionDialog.type === 'confirm' && (
              <Button
                variant="contained"
                onClick={() => {
                  if (actionDialog.appointment) {
                    updateStatusMutation.mutate({
                      id: actionDialog.appointment.id,
                      status: 'confirmed',
                    });
                  }
                }}
                disabled={updateStatusMutation.isPending}
              >
                تأیید
              </Button>
            )}
            {actionDialog.type === 'cancel' && (
              <Button
                variant="contained"
                color="error"
                onClick={() => {
                  if (actionDialog.appointment) {
                    cancelAppointmentMutation.mutate({
                      id: actionDialog.appointment.id,
                      reason: cancellationReason || 'لغو توسط مدیر',
                      confirm: requiresCancellationConfirm || false,
                    });
                  }
                }}
                disabled={cancelAppointmentMutation.isPending}
              >
                {requiresCancellationConfirm ? 'تأیید لغو نوبت' : 'لغو نوبت'}
              </Button>
            )}
          </DialogActions>
        </Dialog>
      </Box>
    </>
  );
};

export default AppointmentsList;
