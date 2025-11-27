import React from 'react';
import { Card, CardContent, Typography, Box, Avatar, useTheme, alpha } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  trend?: {
    value: number;
    isPositive: boolean;
  };
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  color = 'primary',
  trend,
  subtitle,
}) => {
  const theme = useTheme();
  const bgColor = alpha(theme.palette[color].main, 0.1);
  const iconColor = theme.palette[color].main;

  return (
    <Card
      sx={{
        height: '100%',
        transition: 'all 0.3s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="body2"
              color="text.secondary"
              gutterBottom
              sx={{ fontWeight: 500 }}
            >
              {title}
            </Typography>
            <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {trend.isPositive ? (
                  <TrendingUp sx={{ fontSize: 20, color: 'success.main', ml: 0.5 }} />
                ) : (
                  <TrendingDown sx={{ fontSize: 20, color: 'error.main', ml: 0.5 }} />
                )}
                <Typography
                  variant="body2"
                  sx={{
                    color: trend.isPositive ? 'success.main' : 'error.main',
                    fontWeight: 600,
                  }}
                >
                  {trend.value}%
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                  نسبت به ماه قبل
                </Typography>
              </Box>
            )}
          </Box>
          <Avatar
            sx={{
              bgcolor: bgColor,
              color: iconColor,
              width: 56,
              height: 56,
            }}
          >
            {icon}
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );
};

export default StatCard;

