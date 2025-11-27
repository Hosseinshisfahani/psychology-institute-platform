import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  ButtonGroup,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Publish as PublishIcon,
  Unpublished as UnpublishIcon,
  Archive as ArchiveIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';

interface BulkActionBarProps {
  selectedCount: number;
  onBulkAction: (action: string) => void;
  onClearSelection: () => void;
  disabled?: boolean;
}

const BulkActionBar: React.FC<BulkActionBarProps> = ({
  selectedCount,
  onBulkAction,
  onClearSelection,
  disabled = false,
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAction = (action: string) => {
    onBulkAction(action);
    handleMenuClose();
  };

  if (selectedCount === 0) {
    return null;
  }

  return (
    <Paper
      elevation={2}
      sx={{
        position: 'sticky',
        bottom: 0,
        zIndex: 1000,
        p: 2,
        backgroundColor: 'primary.main',
        color: 'white',
        borderRadius: 0,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body1" fontWeight={600}>
            {selectedCount} مورد انتخاب شده
          </Typography>
          <Chip
            label={selectedCount}
            size="small"
            sx={{
              backgroundColor: 'white',
              color: 'primary.main',
              fontWeight: 600,
            }}
          />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ButtonGroup variant="contained" size="small" sx={{ backgroundColor: 'white', color: 'primary.main' }}>
            <Button
              startIcon={<PublishIcon />}
              onClick={() => handleAction('publish')}
              disabled={disabled}
              sx={{
                backgroundColor: 'white',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'grey.100',
                },
              }}
            >
              انتشار
            </Button>
            <Button
              startIcon={<UnpublishIcon />}
              onClick={() => handleAction('unpublish')}
              disabled={disabled}
              sx={{
                backgroundColor: 'white',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'grey.100',
                },
              }}
            >
              پیش‌نویس
            </Button>
            <Button
              startIcon={<ArchiveIcon />}
              onClick={() => handleAction('archive')}
              disabled={disabled}
              sx={{
                backgroundColor: 'white',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'grey.100',
                },
              }}
            >
              بایگانی
            </Button>
          </ButtonGroup>

          <IconButton
            onClick={handleMenuClick}
            sx={{
              color: 'white',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
              },
            }}
          >
            <MoreVertIcon />
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
          >
            <MenuItem
              onClick={() => handleAction('delete')}
              sx={{ color: 'error.main' }}
            >
              <ListItemIcon>
                <DeleteIcon color="error" />
              </ListItemIcon>
              <ListItemText>حذف</ListItemText>
            </MenuItem>
          </Menu>

          <Button
            variant="outlined"
            onClick={onClearSelection}
            sx={{
              borderColor: 'white',
              color: 'white',
              '&:hover': {
                borderColor: 'white',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            لغو انتخاب
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default BulkActionBar;
