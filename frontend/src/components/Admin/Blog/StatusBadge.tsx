import React from 'react';
import { Chip } from '@mui/material';
import { blogUtils } from '../../../services/blogAdminApi';

interface StatusBadgeProps {
  status: 'draft' | 'published' | 'archived';
  size?: 'small' | 'medium';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'small' }) => {
  const color = blogUtils.getStatusColor(status);
  const label = blogUtils.getStatusLabel(status);

  return (
    <Chip
      label={label}
      size={size}
      sx={{
        backgroundColor: color,
        color: 'white',
        fontWeight: 600,
        fontSize: '0.75rem',
        '& .MuiChip-label': {
          px: 1,
        },
      }}
    />
  );
};

export default StatusBadge;
