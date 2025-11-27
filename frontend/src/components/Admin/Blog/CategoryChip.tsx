import React from 'react';
import { Chip } from '@mui/material';

interface CategoryChipProps {
  name: string;
  color?: string;
  size?: 'small' | 'medium';
  onDelete?: () => void;
  clickable?: boolean;
  onClick?: () => void;
}

const CategoryChip: React.FC<CategoryChipProps> = ({
  name,
  color = '#007bff',
  size = 'small',
  onDelete,
  clickable = false,
  onClick,
}) => {
  return (
    <Chip
      label={name}
      size={size}
      clickable={clickable}
      onClick={clickable ? onClick : undefined}
      onDelete={onDelete}
      sx={{
        backgroundColor: color,
        color: 'white',
        fontWeight: 500,
        fontSize: '0.75rem',
        '& .MuiChip-label': {
          px: 1,
        },
        '&:hover': clickable ? {
          backgroundColor: color,
          opacity: 0.8,
        } : {},
      }}
    />
  );
};

export default CategoryChip;
