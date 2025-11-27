import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Tooltip,
  Skeleton,
  Alert,
  Stack,
} from '@mui/material';
import {
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  PlayArrow as PlayIcon,
  OpenInNew as OpenIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { workshopSessionApi, WorkshopSession, SessionFilters } from '../../../services/workshopAdminApi';

interface WorkshopSessionsProps {
  workshopId: number;
  workshopTitle?: string;
  onEditSession: (workshopId: number, session: WorkshopSession) => void;
}

const WorkshopSessions: React.FC<WorkshopSessionsProps> = ({
  workshopId,
  workshopTitle,
  onEditSession,
}) => {
  const [filters, setFilters] = useState<SessionFilters>({});

  // Fetch sessions
  const { data: sessionsData, isLoading, error } = useQuery({
    queryKey: ['admin-workshop-sessions', workshopId, filters],
    queryFn: () => workshopSessionApi.getSessions(workshopId, filters),
  });



  const getStatusColor = (session: WorkshopSession) => {
    if (session.is_completed) return 'success';
    const sessionDate = new Date(session.scheduled_datetime);
    const now = new Date();
    if (sessionDate < now) return 'error';
    return 'info';
  };

  const getStatusLabel = (session: WorkshopSession) => {
    if (session.is_completed) return 'تکمیل شده';
    const sessionDate = new Date(session.scheduled_datetime);
    const now = new Date();
    if (sessionDate < now) return 'گذشته';
    return 'آینده';
  };

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        خطا در بارگذاری جلسات
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          جلسات کارگاه {workshopTitle}
        </Typography>
      </Box>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>شماره</TableCell>
              <TableCell>عنوان</TableCell>
              <TableCell>تاریخ و زمان</TableCell>
              <TableCell>مدت زمان</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>ویدیو جلسه</TableCell>
              <TableCell>لینک سی‌روم</TableCell>
              <TableCell>شرکت‌کنندگان</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 3 }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Skeleton variant="text" width={30} />
                  </TableCell>
                  <TableCell>
                    <Skeleton variant="text" width="80%" />
                  </TableCell>
                  <TableCell>
                    <Skeleton variant="text" width={120} />
                  </TableCell>
                  <TableCell>
                    <Skeleton variant="text" width={60} />
                  </TableCell>
                  <TableCell>
                    <Skeleton variant="rectangular" width={80} height={24} />
                  </TableCell>
                  <TableCell>
                    <Skeleton variant="text" width={40} />
                  </TableCell>
                  <TableCell>
                    <Skeleton variant="text" width={40} />
                  </TableCell>
                  <TableCell>
                    <Skeleton variant="text" width={40} />
                  </TableCell>
                </TableRow>
              ))
            ) : sessionsData?.results?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    هیچ جلسه‌ای یافت نشد
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              sessionsData?.results?.map((session: WorkshopSession) => (
                <TableRow key={session.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>
                      {session.session_number}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight={500}>
                        {session.title}
                      </Typography>
                      {session.description && (
                        <Typography variant="caption" color="text.secondary">
                          {session.description.substring(0, 50)}...
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <ScheduleIcon fontSize="small" color="action" />
                      <Typography variant="body2">
                        {session.scheduled_datetime_persian}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {session.duration_display}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(session)}
                      color={getStatusColor(session)}
                      size="small"
                      icon={session.is_completed ? <CheckCircleIcon /> : undefined}
                    />
                  </TableCell>
                  <TableCell>
                    {session.session_video ? (
                      <Tooltip title="ویدیو جلسه موجود است">
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<PlayIcon />}
                          onClick={() => window.open(session.session_video, '_blank')}
                        >
                          مشاهده
                        </Button>
                      </Tooltip>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {session.croom_platform_link ? (
                      <Tooltip title="لینک پلتفرم سی‌روم">
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<OpenIcon />}
                          onClick={() => window.open(session.croom_platform_link, '_blank')}
                        >
                          سی‌روم
                        </Button>
                      </Tooltip>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Typography variant="body2">
                        {session.attendance_count || 0}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {sessionsData?.results?.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            مجموع {sessionsData.results.length} جلسه
          </Typography>
          <Stack direction="row" spacing={1}>
            <Chip
              label={`${sessionsData.results.filter((s: WorkshopSession) => s.is_completed).length} تکمیل شده`}
              color="success"
              size="small"
            />
            <Chip
              label={`${sessionsData.results.filter((s: WorkshopSession) => s.session_video).length} دارای ویدیو`}
              color="info"
              size="small"
            />
          </Stack>
        </Box>
      )}
    </Box>
  );
};

export default WorkshopSessions;
