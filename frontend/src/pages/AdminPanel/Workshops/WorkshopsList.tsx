import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  IconButton,
  Chip,
  Avatar,
  Tooltip,
  Skeleton,
  Alert,
  Pagination,
  Stack,
  Collapse,
  TablePagination,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  MoreVert as MoreVertIcon,
  People as PeopleIcon,
  Schedule as ScheduleIcon,
  AttachMoney as MoneyIcon,
  VideoCall as VideoCallIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { 
  workshopApi, 
  workshopCategoryApi, 
  Workshop, 
  WorkshopFilters as WorkshopFiltersType,
  workshopUtils 
} from '../../../services/workshopAdminApi';
import { 
  WorkshopStatusBadge, 
  ParticipantBadge, 
  WorkshopFilters,
  SessionFormDialog 
} from '../../../components/Admin/Workshops';
import WorkshopSessions from './WorkshopSessions';
import WorkshopReviewsModeration from './WorkshopReviewsModeration';
import { Tabs, Tab } from '@mui/material';

const WorkshopsList: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  
  const [selectedWorkshops, setSelectedWorkshops] = useState<number[]>([]);
  const [filters, setFilters] = useState<WorkshopFiltersType>({});
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [anchorEl, setAnchorEl] = useState<{ [key: number]: HTMLElement | null }>({});
  const [sessionDialog, setSessionDialog] = useState<{
    open: boolean;
    workshopId?: number;
    session?: any;
  }>({ open: false });
  const [activeTab, setActiveTab] = useState(0);

  // Fetch workshops
  const { data: workshopsData, isLoading, error } = useQuery({
    queryKey: ['admin-workshops', filters, page, rowsPerPage],
    queryFn: () => workshopApi.getWorkshops({ 
      ...filters, 
      page: page + 1, 
      page_size: rowsPerPage 
    }),
  });

  // Fetch categories for filters
  const { data: categories = [] } = useQuery({
    queryKey: ['admin-workshop-categories'],
    queryFn: () => workshopCategoryApi.getCategories(),
  });

  // Bulk action mutation
  const bulkActionMutation = useMutation({
    mutationFn: ({ action, workshopIds }: { action: string; workshopIds: number[] }) =>
      workshopApi.bulkAction(action, workshopIds),
    onSuccess: (data) => {
      enqueueSnackbar(data.message, { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-workshops'] });
      setSelectedWorkshops([]);
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در انجام عملیات', { variant: 'error' });
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => workshopApi.deleteWorkshop(id),
    onSuccess: () => {
      enqueueSnackbar('کارگاه با موفقیت حذف شد', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['admin-workshops'] });
    },
    onError: (error: any) => {
      enqueueSnackbar(error.response?.data?.error || 'خطا در حذف کارگاه', { variant: 'error' });
    },
  });

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedWorkshops(workshopsData?.results?.map((workshop: Workshop) => workshop.id!) || []);
    } else {
      setSelectedWorkshops([]);
    }
  };

  const handleSelectWorkshop = (workshopId: number, checked: boolean) => {
    if (checked) {
      setSelectedWorkshops(prev => [...prev, workshopId]);
    } else {
      setSelectedWorkshops(prev => prev.filter(id => id !== workshopId));
    }
  };

  const handleBulkAction = (action: string) => {
    if (selectedWorkshops.length === 0) return;
    bulkActionMutation.mutate({ action, workshopIds: selectedWorkshops });
  };

  const handleDelete = (workshopId: number) => {
    if (window.confirm('آیا از حذف این کارگاه اطمینان دارید؟')) {
      deleteMutation.mutate(workshopId);
    }
  };

  const handleFiltersChange = (newFilters: WorkshopFiltersType) => {
    setFilters(newFilters);
    setPage(0);
  };

  const handleClearFilters = () => {
    setFilters({});
    setPage(0);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const toggleRowExpansion = (workshopId: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(workshopId)) {
      newExpanded.delete(workshopId);
    } else {
      newExpanded.add(workshopId);
    }
    setExpandedRows(newExpanded);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, workshopId: number) => {
    setAnchorEl(prev => ({ ...prev, [workshopId]: event.currentTarget }));
  };

  const handleMenuClose = (workshopId: number) => {
    setAnchorEl(prev => ({ ...prev, [workshopId]: null }));
  };

  const handleViewParticipants = (workshopId: number) => {
    // Navigate to participants view
    navigate(`/admin-panel/workshops/${workshopId}/participants`);
  };

  const handleAddSession = (workshopId: number) => {
    setSessionDialog({ open: true, workshopId });
  };

  const handleEditSession = (workshopId: number, session: any) => {
    setSessionDialog({ open: true, workshopId, session });
  };

  const handleSessionSave = (sessionData: any) => {
    // This will be handled by the WorkshopSessions component
    setSessionDialog({ open: false });
  };

  // Get unique instructors from workshops
  const instructors = React.useMemo(() => {
    const instructorMap = new Map();
    workshopsData?.results?.forEach((workshop: Workshop) => {
      if (workshop.instructor_name && workshop.instructor_email) {
        instructorMap.set(workshop.instructor, {
          id: workshop.instructor,
          name: workshop.instructor_name,
          email: workshop.instructor_email,
        });
      }
    });
    return Array.from(instructorMap.values());
  }, [workshopsData?.results]);

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        خطا در بارگذاری کارگاه‌ها
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          مدیریت کارگاه‌ها
        </Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="لیست کارگاه‌ها" />
          <Tab label="مدیریت نظرات" />
        </Tabs>
      </Box>

      {activeTab === 1 && <WorkshopReviewsModeration />}
      {activeTab === 0 && (
        <>
      {/* Filters */}
      <WorkshopFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onClear={handleClearFilters}
        categories={Array.isArray(categories) ? categories : []}
        instructors={Array.isArray(instructors) ? instructors : []}
      />

      {/* Workshops Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedWorkshops.length === workshopsData?.results?.length && workshopsData?.results?.length > 0}
                      indeterminate={selectedWorkshops.length > 0 && selectedWorkshops.length < (workshopsData?.results?.length || 0)}
                      onChange={(e) => handleSelectAll(e.target.checked)}
                    />
                  </TableCell>
                  <TableCell>عنوان</TableCell>
                  <TableCell>دسته‌بندی</TableCell>
                  <TableCell>مدرس</TableCell>
                  <TableCell>وضعیت</TableCell>
                  <TableCell>تاریخ‌ها</TableCell>
                  <TableCell>شرکت‌کنندگان</TableCell>
                  <TableCell>قیمت</TableCell>
                  <TableCell>عملیات</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, index) => (
                    <TableRow key={index}>
                      <TableCell padding="checkbox">
                        <Skeleton variant="rectangular" width={20} height={20} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width="80%" />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width={80} height={24} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width="60%" />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width={80} height={24} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width={100} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width={60} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width={80} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="text" width={40} />
                      </TableCell>
                      <TableCell>
                        <Skeleton variant="rectangular" width={120} height={32} />
                      </TableCell>
                    </TableRow>
                  ))
                ) : workshopsData?.results?.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        هیچ کارگاهی یافت نشد
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  workshopsData?.results?.map((workshop: Workshop) => (
                    <React.Fragment key={workshop.id}>
                      <TableRow hover>
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedWorkshops.includes(workshop.id!)}
                            onChange={(e) => handleSelectWorkshop(workshop.id!, e.target.checked)}
                          />
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight={600} noWrap>
                              {workshop.title}
                            </Typography>
                            {workshop.short_description && (
                              <Typography variant="caption" color="text.secondary" noWrap>
                                {workshop.short_description.substring(0, 50)}...
                              </Typography>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={workshop.category_name || 'بدون دسته‌بندی'}
                            size="small"
                            sx={{ 
                              backgroundColor: workshop.category_color || '#e0e0e0',
                              color: 'white'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                              {workshop.instructor_name?.charAt(0)}
                            </Avatar>
                            <Typography variant="body2">
                              {workshop.instructor_name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <WorkshopStatusBadge status={workshop.status} />
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontSize="0.75rem">
                              شروع: {workshop.start_date_persian}
                            </Typography>
                            <Typography variant="body2" fontSize="0.75rem">
                              پایان: {workshop.end_date_persian}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <ParticipantBadge
                            currentParticipants={workshop.current_participants}
                            maxParticipants={workshop.max_participants}
                            registrationCount={workshop.registration_count}
                            showRegistrationCount
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <MoneyIcon fontSize="small" color="action" />
                            <Typography variant="body2">
                              {workshop.current_price_persian || workshopUtils.formatPrice(workshop.current_price)}
                            </Typography>
                          </Box>
                          {workshop.discount_percentage > 0 && (
                            <Chip
                              label={`${workshop.discount_percentage}% تخفیف`}
                              size="small"
                              color="error"
                              variant="outlined"
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                              <Tooltip title="مشاهده جلسات">
                                <IconButton
                                  size="small"
                                  onClick={() => toggleRowExpansion(workshop.id!)}
                                >
                                  {expandedRows.has(workshop.id!) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="مشاهده شرکت‌کنندگان">
                                <IconButton
                                  size="small"
                                  onClick={() => handleViewParticipants(workshop.id!)}
                                >
                                  <PeopleIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <IconButton
                                size="small"
                                onClick={(e) => handleMenuOpen(e, workshop.id!)}
                              >
                                <MoreVertIcon fontSize="small" />
                              </IconButton>
                              <Menu
                                anchorEl={anchorEl[workshop.id!]}
                                open={Boolean(anchorEl[workshop.id!])}
                                onClose={() => handleMenuClose(workshop.id!)}
                              >
                                <MenuItem onClick={() => handleDelete(workshop.id!)}>
                                  <ListItemIcon>
                                    <DeleteIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText>حذف</ListItemText>
                                </MenuItem>
                              </Menu>
                            </Box>
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={() => {
                                const apiUrl = process.env.REACT_APP_API_URL || 'https://sarmadclinic.ir';
                                window.open(`${apiUrl}/admin/workshops/workshop/${workshop.id}/change/`, '_blank');
                              }}
                              sx={{ alignSelf: 'flex-start' }}
                            >
                              ویرایش
                            </Button>
                          </Box>
                        </TableCell>
                      </TableRow>
                      
                      {/* Expanded Row for Sessions */}
                      <TableRow>
                        <TableCell colSpan={9} sx={{ py: 0 }}>
                          <Collapse in={expandedRows.has(workshop.id!)} timeout="auto" unmountOnExit>
                            <Box sx={{ p: 2, backgroundColor: 'grey.50' }}>
                              <WorkshopSessions
                                workshopId={workshop.id!}
                                workshopTitle={workshop.title}
                                onEditSession={handleEditSession}
                              />
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Pagination */}
      {workshopsData?.total_pages && workshopsData.total_pages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={workshopsData.total_pages}
            page={page + 1}
            onChange={(event, value) => setPage(value - 1)}
            color="primary"
          />
        </Box>
      )}

      {/* Bulk Actions */}
      {selectedWorkshops.length > 0 && (
        <Box sx={{ position: 'fixed', bottom: 20, left: '50%', transform: 'translateX(-50%)' }}>
          <Card sx={{ p: 2 }}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Typography variant="body2">
                {selectedWorkshops.length} کارگاه انتخاب شده
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={() => handleBulkAction('publish')}
                disabled={bulkActionMutation.isPending}
              >
                انتشار
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => handleBulkAction('archive')}
                disabled={bulkActionMutation.isPending}
              >
                بایگانی
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => handleBulkAction('open_registration')}
                disabled={bulkActionMutation.isPending}
              >
                باز کردن ثبت‌نام
              </Button>
              <Button
                variant="outlined"
                size="small"
                color="error"
                onClick={() => handleBulkAction('delete')}
                disabled={bulkActionMutation.isPending}
              >
                حذف
              </Button>
              <Button
                variant="text"
                size="small"
                onClick={() => setSelectedWorkshops([])}
              >
                انصراف
              </Button>
            </Stack>
          </Card>
        </Box>
      )}
        </>
      )}

      {/* Session Form Dialog */}
      {activeTab === 0 && (
        <SessionFormDialog
          open={sessionDialog.open}
          onClose={() => setSessionDialog({ open: false })}
          onSave={handleSessionSave}
          session={sessionDialog.session}
          workshopTitle={workshopsData?.results?.find((w: Workshop) => w.id === sessionDialog.workshopId)?.title}
          nextSessionNumber={1} // This should be calculated based on existing sessions
        />
      )}
    </Box>
  );
};

export default WorkshopsList;
