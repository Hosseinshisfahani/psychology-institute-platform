import React from 'react';
import { Box, Card, CardHeader, CardContent, List, ListItem, ListItemText, Chip, Typography, Button, Stack } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import {
  People as PeopleIcon,
  School as SchoolIcon,
  AttachMoney as MoneyIcon,
  Event as EventIcon,
  Add as AddIcon,
  TrendingUp,
} from '@mui/icons-material';
import StatCard from '../../../components/Admin/Charts/StatCard';
import RevenueChart from '../../../components/Admin/Charts/RevenueChart';
import UserGrowthChart from '../../../components/Admin/Charts/UserGrowthChart';

interface DashboardStats {
  total_users: number;
  total_courses: number;
  total_sessions: number;
  total_revenue: number;
  active_users: number;
  pending_sessions: number;
  new_users_this_month: number;
  completed_sessions: number;
  average_session_rating: number;
  monthly_revenue: number;
}

interface Activity {
  id: number;
  type: string;
  description: string;
  user_name: string;
  created_at: string;
}

const DashboardOverview: React.FC = () => {
  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['admin-dashboard-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/dashboard/stats/');
      return response.data;
    },
  });

  // Fetch recent activities
  const { data: activities = [] } = useQuery<Activity[]>({
    queryKey: ['admin-activities'],
    queryFn: async () => {
      const response = await axios.get('/api/admin/activities/');
      return response.data.slice(0, 10);
    },
  });

  // Mock data for charts - in real app, fetch from API
  const revenueData = [
    { month: 'فروردین', revenue: 4000000 },
    { month: 'اردیبهشت', revenue: 3000000 },
    { month: 'خرداد', revenue: 5000000 },
    { month: 'تیر', revenue: 4500000 },
    { month: 'مرداد', revenue: 6000000 },
    { month: 'شهریور', revenue: stats?.monthly_revenue || 5500000 },
  ];

  const userGrowthData = [
    { month: 'فروردین', count: 45 },
    { month: 'اردیبهشت', count: 52 },
    { month: 'خرداد', count: 61 },
    { month: 'تیر', count: 58 },
    { month: 'مرداد', count: 70 },
    { month: 'شهریور', count: stats?.new_users_this_month || 65 },
  ];

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('fa-IR').format(num);
  };

  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat('fa-IR').format(num);
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            داشبورد مدیریت
          </Typography>
          <Typography variant="body1" color="text.secondary">
            خوش آمدید به پنل مدیریت سیستم
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} size="large">
          افزودن محتوا
        </Button>
      </Box>

      {/* Stats Cards */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }, gap: 3, mb: 3 }}>
        <StatCard
          title="کل کاربران"
          value={formatNumber(stats?.total_users || 0)}
          icon={<PeopleIcon />}
          color="primary"
          trend={{ value: 12.5, isPositive: true }}
          subtitle={`${formatNumber(stats?.active_users || 0)} فعال`}
        />
        <StatCard
          title="کل بسته‌های آموزشی"
          value={formatNumber(stats?.total_courses || 0)}
          icon={<SchoolIcon />}
          color="success"
        />
        <StatCard
          title="کل نوبت‌ها"
          value={formatNumber(stats?.total_sessions || 0)}
          icon={<EventIcon />}
          color="warning"
          subtitle={`${formatNumber(stats?.pending_sessions || 0)} در انتظار`}
        />
        <StatCard
          title="کل درآمد"
          value={formatCurrency(stats?.total_revenue || 0)}
          icon={<MoneyIcon />}
          color="info"
          trend={{ value: 8.2, isPositive: true }}
          subtitle="تومان"
        />
      </Box>

      {/* Charts */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' }, gap: 3, mb: 3 }}>
        <RevenueChart data={revenueData} />
        <UserGrowthChart data={userGrowthData} />
      </Box>

      {/* Recent Activities and Quick Stats */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3 }}>
          <Card>
            <CardHeader title="فعالیت‌های اخیر" />
            <CardContent>
              <List>
                {activities.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 3 }}>
                    هیچ فعالیتی یافت نشد
                  </Typography>
                ) : (
                  activities.map((activity) => (
                    <ListItem
                      key={activity.id}
                      sx={{
                        borderRadius: 1,
                        mb: 1,
                        '&:hover': {
                          bgcolor: 'action.hover',
                        },
                      }}
                    >
                      <ListItemText
                        primary={activity.description}
                        secondary={`${activity.user_name} • ${activity.created_at}`}
                      />
                      <Chip
                        label={activity.type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </ListItem>
                  ))
                )}
              </List>
            </CardContent>
          </Card>

          <Card>
            <CardHeader title="آمار سریع" />
            <CardContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'success.lighter',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Typography variant="body2" fontWeight={600}>
                    کاربران جدید این ماه
                  </Typography>
                  <Typography variant="h6" fontWeight={700} color="success.main">
                    {formatNumber(stats?.new_users_this_month || 0)}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'warning.lighter',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Typography variant="body2" fontWeight={600}>
                    نوبت‌های تکمیل شده
                  </Typography>
                  <Typography variant="h6" fontWeight={700} color="warning.main">
                    {formatNumber(stats?.completed_sessions || 0)}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'info.lighter',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Typography variant="body2" fontWeight={600}>
                    میانگین رضایت
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Typography variant="h6" fontWeight={700} color="info.main">
                      {stats?.average_session_rating || 0}
                    </Typography>
                    <TrendingUp sx={{ color: 'info.main' }} />
                  </Box>
                </Box>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'primary.lighter',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Typography variant="body2" fontWeight={600}>
                    درآمد این ماه
                  </Typography>
                  <Typography variant="h6" fontWeight={700} color="primary.main">
                    {formatCurrency(stats?.monthly_revenue || 0)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
      </Box>
    </Box>
  );
};

export default DashboardOverview;

