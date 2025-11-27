import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { faIR } from 'date-fns/locale';
import { WorkshopSession } from '../../../services/workshopAdminApi';

interface SessionFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (sessionData: Partial<WorkshopSession>) => void;
  session?: WorkshopSession | null;
  workshopTitle?: string;
  nextSessionNumber?: number;
  loading?: boolean;
}

const SessionFormDialog: React.FC<SessionFormDialogProps> = ({
  open,
  onClose,
  onSave,
  session,
  workshopTitle,
  nextSessionNumber = 1,
  loading = false,
}) => {
  const [formData, setFormData] = useState<Partial<WorkshopSession>>({
    session_number: nextSessionNumber,
    title: '',
    description: '',
    scheduled_datetime: '',
    duration_minutes: 120,
    materials: '',
    homework: '',
    session_video: '',
    croom_platform_link: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (session) {
      setFormData({
        session_number: session.session_number,
        title: session.title,
        description: session.description || '',
        scheduled_datetime: session.scheduled_datetime,
        duration_minutes: session.duration_minutes,
        materials: session.materials || '',
        homework: session.homework || '',
        session_video: session.session_video || '',
        croom_platform_link: session.croom_platform_link || '',
      });
    } else {
      setFormData({
        session_number: nextSessionNumber,
        title: '',
        description: '',
        scheduled_datetime: '',
        duration_minutes: 120,
        materials: '',
        homework: '',
        session_video: '',
        croom_platform_link: '',
      });
    }
    setErrors({});
  }, [session, nextSessionNumber, open]);

  const handleChange = (field: keyof WorkshopSession, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title?.trim()) {
      newErrors.title = 'عنوان جلسه الزامی است';
    }

    if (!formData.scheduled_datetime) {
      newErrors.scheduled_datetime = 'تاریخ و زمان جلسه الزامی است';
    }

    if (!formData.duration_minutes || formData.duration_minutes <= 0) {
      newErrors.duration_minutes = 'مدت زمان جلسه باید بیشتر از صفر باشد';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (validateForm()) {
      onSave(formData);
    }
  };

  const handleClose = () => {
    setFormData({
      session_number: nextSessionNumber,
      title: '',
      description: '',
      scheduled_datetime: '',
      duration_minutes: 120,
      materials: '',
      homework: '',
      session_video: '',
      croom_platform_link: '',
    });
    setErrors({});
    onClose();
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={faIR}>
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {session ? 'ویرایش جلسه' : 'افزودن جلسه جدید'}
          {workshopTitle && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              کارگاه: {workshopTitle}
            </Typography>
          )}
        </DialogTitle>

        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' }, gap: 2 }}>
              <Box>
                <TextField
                  fullWidth
                  label="شماره جلسه"
                  value={formData.session_number}
                  onChange={(e) => handleChange('session_number', parseInt(e.target.value) || 1)}
                  error={!!errors.session_number}
                  helperText={errors.session_number}
                  type="number"
                  disabled
                />
              </Box>

              <Box>
                <TextField
                  fullWidth
                  label="مدت زمان (دقیقه)"
                  value={formData.duration_minutes}
                  onChange={(e) => handleChange('duration_minutes', parseInt(e.target.value) || 120)}
                  error={!!errors.duration_minutes}
                  helperText={errors.duration_minutes}
                  type="number"
                />
              </Box>

              <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                <TextField
                  fullWidth
                  label="عنوان جلسه"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  error={!!errors.title}
                  helperText={errors.title}
                  required
                />
              </Box>

              <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                <TextField
                  fullWidth
                  label="توضیحات جلسه"
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  multiline
                  rows={3}
                />
              </Box>

              <Box>
                <DateTimePicker
                  label="تاریخ و زمان جلسه"
                  value={formData.scheduled_datetime ? new Date(formData.scheduled_datetime) : null}
                  onChange={(date) => handleChange('scheduled_datetime', date?.toISOString() || '')}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      error: !!errors.scheduled_datetime,
                      helperText: errors.scheduled_datetime,
                    },
                  }}
                />
              </Box>

              <Box>
                <FormControl fullWidth>
                  <InputLabel>مدت زمان پیش‌فرض</InputLabel>
                  <Select
                    value={formData.duration_minutes}
                    onChange={(e) => handleChange('duration_minutes', e.target.value)}
                    label="مدت زمان پیش‌فرض"
                  >
                    <MenuItem value={60}>1 ساعت</MenuItem>
                    <MenuItem value={90}>1.5 ساعت</MenuItem>
                    <MenuItem value={120}>2 ساعت</MenuItem>
                    <MenuItem value={150}>2.5 ساعت</MenuItem>
                    <MenuItem value={180}>3 ساعت</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                <TextField
                  fullWidth
                  label="مواد و منابع جلسه"
                  value={formData.materials}
                  onChange={(e) => handleChange('materials', e.target.value)}
                  multiline
                  rows={3}
                  placeholder="لیست مواد، فایل‌ها، و منابع مورد نیاز برای این جلسه..."
                />
              </Box>

              <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                <TextField
                  fullWidth
                  label="تکلیف و تمرین"
                  value={formData.homework}
                  onChange={(e) => handleChange('homework', e.target.value)}
                  multiline
                  rows={3}
                  placeholder="تکالیف و تمرینات مربوط به این جلسه..."
                />
              </Box>

              <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                <TextField
                  fullWidth
                  label="ویدیو جلسه (لینک یا فایل)"
                  value={formData.session_video}
                  onChange={(e) => handleChange('session_video', e.target.value)}
                  placeholder="لینک ویدیو جلسه یا آدرس فایل..."
                  helperText="می‌توانید لینک ویدیو یا آدرس فایل ویدیو را وارد کنید"
                />
              </Box>

              <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
                <TextField
                  fullWidth
                  label="لینک پلتفرم سی‌روم"
                  value={formData.croom_platform_link}
                  onChange={(e) => handleChange('croom_platform_link', e.target.value)}
                  placeholder="https://croom.ir/..."
                  helperText="لینک پلتفرم سی‌روم برای بحث‌های آنلاین"
                />
              </Box>
            </Box>

            {Object.keys(errors).length > 0 && (
              <Alert severity="error" sx={{ mt: 2 }}>
                لطفاً خطاهای موجود را برطرف کنید
              </Alert>
            )}
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            انصراف
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={loading}
          >
            {loading ? 'در حال ذخیره...' : (session ? 'ویرایش' : 'افزودن')}
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
};

export default SessionFormDialog;
