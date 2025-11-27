import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Tooltip,
  Avatar,
  FormControl,
  InputLabel,
  Select,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  Stack,
  Card,
  CardContent,
} from '@mui/material';
import {
  Edit as EditIcon,
  Visibility as ViewIcon,
  Block as BlockIcon,
  CheckCircle as ActiveIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import AdminDataTable, { Column } from '../../../components/Admin/Tables/AdminDataTable';
import { useSnackbar } from 'notistack';

// Section type labels in Persian
const getSectionLabel = (itemType: string): string => {
  const labels: Record<string, string> = {
    course: 'دوره',
    workshop: 'کارگاه',
    package: 'پکیج',
    test: 'آزمون',
    session: 'جلسه',
    appointment_deposit: 'رزرو نوبت',
  };
  return labels[itemType] || itemType;
};

const formatCurrency = (v: number | string) => {
  const num = typeof v === 'string' ? parseFloat(v) : v;
  return num.toLocaleString('fa-IR');
};

// Financial Logs Component
interface FinancialLog {
  order_id: number;
  order_number: string;
  status: string;
  payment_status: string;
  subtotal: string;
  tax_amount: string;
  discount_amount: string;
  total_amount: string;
  payment_method: string | null;
  transaction_id: string | null;
  created_at: string;
  paid_at: string | null;
  items: Array<{
    id: number;
    item_type: string;
    item_title: string;
    quantity: number;
    unit_price: string;
    total_price: string;
  }>;
  payments: Array<{
    id: number;
    amount: string;
    status: string;
    method: string;
    gateway_transaction_id: string | null;
    created_at: string;
    completed_at: string | null;
  }>;
}

interface FinancialLogsData {
  user: {
    id: number;
    full_name: string;
    email: string;
  };
  summary: {
    total_orders: number;
    total_spent: string;
    total_refunded: string;
  };
  logs: FinancialLog[];
}

const UserFinancialLogs: React.FC<{ userId: number }> = ({ userId }) => {
  const { data, isLoading } = useQuery<FinancialLogsData>({
    queryKey: ['admin-user-financial-logs', userId],
    queryFn: async () => {
      const response = await axios.get(`/api/admin/users/${userId}/financial-logs/`);
      return response.data;
    },
  });

  if (isLoading) {
    return <Typography>در حال بارگذاری...</Typography>;
  }

  if (!data) {
    return <Typography color="text.secondary">داده‌ای یافت نشد</Typography>;
  }

  return (
    <Box>
      {/* Summary Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 2, mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">تعداد سفارش‌ها</Typography>
            <Typography variant="h5">{data.summary.total_orders}</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">مجموع پرداخت‌ها</Typography>
            <Typography variant="h5" color="success.main">
              {formatCurrency(data.summary.total_spent)} تومان
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Typography variant="body2" color="text.secondary">مجموع بازگشت‌ها</Typography>
            <Typography variant="h5" color="error.main">
              {formatCurrency(data.summary.total_refunded)} تومان
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Financial Logs Table */}
      {data.logs.length === 0 ? (
        <Typography align="center" color="text.secondary" sx={{ py: 4 }}>
          هیچ تراکنش مالی‌ای یافت نشد
        </Typography>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>شماره سفارش</TableCell>
                <TableCell>بخش</TableCell>
                <TableCell>مبلغ کل</TableCell>
                <TableCell>وضعیت سفارش</TableCell>
                <TableCell>وضعیت پرداخت</TableCell>
                <TableCell>تاریخ</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.logs.map((log) => (
                <TableRow key={log.order_id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>
                      {log.order_number}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap">
                      {log.items.map((item, idx) => (
                        <Chip
                          key={idx}
                          label={getSectionLabel(item.item_type)}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>
                      {formatCurrency(log.total_amount)} تومان
                    </Typography>
                    {parseFloat(log.discount_amount) > 0 && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        تخفیف: {formatCurrency(log.discount_amount)} تومان
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={log.status}
                      size="small"
                      color={
                        log.status === 'paid' ? 'success' :
                        log.status === 'cancelled' || log.status === 'refunded' ? 'error' :
                        'default'
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={log.payment_status}
                      size="small"
                      color={
                        log.payment_status === 'paid' ? 'success' :
                        log.payment_status === 'failed' ? 'error' :
                        'default'
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(log.created_at).toLocaleDateString('fa-IR')}
                    </Typography>
                    {log.paid_at && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        پرداخت: {new Date(log.paid_at).toLocaleDateString('fa-IR')}
                      </Typography>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  user_type: string;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  phone_number?: string;
}

const UsersList: React.FC = () => {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [filters, setFilters] = useState({
    search: '',
    user_type: '',
    status: '',
  });
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editUser, setEditUser] = useState<User | null>(null);
  const [detailTab, setDetailTab] = useState(0);

  // Fetch users
  const { data, isLoading } = useQuery({
    queryKey: ['admin-users', page, rowsPerPage, filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: (page + 1).toString(),
        page_size: rowsPerPage.toString(),
        ...(filters.search && { search: filters.search }),
        ...(filters.user_type && { user_type: filters.user_type }),
        ...(filters.status && { is_active: filters.status }),
      });
      const response = await axios.get(`/api/admin/users/?${params}`);
      return response.data;
    },
  });

  // Toggle user status mutation
  const toggleStatusMutation = useMutation({
    mutationFn: async (userId: number) => {
      const response = await axios.post(`/api/admin/users/${userId}/toggle-status/`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      enqueueSnackbar('وضعیت کاربر با موفقیت تغییر کرد', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('خطا در تغییر وضعیت کاربر', { variant: 'error' });
    },
  });

  // Bulk delete mutation
  const bulkDeleteMutation = useMutation({
    mutationFn: async (userIds: number[]) => {
      const response = await axios.post('/api/admin/users/bulk-action/', {
        action: 'delete',
        user_ids: userIds,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      enqueueSnackbar('کاربران با موفقیت حذف شدند', { variant: 'success' });
    },
    onError: () => {
      enqueueSnackbar('خطا در حذف کاربران', { variant: 'error' });
    },
  });

  // Update user mutation
  const updateUserMutation = useMutation({
    mutationFn: async ({ userId, userData }: { userId: number; userData: Partial<User> }) => {
      const response = await axios.patch(`/api/admin/users/${userId}/`, userData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      enqueueSnackbar('کاربر با موفقیت بروزرسانی شد', { variant: 'success' });
      setEditDialogOpen(false);
      setEditUser(null);
    },
    onError: () => {
      enqueueSnackbar('خطا در بروزرسانی کاربر', { variant: 'error' });
    },
  });

  const columns: Column[] = [
    {
      id: 'full_name',
      label: 'نام و نام خانوادگی',
      minWidth: 200,
      sortable: true,
      format: (value, row) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ width: 32, height: 32 }}>
            {row.first_name?.charAt(0) || row.email?.charAt(0)}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight={600}>
              {value || row.email}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {row.email}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      id: 'user_type',
      label: 'نوع کاربر',
      minWidth: 120,
      format: (value) => {
        const typeMap: Record<string, { label: string; color: any }> = {
          admin: { label: 'مدیر', color: 'error' },
          therapist: { label: 'مشاور', color: 'primary' },
          instructor: { label: 'مدرس', color: 'secondary' },
          client: { label: 'کاربر', color: 'default' },
        };
        const type = typeMap[value] || { label: value, color: 'default' };
        return <Chip label={type.label} color={type.color} size="small" />;
      },
    },
    {
      id: 'is_active',
      label: 'وضعیت',
      minWidth: 100,
      format: (value) => (
        <Chip
          label={value ? 'فعال' : 'غیرفعال'}
          color={value ? 'success' : 'default'}
          size="small"
          icon={value ? <ActiveIcon /> : <BlockIcon />}
        />
      ),
    },
    {
      id: 'date_joined',
      label: 'تاریخ عضویت',
      minWidth: 150,
      format: (value) => new Date(value).toLocaleDateString('fa-IR'),
    },
    {
      id: 'last_login',
      label: 'آخرین ورود',
      minWidth: 150,
      format: (value) => 
        value ? new Date(value).toLocaleDateString('fa-IR') : 'هرگز',
    },
    {
      id: 'actions',
      label: 'عملیات',
      minWidth: 150,
      align: 'center',
      format: (_value, row) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
          <Tooltip title="مشاهده جزئیات">
            <IconButton
              size="small"
              color="info"
              onClick={() => {
                setSelectedUser(row);
                setDetailDialogOpen(true);
              }}
            >
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="ویرایش">
            <IconButton 
              size="small" 
              color="primary"
              onClick={() => {
                setEditUser(row);
                setEditDialogOpen(true);
              }}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title={row.is_active ? 'غیرفعال کردن' : 'فعال کردن'}>
            <IconButton
              size="small"
              color={row.is_active ? 'error' : 'success'}
              onClick={() => toggleStatusMutation.mutate(row.id)}
            >
              {row.is_active ? <BlockIcon fontSize="small" /> : <ActiveIcon fontSize="small" />}
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  const handleDelete = (selected: User[]) => {
    if (window.confirm(`آیا از حذف ${selected.length} کاربر اطمینان دارید؟`)) {
      bulkDeleteMutation.mutate(selected.map((u) => u.id));
    }
  };

  const handleExport = async () => {
    try {
      const response = await axios.get('/api/admin/users/export/', {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `users_${new Date().toISOString()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      enqueueSnackbar('فایل با موفقیت دانلود شد', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('خطا در دانلود فایل', { variant: 'error' });
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          مدیریت کاربران
        </Typography>
        <Typography variant="body1" color="text.secondary">
          مشاهده و مدیریت کاربران سیستم
        </Typography>
      </Box>

      {/* Filters */}
      <Box sx={{ mb: 3, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 2 }}>
        <TextField
          id="user-search-filter"
          fullWidth
          label="جستجو بر اساس نام، ایمیل"
          placeholder="جستجو بر اساس نام، ایمیل..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          InputLabelProps={{
            htmlFor: 'user-search-filter'
          }}
        />
        <FormControl fullWidth>
          <InputLabel id="user-type-filter-label">نوع کاربر</InputLabel>
          <Select
            id="user-type-filter"
            labelId="user-type-filter-label"
            value={filters.user_type}
            label="نوع کاربر"
            onChange={(e) => setFilters({ ...filters, user_type: e.target.value })}
          >
            <MenuItem value="">همه</MenuItem>
            <MenuItem value="admin">مدیر</MenuItem>
            <MenuItem value="therapist">مشاور</MenuItem>
            <MenuItem value="instructor">مدرس</MenuItem>
            <MenuItem value="client">کاربر</MenuItem>
          </Select>
        </FormControl>
        <FormControl fullWidth>
          <InputLabel id="user-status-filter-label">وضعیت</InputLabel>
          <Select
            id="user-status-filter"
            labelId="user-status-filter-label"
            value={filters.status}
            label="وضعیت"
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <MenuItem value="">همه</MenuItem>
            <MenuItem value="true">فعال</MenuItem>
            <MenuItem value="false">غیرفعال</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Data Table */}
      <AdminDataTable
        columns={columns}
        rows={data?.results || []}
        loading={isLoading}
        page={page}
        rowsPerPage={rowsPerPage}
        totalCount={data?.count || 0}
        onPageChange={setPage}
        onRowsPerPageChange={setRowsPerPage}
        onDelete={handleDelete}
        onExport={handleExport}
        title="لیست کاربران"
      />

      {/* User Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => {
          setDetailDialogOpen(false);
          setDetailTab(0);
        }}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>جزئیات کاربر</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Box>
              <Tabs value={detailTab} onChange={(e, newValue) => setDetailTab(newValue)} sx={{ mb: 2 }}>
                <Tab label="اطلاعات" />
                <Tab label="گزارش مالی" />
              </Tabs>
              
              {detailTab === 0 && (
                <Box sx={{ pt: 2, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 2 }}>
                  <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                    <Typography variant="body2" color="text.secondary">
                      نام و نام خانوادگی
                    </Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {selectedUser.full_name || '-'}
                    </Typography>
                  </Box>
                  <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                    <Typography variant="body2" color="text.secondary">
                      ایمیل
                    </Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {selectedUser.email}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      نوع کاربر
                    </Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {selectedUser.user_type}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      وضعیت
                    </Typography>
                    <Chip
                      label={selectedUser.is_active ? 'فعال' : 'غیرفعال'}
                      color={selectedUser.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      تاریخ عضویت
                    </Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {new Date(selectedUser.date_joined).toLocaleDateString('fa-IR')}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      آخرین ورود
                    </Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {selectedUser.last_login
                        ? new Date(selectedUser.last_login).toLocaleDateString('fa-IR')
                        : 'هرگز'}
                    </Typography>
                  </Box>
                </Box>
              )}
              
              {detailTab === 1 && selectedUser && (
                <UserFinancialLogs userId={selectedUser.id} />
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setDetailDialogOpen(false);
            setDetailTab(0);
          }}>بستن</Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>ویرایش کاربر</DialogTitle>
        <DialogContent>
          {editUser && (
            <Box sx={{ pt: 2, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 2 }}>
              <TextField
                fullWidth
                label="نام"
                value={editUser.first_name || ''}
                onChange={(e) => setEditUser({ ...editUser, first_name: e.target.value })}
                sx={{ gridColumn: { xs: '1', sm: '1' } }}
              />
              <TextField
                fullWidth
                label="نام خانوادگی"
                value={editUser.last_name || ''}
                onChange={(e) => setEditUser({ ...editUser, last_name: e.target.value })}
                sx={{ gridColumn: { xs: '1', sm: '2' } }}
              />
              <TextField
                fullWidth
                label="ایمیل"
                value={editUser.email}
                onChange={(e) => setEditUser({ ...editUser, email: e.target.value })}
                sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}
              />
              <TextField
                fullWidth
                label="شماره تلفن"
                value={editUser.phone_number || ''}
                onChange={(e) => setEditUser({ ...editUser, phone_number: e.target.value })}
                sx={{ gridColumn: { xs: '1', sm: '1' } }}
              />
              <FormControl fullWidth sx={{ gridColumn: { xs: '1', sm: '2' } }}>
                <InputLabel>نوع کاربر</InputLabel>
                <Select
                  value={editUser.user_type}
                  label="نوع کاربر"
                  onChange={(e) => setEditUser({ ...editUser, user_type: e.target.value })}
                >
                  <MenuItem value="admin">مدیر</MenuItem>
                  <MenuItem value="therapist">مشاور</MenuItem>
                  <MenuItem value="instructor">مدرس</MenuItem>
                  <MenuItem value="client">کاربر</MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>لغو</Button>
          <Button 
            variant="contained" 
            onClick={() => {
              if (editUser) {
                updateUserMutation.mutate({ 
                  userId: editUser.id, 
                  userData: {
                    first_name: editUser.first_name,
                    last_name: editUser.last_name,
                    email: editUser.email,
                    phone_number: editUser.phone_number,
                    user_type: editUser.user_type
                  }
                });
              }
            }}
            disabled={updateUserMutation.isPending}
          >
            ذخیره
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UsersList;

