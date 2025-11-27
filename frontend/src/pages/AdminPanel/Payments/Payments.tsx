import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Box, Card, CardContent, Typography, Stack, Chip, Divider, Tooltip, IconButton, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import { AreaChart, Area, XAxis, YAxis, Tooltip as ReTooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell, Legend } from 'recharts';
import { paymentsAdminApi } from '../../../services/paymentsAdminApi';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const formatCurrency = (v: number) => v.toLocaleString('fa-IR');

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

const KPICard: React.FC<{ title: string; value: string; subtitle?: string }> = ({ title, value, subtitle }) => (
  <Card>
    <CardContent>
      <Stack spacing={0.5}>
        <Typography variant="body2" color="text.secondary">{title}</Typography>
        <Typography variant="h5">{value}</Typography>
        {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
      </Stack>
    </CardContent>
  </Card>
);

const AdminPayments: React.FC = () => {
  const [sectionFilter, setSectionFilter] = useState<string>('');

  const overviewQuery = useQuery({
    queryKey: ['admin-payments-overview', sectionFilter],
    queryFn: () => paymentsAdminApi.getOverview(sectionFilter || undefined),
  });

  const revenueSeriesQuery = useQuery({
    queryKey: ['admin-payments-revenue-series', sectionFilter],
    queryFn: () => paymentsAdminApi.getRevenueSeries(30, sectionFilter || undefined),
  });

  const recentPaymentsQuery = useQuery({
    queryKey: ['admin-recent-payments', sectionFilter],
    queryFn: () => paymentsAdminApi.getRecentPayments(sectionFilter || undefined),
  });

  const isLoading = overviewQuery.isLoading || revenueSeriesQuery.isLoading || recentPaymentsQuery.isLoading;

  const overview = overviewQuery.data || {
    totalRevenue: 0,
    totalOrders: 0,
    completedPayments: 0,
    failedPayments: 0,
    refunds: 0,
  };

  const revenueSeries = revenueSeriesQuery.data || [];

  // Static distribution until backend provides real breakdown
  const methodDistribution = [
    { name: 'زرین‌پال', value: overview.completedPayments },
    { name: 'سایر', value: overview.failedPayments + overview.refunds },
  ];

  return (
    <Box p={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">مدیریت پرداخت‌ها</Typography>
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>فیلتر بر اساس بخش</InputLabel>
            <Select
              value={sectionFilter}
              onChange={(e) => setSectionFilter(e.target.value)}
              label="فیلتر بر اساس بخش"
            >
              <MenuItem value="">همه بخش‌ها</MenuItem>
              <MenuItem value="course">دوره‌ها</MenuItem>
              <MenuItem value="workshop">کارگاه‌ها</MenuItem>
              <MenuItem value="package">پکیج‌ها</MenuItem>
              <MenuItem value="test">آزمون‌ها</MenuItem>
              <MenuItem value="session">جلسات</MenuItem>
              <MenuItem value="appointment_deposit">رزرو نوبت</MenuItem>
            </Select>
          </FormControl>
          <Tooltip title="بازخوانی">
            <span>
              <IconButton onClick={() => { overviewQuery.refetch(); revenueSeriesQuery.refetch(); recentPaymentsQuery.refetch(); }} disabled={isLoading}>
                <RefreshIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Stack>
      </Stack>

      {/* KPI row */}
      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', md: 'repeat(4, 1fr)' } }}>
        <Box>
          <KPICard title="مجموع درآمد" value={`${formatCurrency(overview.totalRevenue)} تومان`} />
        </Box>
        <Box>
          <KPICard title="تعداد سفارش‌ها" value={formatCurrency(overview.totalOrders)} />
        </Box>
        <Box>
          <KPICard title="پرداخت‌های موفق" value={formatCurrency(overview.completedPayments)} />
        </Box>
        <Box>
          <KPICard title="لغو/ناموفق/بازگشت" value={formatCurrency(overview.failedPayments + overview.refunds)} />
        </Box>
      </Box>

      {/* Charts row */}
      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, mt: 2 }}>
        <Box>
          <Card sx={{ height: 360 }}>
            <CardContent sx={{ height: '100%' }}>
              <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
                <Typography variant="subtitle1">روند درآمد ۳۰ روز گذشته</Typography>
                <Chip size="small" label="تومان" />
              </Stack>
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={revenueSeries} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8884d8" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value: string) => {
                      try {
                        const d = new Date(value);
                        return d.toLocaleDateString('fa-IR', { month: '2-digit', day: '2-digit' });
                      } catch {
                        return value;
                      }
                    }}
                  />
                  <YAxis tickFormatter={(v) => `${(v / 1_000_000).toFixed(0)}M`} />
                  <ReTooltip
                    formatter={(v: any) => `${formatCurrency(v as number)} تومان`}
                    labelFormatter={(label: any) => {
                      try {
                        const d = new Date(label);
                        return d.toLocaleDateString('fa-IR', { year: 'numeric', month: '2-digit', day: '2-digit' });
                      } catch {
                        return label;
                      }
                    }}
                  />
                  <Area type="monotone" dataKey="revenue" stroke="#8884d8" fillOpacity={1} fill="url(#colorRev)" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>

        <Box>
          <Card sx={{ height: 360 }}>
            <CardContent sx={{ height: '100%' }}>
              <Typography variant="subtitle1" mb={1}>سهم روش‌های پرداخت</Typography>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={methodDistribution} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                    {methodDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Recent payments table */}
      <Box sx={{ mt: 2 }}>
        <Card>
          <CardContent>
            <Typography variant="subtitle1" mb={1}>تراکنش‌های اخیر</Typography>
            <Divider />
            <Box mt={2}>
              {recentPaymentsQuery.data && recentPaymentsQuery.data.length > 0 ? (
                <Box sx={{ overflowX: 'auto' }}>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>شماره سفارش</th>
                        <th>بخش</th>
                        <th>مبلغ</th>
                        <th>وضعیت</th>
                        <th>روش</th>
                        <th>تاریخ</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentPaymentsQuery.data.map((p) => (
                        <tr key={p.id}>
                          <td>{p.orderNumber}</td>
                          <td>
                            {p.item_types && p.item_types.length > 0 ? (
                              <Stack direction="row" spacing={0.5} flexWrap="wrap">
                                {p.item_types.map((itemType, idx) => (
                                  <Chip 
                                    key={idx} 
                                    label={getSectionLabel(itemType)} 
                                    size="small" 
                                    color="primary" 
                                    variant="outlined"
                                  />
                                ))}
                              </Stack>
                            ) : (
                              <Typography variant="body2" color="text.secondary">-</Typography>
                            )}
                          </td>
                          <td>{formatCurrency(p.amount)} تومان</td>
                          <td>
                            <Chip size="small" color={p.status === 'completed' ? 'success' : p.status === 'failed' ? 'error' : 'default'} label={p.status} />
                          </td>
                          <td>{p.method}</td>
                          <td>{new Date(p.createdAt).toLocaleString('fa-IR')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">داده‌ای برای نمایش موجود نیست.</Typography>
              )}
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default AdminPayments;


