import React from 'react';
import { Chip } from '@mui/material';
import { workshopUtils } from '../../../services/workshopAdminApi';

interface WorkshopStatusBadgeProps {
  status: string;
  size?: 'small' | 'medium';
  variant?: 'filled' | 'outlined';
}

const WorkshopStatusBadge: React.FC<WorkshopStatusBadgeProps> = ({
  status,
  size = 'small',
  variant = 'filled',
}) => {
  const getStatusColor = (status: string) => {
    const colors: Record<string, any> = {
      draft: 'warning',
      published: 'success',
      registration_open: 'info',
      in_progress: 'secondary',
      completed: 'success',
      cancelled: 'error',
      archived: 'default',
    };
    return colors[status] || 'default';
  };

  return (
    <Chip
      label={workshopUtils.getStatusLabel(status)}
      color={getStatusColor(status)}
      size={size}
      variant={variant}
    />
  );
};

export default WorkshopStatusBadge;
