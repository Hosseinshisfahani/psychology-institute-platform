import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Avatar,
  Divider,
  IconButton,
  Paper,
} from '@mui/material';
import {
  Close as CloseIcon,
  Edit as EditIcon,
  Share as ShareIcon,
} from '@mui/icons-material';
import { BlogPost } from '../../../services/blogAdminApi';
import StatusBadge from '../../../components/Admin/Blog/StatusBadge';
import CategoryChip from '../../../components/Admin/Blog/CategoryChip';
import TagChip from '../../../components/Admin/Blog/TagChip';

interface BlogPreviewProps {
  open: boolean;
  onClose: () => void;
  post: BlogPost | null;
  onEdit?: () => void;
}

const BlogPreview: React.FC<BlogPreviewProps> = ({
  open,
  onClose,
  post,
  onEdit,
}) => {
  if (!post) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">پیش‌نمایش پست</Typography>
        <Box>
          {onEdit && (
            <IconButton onClick={onEdit} color="primary" sx={{ mr: 1 }}>
              <EditIcon />
            </IconButton>
          )}
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Paper elevation={0} sx={{ p: 3, border: '1px solid', borderColor: 'divider' }}>
          {/* Post Header */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              {post.title}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ width: 32, height: 32 }}>
                  {post.author_name?.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="body2" fontWeight={600}>
                    {post.author_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {post.author_email}
                  </Typography>
                </Box>
              </Box>

              <Divider orientation="vertical" flexItem />

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {post.created_at_persian}
                </Typography>
                {post.published_at_persian && (
                  <>
                    <Typography variant="body2" color="text.secondary">
                      •
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      منتشر شده: {post.published_at_persian}
                    </Typography>
                  </>
                )}
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
              <StatusBadge status={post.status} />
              <CategoryChip
                name={post.category_name || ''}
                color={post.category_color}
              />
              {post.is_featured && (
                <Chip
                  label="ویژه"
                  color="warning"
                  size="small"
                />
              )}
            </Box>

            {post.tags_data && post.tags_data.length > 0 && (
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                {post.tags_data.map((tag) => (
                  <TagChip
                    key={tag.id}
                    name={tag.name}
                    size="small"
                  />
                ))}
              </Box>
            )}

            {post.excerpt && (
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2, fontStyle: 'italic' }}>
                {post.excerpt}
              </Typography>
            )}
          </Box>

          {/* Featured Image */}
          {post.featured_image && (
            <Box sx={{ mb: 3 }}>
              <Box
                component="img"
                src={post.featured_image}
                alt={post.title}
                sx={{
                  width: '100%',
                  maxHeight: 400,
                  objectFit: 'cover',
                  borderRadius: 1,
                }}
              />
            </Box>
          )}

          {/* Post Content */}
          <Box sx={{ mb: 3 }}>
            <div
              dangerouslySetInnerHTML={{ __html: post.content }}
              style={{
                lineHeight: '1.8',
                fontSize: '16px',
                fontFamily: 'Vazir, Arial, sans-serif',
              }}
            />
          </Box>

          {/* Post Stats */}
          <Box sx={{ display: 'flex', gap: 3, mb: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                بازدید:
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {post.view_count}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                لایک:
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {post.like_count}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                نظرات:
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {post.allow_comments ? 'فعال' : 'غیرفعال'}
              </Typography>
            </Box>
          </Box>

          {/* SEO Meta */}
          {(post.meta_title || post.meta_description) && (
            <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>
                اطلاعات SEO
              </Typography>
              {post.meta_title && (
                <Box sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    عنوان متا:
                  </Typography>
                  <Typography variant="body2">
                    {post.meta_title}
                  </Typography>
                </Box>
              )}
              {post.meta_description && (
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    توضیحات متا:
                  </Typography>
                  <Typography variant="body2">
                    {post.meta_description}
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </Paper>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          بستن
        </Button>
        {onEdit && (
          <Button
            variant="contained"
            startIcon={<EditIcon />}
            onClick={onEdit}
          >
            ویرایش
          </Button>
        )}
        <Button
          variant="outlined"
          startIcon={<ShareIcon />}
          onClick={() => {
            // Copy URL to clipboard or open in new tab
            const url = `${window.location.origin}/blog/post/${post.slug}`;
            navigator.clipboard.writeText(url);
          }}
        >
          اشتراک‌گذاری
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default BlogPreview;
