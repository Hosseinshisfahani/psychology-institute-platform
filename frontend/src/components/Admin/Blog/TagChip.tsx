import React from 'react';
import { Chip } from '@mui/material';

interface TagChipProps {
  name: string;
  size?: 'small' | 'medium';
  onDelete?: () => void;
  clickable?: boolean;
  onClick?: () => void;
  variant?: 'filled' | 'outlined';
}

const TagChip: React.FC<TagChipProps> = ({
  name,
  size = 'small',
  onDelete,
  clickable = false,
  onClick,
  variant = 'outlined',
}) => {
  return (
    <Chip
      label={name}
      size={size}
      variant={variant}
      clickable={clickable}
      onClick={clickable ? onClick : undefined}
      onDelete={onDelete}
      sx={{
        fontWeight: 500,
        fontSize: '0.75rem',
        '& .MuiChip-label': {
          px: 1,
        },
        '&:hover': clickable ? {
          backgroundColor: 'primary.main',
          color: 'white',
        } : {},
      }}
    />
  );
};

export default TagChip;
