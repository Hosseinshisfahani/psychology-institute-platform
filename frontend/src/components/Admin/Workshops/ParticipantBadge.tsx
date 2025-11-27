import React from 'react';
import { Box, Chip, Typography } from '@mui/material';
import { People as PeopleIcon, CheckCircle as CheckIcon } from '@mui/icons-material';

interface ParticipantBadgeProps {
  currentParticipants: number;
  maxParticipants: number;
  registrationCount?: number;
  showRegistrationCount?: boolean;
  size?: 'small' | 'medium';
}

const ParticipantBadge: React.FC<ParticipantBadgeProps> = ({
  currentParticipants,
  maxParticipants,
  registrationCount,
  showRegistrationCount = false,
  size = 'small',
}) => {
  const isFull = currentParticipants >= maxParticipants;
  const availableSeats = maxParticipants - currentParticipants;
  const percentage = (currentParticipants / maxParticipants) * 100;

  const getColor = () => {
    if (isFull) return 'error';
    if (percentage >= 80) return 'warning';
    return 'success';
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Chip
        icon={<PeopleIcon />}
        label={`${currentParticipants}/${maxParticipants}`}
        color={getColor()}
        size={size}
        variant={isFull ? 'filled' : 'outlined'}
      />
      {showRegistrationCount && registrationCount !== undefined && (
        <Chip
          icon={<CheckIcon />}
          label={`${registrationCount} ثبت‌نام`}
          color="info"
          size={size}
          variant="outlined"
        />
      )}
      {!isFull && (
        <Typography variant="caption" color="text.secondary">
          {availableSeats} جای خالی
        </Typography>
      )}
    </Box>
  );
};

export default ParticipantBadge;
