import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Image as ImageIcon,
} from '@mui/icons-material';
import { fileUploadApi } from '../../../services/blogAdminApi';

interface ImageUploaderProps {
  value?: string;
  onChange: (url: string) => void;
  error?: boolean;
  helperText?: string;
  maxSize?: number; // in MB
  acceptedTypes?: string[];
}

const ImageUploader: React.FC<ImageUploaderProps> = ({
  value,
  onChange,
  error = false,
  helperText,
  maxSize = 5,
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp'],
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setErrorMessage('');

    // Validate file type
    if (!acceptedTypes.includes(file.type)) {
      setErrorMessage('فرمت فایل پشتیبانی نمی‌شود. لطفاً از فرمت‌های JPG، PNG یا WebP استفاده کنید.');
      return;
    }

    // Validate file size
    if (file.size > maxSize * 1024 * 1024) {
      setErrorMessage(`حجم فایل نباید بیشتر از ${maxSize} مگابایت باشد.`);
      return;
    }

    try {
      setUploading(true);
      const url = await fileUploadApi.uploadFile(file);
      onChange(url);
    } catch (error) {
      console.error('File upload error:', error);
      setErrorMessage('خطا در آپلود فایل. لطفاً دوباره تلاش کنید.');
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleRemove = () => {
    onChange('');
    setErrorMessage('');
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <Box>
      <Box
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
        sx={{
          border: `2px dashed ${error ? 'error.main' : dragActive ? 'primary.main' : 'grey.300'}`,
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: dragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        {value ? (
          <Box>
              <Box
                component="img"
                src={value}
                alt="Preview"
                loading="lazy"
                sx={{
                  maxWidth: '100%',
                  maxHeight: 200,
                  borderRadius: 1,
                  mb: 2,
              }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<UploadIcon />}
                onClick={(e) => {
                  e.stopPropagation();
                  handleClick();
                }}
                size="small"
              >
                تغییر تصویر
              </Button>
              <IconButton
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemove();
                }}
                size="small"
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          </Box>
        ) : (
          <Box>
            <ImageIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              تصویر شاخص را انتخاب کنید
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              فایل را اینجا بکشید یا کلیک کنید
            </Typography>
            <Typography variant="caption" color="text.secondary">
              فرمت‌های پشتیبانی شده: JPG، PNG، WebP (حداکثر {maxSize} مگابایت)
            </Typography>
          </Box>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedTypes.join(',')}
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
      </Box>

      {errorMessage && (
        <Alert severity="error" sx={{ mt: 1 }}>
          {errorMessage}
        </Alert>
      )}

      {error && helperText && (
        <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
          {helperText}
        </Typography>
      )}

      {uploading && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
          <CircularProgress size={16} />
          <Typography variant="caption" color="text.secondary">
            در حال آپلود...
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ImageUploader;
