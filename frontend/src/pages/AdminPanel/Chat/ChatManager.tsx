import React, { useMemo, useState } from 'react';
import {
  Avatar,
  Badge,
  Box,
  Button,
  Card,
  CircularProgress,
  Divider,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { useSnackbar } from 'notistack';
import {
  Refresh as RefreshIcon,
  Send as SendIcon,
  Search as SearchIcon,
  ChatBubbleOutline as ChatBubbleOutlineIcon,
} from '@mui/icons-material';

interface ThreadSummary {
  id: number;
  user_name: string;
  user_email: string;
  assigned_admin_name: string | null;
  unread_count: number;
  last_message_preview: string;
  last_message_at: string | null;
}

interface ThreadMessage {
  id: number;
  message: string;
  is_from_admin: boolean;
  created_at: string;
  sender_name: string;
}

interface ThreadDetail {
  id: number;
  user_name: string;
  user_email: string;
  assigned_admin_name: string | null;
  messages: ThreadMessage[];
}

const formatDateTime = (value: string | null) => {
  if (!value) {
    return '—';
  }
  try {
    return new Date(value).toLocaleString('fa-IR', {
      hour: '2-digit',
      minute: '2-digit',
      day: '2-digit',
      month: 'short',
    });
  } catch (error) {
    return value;
  }
};

const messageBubbleStyles = (isAdmin: boolean) => ({
  borderRadius: 3,
  p: 1.5,
  bgcolor: isAdmin ? 'primary.main' : '#f1f4fb',
  color: isAdmin ? 'primary.contrastText' : 'text.primary',
  alignSelf: isAdmin ? 'flex-end' : 'flex-start',
  maxWidth: '75%',
  boxShadow: isAdmin ? 2 : 0,
});

const ChatManager: React.FC = () => {
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();
  const [selectedThreadId, setSelectedThreadId] = useState<number | null>(null);
  const [messageDraft, setMessageDraft] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const threadsQuery = useQuery<ThreadSummary[]>({
    queryKey: ['admin-chat-threads'],
    queryFn: async () => {
      const response = await axios.get('/api/chat/admin/threads/');
      return response.data;
    },
    refetchInterval: 20000,
  });

  const filteredThreads = useMemo(() => {
    if (!threadsQuery.data) {
      return [];
    }
    if (!searchTerm.trim()) {
      return threadsQuery.data;
    }
    const term = searchTerm.trim().toLowerCase();
    return threadsQuery.data.filter(
      (thread) =>
        thread.user_name?.toLowerCase().includes(term) ||
        thread.user_email?.toLowerCase().includes(term),
    );
  }, [threadsQuery.data, searchTerm]);

  const threadDetailQuery = useQuery<ThreadDetail>({
    queryKey: ['admin-chat-thread', selectedThreadId],
    queryFn: async () => {
      if (selectedThreadId == null) {
        return null as unknown as ThreadDetail;
      }
      const response = await axios.get(`/api/chat/admin/thread/${selectedThreadId}/`);
      return response.data;
    },
    enabled: selectedThreadId != null,
    refetchInterval: 15000,
  });

  const sendMessageMutation = useMutation({
    mutationFn: async ({ threadId, message }: { threadId: number; message: string }) => {
      const response = await axios.post('/api/chat/admin/message/', {
        thread_id: threadId,
        message,
      });
      return response.data;
    },
    onSuccess: () => {
      enqueueSnackbar('پیام ارسال شد', { variant: 'success' });
      setMessageDraft('');
      queryClient.invalidateQueries({ queryKey: ['admin-chat-thread', selectedThreadId] });
      queryClient.invalidateQueries({ queryKey: ['admin-chat-threads'] });
    },
    onError: () => {
      enqueueSnackbar('ارسال پیام با خطا مواجه شد', { variant: 'error' });
    },
  });

  const handleSendMessage = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedThreadId || !messageDraft.trim()) {
      return;
    }
    sendMessageMutation.mutate({ threadId: selectedThreadId, message: messageDraft.trim() });
  };

  const selectedThread = threadDetailQuery.data;

  return (
    <Box p={3}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h5" fontWeight={700}>
          مدیریت گفت‌وگوهای کاربران
        </Typography>
        <Tooltip title="به‌روزرسانی">
          <span>
            <IconButton
              onClick={() => queryClient.invalidateQueries({ queryKey: ['admin-chat-threads'] })}
              disabled={threadsQuery.isFetching}
            >
              {threadsQuery.isFetching ? <CircularProgress size={20} /> : <RefreshIcon />}
            </IconButton>
          </span>
        </Tooltip>
      </Stack>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
        <Box flex={{ xs: '1 1 auto', md: '0 0 360px' }} display="flex">
          <Card sx={{ p: 2, height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
            <TextField
              size="small"
              placeholder="جستجوی کاربران..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" />
                  </InputAdornment>
                ),
              }}
            />
            <Divider sx={{ my: 2 }} />
            {threadsQuery.isLoading ? (
              <Box display="flex" justifyContent="center" mt={4}>
                <CircularProgress />
              </Box>
            ) : filteredThreads.length === 0 ? (
              <Stack alignItems="center" spacing={2} mt={4} color="text.secondary">
                <ChatBubbleOutlineIcon fontSize="large" />
                <Typography variant="body2">گفتگویی برای نمایش وجود ندارد.</Typography>
              </Stack>
            ) : (
              <List sx={{ flex: 1, overflowY: 'auto' }}>
                {filteredThreads.map((thread) => {
                  const isSelected = thread.id === selectedThreadId;
                  const initials = thread.user_name?.charAt(0) || thread.user_email?.charAt(0) || '?';
                  return (
                    <ListItemButton
                      key={thread.id}
                      selected={isSelected}
                      onClick={() => setSelectedThreadId(thread.id)}
                      sx={{
                        borderRadius: 2,
                        mb: 1,
                        alignItems: 'flex-start',
                      }}
                    >
                      <ListItem disablePadding>
                        <ListItemAvatar>
                          <Badge
                            color="error"
                            badgeContent={thread.unread_count || 0}
                            invisible={!thread.unread_count}
                            overlap="circular"
                          >
                            <Avatar>{initials}</Avatar>
                          </Badge>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box display="flex" justifyContent="space-between" alignItems="center" gap={1}>
                              <Typography variant="subtitle2" fontWeight={isSelected ? 700 : 600}>
                                {thread.user_name || thread.user_email}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {formatDateTime(thread.last_message_at)}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}
                            >
                              {thread.last_message_preview || 'بدون پیام'}
                            </Typography>
                          }
                        />
                      </ListItem>
                    </ListItemButton>
                  );
                })}
              </List>
            )}
          </Card>
        </Box>

        <Box flex={1} display="flex">
          <Card sx={{ p: 3, height: '100%', minHeight: 500, width: '100%', display: 'flex', flexDirection: 'column' }}>
            {selectedThreadId == null ? (
              <Stack alignItems="center" justifyContent="center" height="100%" spacing={2} color="text.secondary">
                <ChatBubbleOutlineIcon fontSize="large" />
                <Typography variant="body2">برای مشاهده پیام‌ها یک گفتگو را انتخاب کنید.</Typography>
              </Stack>
            ) : threadDetailQuery.isLoading || threadDetailQuery.isFetching ? (
              <Box display="flex" justifyContent="center" alignItems="center" flexGrow={1}>
                <CircularProgress />
              </Box>
            ) : selectedThread ? (
              <>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Box>
                    <Typography variant="h6" fontWeight={700}>
                      {selectedThread.user_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedThread.user_email}
                    </Typography>
                  </Box>
                  {selectedThread.assigned_admin_name && (
                    <Typography variant="body2" color="text.secondary">
                      ادمین مسئول: {selectedThread.assigned_admin_name}
                    </Typography>
                  )}
                </Box>
                <Divider />
                <Box
                  sx={{
                    flexGrow: 1,
                    my: 2,
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1.5,
                  }}
                >
                  {selectedThread.messages.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" textAlign="center" mt={4}>
                      هنوز پیامی ثبت نشده است.
                    </Typography>
                  ) : (
                    selectedThread.messages.map((message) => (
                      <Box key={message.id} sx={messageBubbleStyles(message.is_from_admin)}>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                          {message.message}
                        </Typography>
                        <Typography variant="caption" sx={{ mt: 0.5, opacity: 0.75, display: 'block' }}>
                          {message.sender_name} •{' '}
                          {new Date(message.created_at).toLocaleString('fa-IR', {
                            hour: '2-digit',
                            minute: '2-digit',
                            day: 'numeric',
                            month: 'short',
                          })}
                        </Typography>
                      </Box>
                    ))
                  )}
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Box component="form" onSubmit={handleSendMessage}>
                  <TextField
                    fullWidth
                    multiline
                    minRows={2}
                    maxRows={6}
                    placeholder="پاسخ خود را بنویسید..."
                    value={messageDraft}
                    onChange={(event) => setMessageDraft(event.target.value)}
                  />
                  <Stack direction="row" justifyContent="flex-end" mt={2}>
                    <Button
                      type="submit"
                      variant="contained"
                      endIcon={<SendIcon />}
                      disabled={!messageDraft.trim() || sendMessageMutation.isPending}
                    >
                      ارسال پیام
                    </Button>
                  </Stack>
                </Box>
              </>
            ) : (
              <Typography variant="body2" color="error">
                بارگذاری گفتگو با خطا مواجه شد.
              </Typography>
            )}
          </Card>
        </Box>
      </Stack>
    </Box>
  );
};

export default ChatManager;

