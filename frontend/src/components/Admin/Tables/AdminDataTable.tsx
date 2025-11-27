import React from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Checkbox,
  IconButton,
  Toolbar,
  Typography,
  Tooltip,
  Box,
  alpha,
  CircularProgress,
  TableSortLabel,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  FilterList as FilterListIcon,
  FileDownload as FileDownloadIcon,
} from '@mui/icons-material';

export interface Column {
  id: string;
  label: string;
  minWidth?: number;
  align?: 'right' | 'left' | 'center';
  format?: (value: any, row: any) => React.ReactNode;
  sortable?: boolean;
}

interface AdminDataTableProps {
  columns: Column[];
  rows: any[];
  loading?: boolean;
  page: number;
  rowsPerPage: number;
  totalCount: number;
  onPageChange: (newPage: number) => void;
  onRowsPerPageChange: (newRowsPerPage: number) => void;
  onSelectionChange?: (selected: any[]) => void;
  onDelete?: (selected: any[]) => void;
  onExport?: () => void;
  selectable?: boolean;
  title?: string;
  onSort?: (field: string, direction: 'asc' | 'desc') => void;
  sortField?: string;
  sortDirection?: 'asc' | 'desc';
}

const AdminDataTable: React.FC<AdminDataTableProps> = ({
  columns,
  rows,
  loading = false,
  page,
  rowsPerPage,
  totalCount,
  onPageChange,
  onRowsPerPageChange,
  onSelectionChange,
  onDelete,
  onExport,
  selectable = true,
  title,
  onSort,
  sortField,
  sortDirection = 'asc',
}) => {
  const [selected, setSelected] = React.useState<any[]>([]);

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelected(rows);
      onSelectionChange?.(rows);
    } else {
      setSelected([]);
      onSelectionChange?.([]);
    }
  };

  const handleClick = (row: any) => {
    const selectedIndex = selected.findIndex((item) => item.id === row.id);
    let newSelected: any[] = [];

    if (selectedIndex === -1) {
      newSelected = [...selected, row];
    } else {
      newSelected = selected.filter((item) => item.id !== row.id);
    }

    setSelected(newSelected);
    onSelectionChange?.(newSelected);
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    onPageChange(newPage);
    setSelected([]);
    onSelectionChange?.([]);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    onRowsPerPageChange(parseInt(event.target.value, 10));
    onPageChange(0);
    setSelected([]);
    onSelectionChange?.([]);
  };

  const handleDelete = () => {
    onDelete?.(selected);
    setSelected([]);
    onSelectionChange?.([]);
  };

  const handleSortClick = (columnId: string) => {
    if (!onSort) return;
    
    const isAsc = sortField === columnId && sortDirection === 'asc';
    onSort(columnId, isAsc ? 'desc' : 'asc');
  };

  const isSelected = (row: any) => selected.findIndex((item) => item.id === row.id) !== -1;

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {(selected.length > 0 || title) && (
        <Toolbar
          sx={{
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 },
            ...(selected.length > 0 && {
              bgcolor: (theme) =>
                alpha(theme.palette.primary.main, theme.palette.action.activatedOpacity),
            }),
          }}
        >
          {selected.length > 0 ? (
            <Typography
              sx={{ flex: '1 1 100%' }}
              color="inherit"
              variant="subtitle1"
              component="div"
            >
              {selected.length} مورد انتخاب شده
            </Typography>
          ) : (
            title && (
              <Typography
                sx={{ flex: '1 1 100%' }}
                variant="h6"
                id="tableTitle"
                component="div"
              >
                {title}
              </Typography>
            )
          )}

          {selected.length > 0 ? (
            <Tooltip title="حذف">
              <IconButton onClick={handleDelete}>
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {onExport && (
                <Tooltip title="خروجی Excel">
                  <IconButton onClick={onExport}>
                    <FileDownloadIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          )}
        </Toolbar>
      )}

      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader aria-label="admin data table" role="table">
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    id="select-all-checkbox"
                    color="primary"
                    indeterminate={selected.length > 0 && selected.length < rows.length}
                    checked={rows.length > 0 && selected.length === rows.length}
                    onChange={handleSelectAllClick}
                    inputProps={{ 'aria-label': 'انتخاب همه' }}
                  />
                </TableCell>
              )}
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'right'}
                  style={{ minWidth: column.minWidth }}
                >
                  {column.sortable && onSort ? (
                    <TableSortLabel
                      active={sortField === column.id}
                      direction={sortField === column.id ? sortDirection : 'asc'}
                      onClick={() => handleSortClick(column.id)}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={columns.length + (selectable ? 1 : 0)} align="center">
                  <Box sx={{ py: 4 }}>
                    <CircularProgress />
                  </Box>
                </TableCell>
              </TableRow>
            ) : rows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length + (selectable ? 1 : 0)} align="center">
                  <Box sx={{ py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      هیچ داده‌ای یافت نشد
                    </Typography>
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              rows.map((row) => {
                const isItemSelected = isSelected(row);
                return (
                  <TableRow
                    hover
                    role="checkbox"
                    aria-checked={isItemSelected}
                    tabIndex={-1}
                    key={row.id}
                    selected={isItemSelected}
                    sx={{ cursor: selectable ? 'pointer' : 'default' }}
                    aria-label={`ردیف ${row.full_name || row.email || row.id}`}
                  >
                    {selectable && (
                      <TableCell padding="checkbox">
                        <Checkbox
                          id={`row-checkbox-${row.id}`}
                          color="primary"
                          checked={isItemSelected}
                          onChange={() => handleClick(row)}
                          inputProps={{ 'aria-label': `انتخاب ${row.full_name || row.email || row.id}` }}
                        />
                      </TableCell>
                    )}
                    {columns.map((column) => {
                      const value = row[column.id];
                      return (
                        <TableCell key={column.id} align={column.align || 'right'}>
                          {column.format ? column.format(value, row) : value}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 20, 50, 100]}
        component="div"
        count={totalCount}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="تعداد در صفحه:"
        labelDisplayedRows={({ from, to, count }) =>
          `${from}–${to} از ${count !== -1 ? count : `بیشتر از ${to}`}`
        }
        getItemAriaLabel={(type) => {
          if (type === 'first') return 'صفحه اول';
          if (type === 'last') return 'صفحه آخر';
          if (type === 'next') return 'صفحه بعدی';
          if (type === 'previous') return 'صفحه قبلی';
          return '';
        }}
      />
    </Paper>
  );
};

export default AdminDataTable;

