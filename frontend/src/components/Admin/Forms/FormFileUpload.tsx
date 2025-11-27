import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  IconButton,
  Paper,
  FormHelperText,
} from '@mui/material';
import { CloudUpload, Close } from '@mui/icons-material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';

interface FormFileUploadProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  accept?: string;
  maxSize?: number; // in MB
  preview?: boolean;
}

function FormFileUpload<T extends FieldValues>({
  name,
  control,
  label,
  accept = 'image/*',
  maxSize = 5,
  preview = true,
}: FormFileUploadProps<T>) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>,
    onChange: (value: any) => void
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      // Check file size
      if (file.size > maxSize * 1024 * 1024) {
        alert(`حجم فایل نباید بیشتر از ${maxSize} مگابایت باشد`);
        return;
      }

      onChange(file);

      // Create preview for images
      if (preview && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setPreviewUrl(reader.result as string);
        };
        reader.readAsDataURL(file);
      }
    }
  };

  const handleRemove = (onChange: (value: any) => void) => {
    onChange(null);
    setPreviewUrl(null);
  };

  return (
    <Controller
      name={name}
      control={control}
      render={({ field: { onChange, value }, fieldState: { error } }) => (
        <Box>
          <input
            accept={accept}
            style={{ display: 'none' }}
            id={`file-upload-${name}`}
            type="file"
            onChange={(e) => handleFileChange(e, onChange)}
          />
          <label htmlFor={`file-upload-${name}`}>
            <Button
              variant="outlined"
              component="span"
              startIcon={<CloudUpload />}
              fullWidth
              sx={{ mb: 1 }}
            >
              {label}
            </Button>
          </label>

          {value && (
            <Paper
              variant="outlined"
              sx={{
                p: 2,
                mt: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {previewUrl && (
                  <Box
                    component="img"
                    src={previewUrl}
                    alt="Preview"
                    sx={{
                      width: 80,
                      height: 80,
                      objectFit: 'cover',
                      borderRadius: 1,
                    }}
                  />
                )}
                <Typography variant="body2">
                  {value.name || 'فایل انتخاب شده'}
                </Typography>
              </Box>
              <IconButton
                size="small"
                onClick={() => handleRemove(onChange)}
                color="error"
              >
                <Close />
              </IconButton>
            </Paper>
          )}

          {error && (
            <FormHelperText error sx={{ mt: 1 }}>
              {error.message}
            </FormHelperText>
          )}
        </Box>
      )}
    />
  );
}

export default FormFileUpload;

