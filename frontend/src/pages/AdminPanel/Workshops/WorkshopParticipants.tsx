import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Avatar,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Collapse,
} from '@mui/material';
import {
  ArrowBack,
  MoreVert,
  CheckCircle,
  Cancel,
  Person,
  Email,
  CalendarToday,
  AttachMoney,
  TrendingUp,
  Search,
  FilterList,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';
import { workshopRegistrationApi, workshopApi } from '../../../services/workshopAdminApi';
import { format } from 'date-fns';

interface InstallmentPayment {
  id: number;
  installment_number: number;
  amount: string;
  due_date: string;
  due_date_persian: string;
  status: string;
  paid_at?: string;
  paid_at_persian?: string;
  is_overdue: boolean;
}

interface InstallmentPlan {
  id: number;
  total_amount: string;
  number_of_installments: number;
  installment_amount: string;
  total_paid: number;
  remaining_amount: number;
  is_fully_paid: boolean;
  payments: InstallmentPayment[];
}

interface WorkshopRegistration {
  id: number;
  user: number;
  user_name: string;
  user_email: string;
  workshop: number;
  workshop_title: string;
  status: string;
  payment_type: string;
  amount_paid: number;
  total_amount: number;
  progress_percentage: number;
  registered_at: string;
  registered_at_persian: string;
  completed_at?: string;
  completed_at_persian?: string;
  last_accessed?: string;
  last_accessed_persian?: string;
  payment_status: string;
  installment_plan?: InstallmentPlan;
}

const WorkshopParticipants: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedRegistration, setSelectedRegistration] = useState<WorkshopRegistration | null>(null);
  const [actionDialog, setActionDialog] = useState<'approve' | 'reject' | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  const workshopId = parseInt(id || '0');

  // Fetch workshop details
  const { data: workshop, isLoading: workshopLoading } = useQuery({
    queryKey: ['workshop', workshopId],
    queryFn: () => workshopApi.getWorkshop(workshopId),
    enabled: !!workshopId,
  });

  // Fetch participants/registrations
  const { data: registrationsData, isLoading: registrationsLoading } = useQuery({
    queryKey: ['workshop-registrations', workshopId, searchTerm, statusFilter],
    queryFn: () => workshopRegistrationApi.getRegistrations(workshopId, {
      search: searchTerm,
      status: statusFilter,
      ordering: '-registered_at',
    }),
    enabled: !!workshopId,
  });

  // Approve registration mutation
  const approveMutation = useMutation({
    mutationFn: (registrationId: number) => workshopRegistrationApi.approveRegistration(registrationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workshop-registrations', workshopId] });
      setActionDialog(null);
      setSelectedRegistration(null);
    },
  });

  // Reject registration mutation
  const rejectMutation = useMutation({
    mutationFn: ({ registrationId, reason }: { registrationId: number; reason: string }) =>
      workshopRegistrationApi.rejectRegistration(registrationId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workshop-registrations', workshopId] });
      setActionDialog(null);
      setSelectedRegistration(null);
      setRejectionReason('');
    },
  });

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, registration: WorkshopRegistration) => {
    setAnchorEl(event.currentTarget);
    setSelectedRegistration(registration);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedRegistration(null);
  };

  const handleApprove = () => {
    if (selectedRegistration) {
      approveMutation.mutate(selectedRegistration.id);
    }
  };

  const handleReject = () => {
    if (selectedRegistration) {
      rejectMutation.mutate({
        registrationId: selectedRegistration.id,
        reason: rejectionReason,
      });
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      pending_payment: '#f57c00',
      active: '#2e7d32',
      completed: '#388e3c',
      cancelled: '#d32f2f',
    };
    return colors[status as keyof typeof colors] || '#757575';
  };

  const getStatusLabel = (status: string) => {
    const labels = {
      pending_payment: 'در انتظار پرداخت',
      active: 'فعال',
      completed: 'تکمیل شده',
      cancelled: 'لغو شده',
    };
    return labels[status as keyof typeof labels] || status;
  };

  const getPaymentTypeLabel = (paymentType: string) => {
    const labels = {
      full_payment: 'پرداخت کامل',
      installment: 'قسطی',
      both: 'هر دو گزینه',
    };
    return labels[paymentType as keyof typeof labels] || paymentType;
  };

  const toggleRowExpansion = (registrationId: number) => {
    setExpandedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(registrationId)) {
        newSet.delete(registrationId);
      } else {
        newSet.add(registrationId);
      }
      return newSet;
    });
  };

  const getInstallmentStatusLabel = (status: string): string => {
    const labels: { [key: string]: string } = {
      pending: 'در انتظار پرداخت',
      paid: 'پرداخت شده',
      overdue: 'سررسید شده',
      cancelled: 'لغو شده',
    };
    return labels[status] || status;
  };

  const getInstallmentStatusColor = (status: string): "success" | "warning" | "error" | "default" => {
    const colors: { [key: string]: "success" | "warning" | "error" | "default" } = {
      paid: 'success',
      pending: 'warning',
      overdue: 'error',
      cancelled: 'default',
    };
    return colors[status] || 'default';
  };

  if (workshopLoading || registrationsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const registrations = registrationsData?.results || [];
  const totalParticipants = registrationsData?.count || 0;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton onClick={() => navigate('/admin-panel/workshops')}>
          <ArrowBack />
        </IconButton>
        <Box>
          <Typography variant="h4" component="h1">
            شرکت‌کنندگان کارگاه
          </Typography>
          <Typography variant="h6" color="text.secondary">
            {workshop?.title}
          </Typography>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Person color="primary" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h6">{totalParticipants}</Typography>
                <Typography variant="body2" color="text.secondary">
                  کل شرکت‌کنندگان
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CheckCircle color="success" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h6">
                  {registrations.filter((r: WorkshopRegistration) => r.status === 'active').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  فعال
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AttachMoney color="warning" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h6">
                  {registrations
                    .reduce((sum: number, r: WorkshopRegistration) => sum + Number(r.amount_paid || 0), 0)
                    .toLocaleString('fa-IR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  درآمد (تومان)
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <TrendingUp color="info" sx={{ mr: 2 }} />
              <Box>
                <Typography variant="h6">
                  {Math.round(registrations.reduce((sum: number, r: WorkshopRegistration) => sum + r.progress_percentage, 0) / registrations.length || 0)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  میانگین پیشرفت
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'flex-start' }}>
            <Box sx={{ flex: 1, minWidth: 200 }}>
              <TextField
                fullWidth
                placeholder="جستجو در نام، ایمیل..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Box>
            <Box sx={{ width: { xs: '100%', sm: 250 }, flexShrink: 0 }}>
              <TextField
                fullWidth
                select
                label="وضعیت"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                SelectProps={{ native: true }}
                sx={{
                  '& .MuiSelect-select': {
                    paddingRight: '14px !important',
                    paddingLeft: '32px !important',
                  }
                }}
              >
                <option value="">همه وضعیت‌ها</option>
                <option value="pending_payment">در انتظار پرداخت</option>
                <option value="active">فعال</option>
                <option value="completed">تکمیل شده</option>
                <option value="cancelled">لغو شده</option>
              </TextField>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Participants Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox"></TableCell>
                <TableCell>شرکت‌کننده</TableCell>
                <TableCell>وضعیت</TableCell>
                <TableCell>نوع پرداخت</TableCell>
                <TableCell>مبلغ پرداختی</TableCell>
                <TableCell>پیشرفت</TableCell>
                <TableCell>تاریخ ثبت‌نام</TableCell>
                <TableCell>عملیات</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {registrations.map((registration: WorkshopRegistration) => {
                const isExpanded = expandedRows.has(registration.id);
                const hasInstallments = registration.payment_type === 'installment' && registration.installment_plan?.payments && registration.installment_plan.payments.length > 0;
                
                return (
                  <React.Fragment key={registration.id}>
                    <TableRow>
                      <TableCell>
                        {hasInstallments && (
                          <IconButton
                            size="small"
                            onClick={() => toggleRowExpansion(registration.id)}
                          >
                            {isExpanded ? <ExpandLess /> : <ExpandMore />}
                          </IconButton>
                        )}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                            {registration.user_name.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2">{registration.user_name}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {registration.user_email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(registration.status)}
                      color={registration.status === 'active' ? 'success' : 'default'}
                      size="small"
                      sx={{ bgcolor: getStatusColor(registration.status), color: 'white' }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {getPaymentTypeLabel(registration.payment_type)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {Number(registration.amount_paid || 0).toLocaleString('fa-IR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} تومان
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      از {Number(registration.total_amount || 0).toLocaleString('fa-IR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} تومان
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <Box
                          sx={{
                            width: '100%',
                            height: 8,
                            bgcolor: 'grey.300',
                            borderRadius: 1,
                            overflow: 'hidden',
                          }}
                        >
                          <Box
                            sx={{
                              width: `${registration.progress_percentage}%`,
                              height: '100%',
                              bgcolor: 'primary.main',
                              transition: 'width 0.3s ease',
                            }}
                          />
                        </Box>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {registration.progress_percentage}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {registration.registered_at_persian}
                    </Typography>
                  </TableCell>
                      <TableCell>
                        <IconButton
                          onClick={(e) => handleMenuClick(e, registration)}
                          size="small"
                        >
                          <MoreVert />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                    
                    {/* Expanded Installments Table */}
                    {hasInstallments && (
                      <TableRow>
                        <TableCell colSpan={8} sx={{ py: 0, borderBottom: 'none' }}>
                          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                            <Box sx={{ margin: 2 }}>
                              <Typography variant="h6" sx={{ mb: 2 }}>
                                اقساط
                              </Typography>
                              <Table size="small">
                                <TableHead>
                                  <TableRow>
                                    <TableCell>قسط</TableCell>
                                    <TableCell>مبلغ</TableCell>
                                    <TableCell>سررسید</TableCell>
                                    <TableCell>وضعیت</TableCell>
                                    <TableCell>تاریخ پرداخت</TableCell>
                                  </TableRow>
                                </TableHead>
                                <TableBody>
                                  {registration.installment_plan!.payments.map((payment) => (
                                    <TableRow 
                                      key={payment.id}
                                      sx={{ 
                                        bgcolor: payment.is_overdue ? 'error.light' : 'inherit',
                                        opacity: payment.is_overdue ? 0.8 : 1
                                      }}
                                    >
                                      <TableCell>قسط {payment.installment_number}</TableCell>
                                      <TableCell>
                                        {Number(payment.amount || 0).toLocaleString('fa-IR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} تومان
                                      </TableCell>
                                      <TableCell>{payment.due_date_persian}</TableCell>
                                      <TableCell>
                                        <Chip
                                          label={getInstallmentStatusLabel(payment.status)}
                                          color={getInstallmentStatusColor(payment.status)}
                                          size="small"
                                        />
                                      </TableCell>
                                      <TableCell>
                                        {payment.paid_at_persian || '-'}
                                      </TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    )}
                  </React.Fragment>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {selectedRegistration?.status === 'pending_payment' && (
          <>
            <MenuItem onClick={() => { setActionDialog('approve'); handleMenuClose(); }}>
              <ListItemIcon>
                <CheckCircle color="success" />
              </ListItemIcon>
              <ListItemText>تایید ثبت‌نام</ListItemText>
            </MenuItem>
            <MenuItem onClick={() => { setActionDialog('reject'); handleMenuClose(); }}>
              <ListItemIcon>
                <Cancel color="error" />
              </ListItemIcon>
              <ListItemText>رد ثبت‌نام</ListItemText>
            </MenuItem>
          </>
        )}
      </Menu>

      {/* Approve Dialog */}
      <Dialog open={actionDialog === 'approve'} onClose={() => setActionDialog(null)}>
        <DialogTitle>تایید ثبت‌نام</DialogTitle>
        <DialogContent>
          <Typography>
            آیا از تایید ثبت‌نام {selectedRegistration?.user_name} اطمینان دارید؟
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog(null)}>انصراف</Button>
          <Button
            onClick={handleApprove}
            variant="contained"
            color="success"
            disabled={approveMutation.isPending}
          >
            {approveMutation.isPending ? <CircularProgress size={20} /> : 'تایید'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={actionDialog === 'reject'} onClose={() => setActionDialog(null)}>
        <DialogTitle>رد ثبت‌نام</DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            آیا از رد ثبت‌نام {selectedRegistration?.user_name} اطمینان دارید؟
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="دلیل رد (اختیاری)"
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder="دلیل رد ثبت‌نام را وارد کنید..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionDialog(null)}>انصراف</Button>
          <Button
            onClick={handleReject}
            variant="contained"
            color="error"
            disabled={rejectMutation.isPending}
          >
            {rejectMutation.isPending ? <CircularProgress size={20} /> : 'رد'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkshopParticipants;
