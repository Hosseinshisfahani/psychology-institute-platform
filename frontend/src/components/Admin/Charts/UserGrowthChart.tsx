import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Box,
  useTheme,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface UserGrowthChartProps {
  data: Array<{
    month: string;
    count: number;
  }>;
}

const UserGrowthChart: React.FC<UserGrowthChartProps> = ({ data }) => {
  const theme = useTheme();

  const colors = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main,
    theme.palette.info.main,
  ];

  return (
    <Card>
      <CardHeader title="رشد کاربران" />
      <CardContent>
        <Box sx={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <BarChart
              data={data}
              margin={{
                top: 10,
                right: 10,
                left: 10,
                bottom: 0,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
              <XAxis
                dataKey="month"
                stroke={theme.palette.text.secondary}
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke={theme.palette.text.secondary}
                style={{ fontSize: '12px' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: theme.palette.background.paper,
                  border: `1px solid ${theme.palette.divider}`,
                  borderRadius: '8px',
                }}
                formatter={(value: number) => [value + ' کاربر', 'تعداد']}
                labelStyle={{ color: theme.palette.text.primary }}
              />
              <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                {data.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
};

export default UserGrowthChart;

