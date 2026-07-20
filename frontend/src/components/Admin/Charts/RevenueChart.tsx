import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Box,
  useTheme,
} from '@mui/material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface RevenueChartProps {
  data: Array<{
    month: string;
    revenue: number;
  }>;
}

const RevenueChart: React.FC<RevenueChartProps> = ({ data }) => {
  const theme = useTheme();

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('fa-IR').format(value);
  };

  return (
    <Card>
      <CardHeader title="روند درآمد" />
      <CardContent>
        <Box sx={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <AreaChart
              data={data}
              margin={{
                top: 10,
                right: 10,
                left: 10,
                bottom: 0,
              }}
            >
              <defs>
                <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="5%"
                    stopColor={theme.palette.primary.main}
                    stopOpacity={0.8}
                  />
                  <stop
                    offset="95%"
                    stopColor={theme.palette.primary.main}
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
              <XAxis
                dataKey="month"
                stroke={theme.palette.text.secondary}
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke={theme.palette.text.secondary}
                style={{ fontSize: '12px' }}
                tickFormatter={formatCurrency}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: '8px',
                }}
                formatter={(value: number | undefined) => [formatCurrency(value ?? 0) + ' تومان', 'درآمد']}
                labelStyle={{ color: theme.palette.text.primary }}
              />
              <Area
                type="monotone"
                dataKey="revenue"
                stroke={theme.palette.primary.main}
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorRevenue)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RevenueChart;

