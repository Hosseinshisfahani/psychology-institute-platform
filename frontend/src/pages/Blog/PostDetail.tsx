import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Spinner, Alert, Form } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';
import { useAuth } from '../../contexts/AuthContext';
import { blogApi, Comment } from '../../services/blogApi';

interface Post {
  id: number;
  title: string;
  content: string;
  featured_image?: string;
  category: {
    name: string;
  };
  tags: Array<{
    name: string;
    slug: string;
  }>;
  author_name: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  created_at_persian: string;
}

const PostDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const { t } = useI18n();
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [likeError, setLikeError] = useState<string>('');
  const [isLiked, setIsLiked] = useState<boolean>(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState<boolean>(false);
  const [likeAnimation, setLikeAnimation] = useState<boolean>(false);
  const [commentContent, setCommentContent] = useState<string>('');
  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [replyContent, setReplyContent] = useState<{ [key: number]: string }>({});
  const [commentError, setCommentError] = useState<string>('');
  const [commentSuccess, setCommentSuccess] = useState<boolean>(false);

  const { data: post, isLoading } = useQuery({
    queryKey: ['post', slug],
    queryFn: async () => {
      return await blogApi.getPost(slug!);
    },
    enabled: !!slug,
  });

  // Fetch comments
  const { data: commentsData, isLoading: commentsLoading, refetch: refetchComments } = useQuery({
    queryKey: ['post-comments', slug],
    queryFn: async () => {
      return await blogApi.getComments(slug!);
    },
    enabled: !!slug,
  });

  // Ensure comments is always an array
  const comments = Array.isArray(commentsData) ? commentsData : (commentsData?.results || []);

  // Check if user has already liked this post (this would need backend support)
  // For now, we'll track it locally after the first like action

  // Like mutation
  const likeMutation = useMutation({
    mutationFn: () => blogApi.toggleLike(slug!),
    onSuccess: (data) => {
      // Update the post data with new like count
      queryClient.setQueryData(['post', slug], (oldData: Post | undefined) => {
        if (oldData) {
          return {
            ...oldData,
            like_count: data.like_count,
          };
        }
        return oldData;
      });
      
      // Update like status and show success message
      setIsLiked(data.liked);
      setLikeError('');
      setShowSuccessMessage(true);
      
      // Trigger animation
      setLikeAnimation(true);
      setTimeout(() => setLikeAnimation(false), 600);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setShowSuccessMessage(false);
      }, 3000);
    },
    onError: (error: any) => {
      if (error.response?.status === 401) {
        setLikeError('لطفاً ابتدا وارد شوید');
      } else {
        setLikeError('خطا در ثبت لایک. لطفاً دوباره تلاش کنید.');
      }
    },
  });

  const handleLike = () => {
    if (!isAuthenticated) {
      setLikeError('لطفاً ابتدا وارد شوید');
      return;
    }
    likeMutation.mutate();
  };

  // Comment mutation
  const commentMutation = useMutation({
    mutationFn: ({ content, parentId }: { content: string; parentId?: number }) => 
      blogApi.createComment(slug!, content, parentId),
    onSuccess: () => {
      setCommentContent('');
      setReplyTo(null);
      setCommentError('');
      setCommentSuccess(true);
      refetchComments();
      queryClient.invalidateQueries({ queryKey: ['post', slug] });
      // Hide success message after 3 seconds
      setTimeout(() => {
        setCommentSuccess(false);
      }, 3000);
    },
    onError: (error: any) => {
      console.error('Comment submission error:', error);
      if (error.response?.status === 401) {
        setCommentError('لطفاً ابتدا وارد شوید');
      } else if (error.response?.status === 400) {
        setCommentError(error.response?.data?.error || 'لطفاً متن نظر را وارد کنید');
      } else {
        setCommentError('خطا در ثبت نظر. لطفاً دوباره تلاش کنید.');
      }
      // Clear error after 5 seconds
      setTimeout(() => {
        setCommentError('');
      }, 5000);
    },
  });

  const handleSubmitComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('لطفاً ابتدا وارد شوید');
      return;
    }
    if (!commentContent.trim()) {
      alert('لطفاً متن نظر را وارد کنید');
      return;
    }
    commentMutation.mutate({ content: commentContent });
  };

  const handleReply = (parentId: number, content: string) => {
    if (!isAuthenticated) {
      alert('لطفاً ابتدا وارد شوید');
      return;
    }
    if (!content.trim()) {
      alert('لطفاً متن پاسخ را وارد کنید');
      return;
    }
    commentMutation.mutate({ content, parentId });
    setReplyContent({ ...replyContent, [parentId]: '' });
  };

  // Organize comments into tree structure
  const organizeComments = (comments: Comment[]): Comment[] => {
    const commentMap = new Map<number, Comment & { replies?: Comment[] }>();
    const rootComments: (Comment & { replies?: Comment[] })[] = [];

    // First pass: create map of all comments
    comments.forEach(comment => {
      commentMap.set(comment.id, { ...comment, replies: [] });
    });

    // Second pass: organize into tree
    comments.forEach(comment => {
      const commentWithReplies = commentMap.get(comment.id)!;
      if (comment.parent) {
        const parent = commentMap.get(comment.parent);
        if (parent) {
          if (!parent.replies) parent.replies = [];
          parent.replies.push(commentWithReplies);
        }
      } else {
        rootComments.push(commentWithReplies);
      }
    });

    return rootComments;
  };

  const organizedComments = organizeComments(comments);

  if (isLoading) {
    return (
      <Container className="py-5">
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">{t('common.loading')}</span>
          </Spinner>
        </div>
      </Container>
    );
  }

  if (!post) {
    return (
      <Container className="py-5">
        <Card>
          <Card.Body className="text-center py-5">
            <h5>مقاله یافت نشد</h5>
            <Link to="/blog" className="btn btn-primary">
              بازگشت به وبلاگ
            </Link>
          </Card.Body>
        </Card>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>{post.title} - {t('nav.blog')}</title>
        <meta name="description" content={post.content.substring(0, 160)} />
      </Helmet>

      <Container className="py-5">
        <Row>
          <Col lg={8}>
            <article>
              <div className="mb-4">
                <div className="d-flex align-items-center mb-3">
                  <span className="badge bg-primary me-2">{post.category.name}</span>
                  <small className="text-muted">{post.created_at_persian}</small>
                </div>
                
                <h1 className="mb-3">{post.title}</h1>
                
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div className="d-flex align-items-center">
                    <i className="fas fa-user me-2"></i>
                    <span>{post.author_name}</span>
                  </div>
                  <div className="d-flex gap-3">
                    <small className="text-muted">
                      <i className="fas fa-eye me-1"></i>
                      {post.view_count}
                    </small>
                    <small className="text-muted">
                      <i className="fas fa-heart me-1"></i>
                      {post.like_count}
                    </small>
                    <small className="text-muted">
                      <i className="fas fa-comment me-1"></i>
                      {post.comment_count}
                    </small>
                  </div>
                </div>

                {post.featured_image && (
                  <img 
                    src={post.featured_image} 
                    alt={post.title}
                    className="img-fluid rounded mb-4"
                    style={{ width: '100%', height: '400px', objectFit: 'cover' }}
                    loading="lazy"
                  />
                )}
              </div>

              <div 
                className="post-content"
                dangerouslySetInnerHTML={{ __html: post.content }}
              />

              {post.tags && post.tags.length > 0 && (
                <div className="mt-4">
                  <h6>برچسب‌ها:</h6>
                  <div className="d-flex flex-wrap gap-2">
                    {post.tags.map((tag: { name: string; slug: string; }) => (
                      <span key={tag.slug} className="badge bg-secondary">
                        {tag.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-4 d-flex justify-content-between">
                <Link to="/blog" className="btn btn-outline-primary">
                  <i className="fas fa-arrow-right me-2"></i>
                  بازگشت به وبلاگ
                </Link>
                <div className="d-flex flex-column align-items-end">
                  <Button 
                    variant={
                      likeMutation.isPending 
                        ? "secondary" 
                        : isLiked 
                          ? "danger" 
                          : "outline-danger"
                    }
                    onClick={handleLike}
                    disabled={likeMutation.isPending}
                    className="mb-2"
                    style={{
                      transform: likeAnimation ? 'scale(1.2)' : isLiked ? 'scale(1.05)' : 'scale(1)',
                      transition: 'all 0.3s ease-in-out',
                      boxShadow: isLiked ? '0 4px 8px rgba(220, 53, 69, 0.3)' : 'none'
                    }}
                  >
                    {likeMutation.isPending ? (
                      <>
                        <Spinner size="sm" className="me-2" />
                        در حال پردازش...
                      </>
                    ) : (
                      <>
                        <i 
                          className={`fas fa-heart me-2 ${isLiked ? 'text-white' : ''} ${likeAnimation ? 'fa-beat' : ''}`}
                          style={{ 
                            color: likeAnimation ? '#ff6b6b' : undefined,
                            transition: 'color 0.3s ease-in-out'
                          }}
                        ></i>
                        {isLiked ? 'لایک شده' : 'لایک'}
                      </>
                    )}
                  </Button>
                  
                  {showSuccessMessage && (
                    <Alert variant="success" className="mb-2" style={{ fontSize: '0.875rem' }}>
                      <i className="fas fa-check-circle me-2"></i>
                      {isLiked ? 'لایک شد!' : 'لایک برداشته شد!'}
                    </Alert>
                  )}
                  
                  {likeError && (
                    <Alert variant="danger" className="mb-0" style={{ fontSize: '0.875rem' }}>
                      {likeError}
                    </Alert>
                  )}
                </div>
              </div>

              {/* Comments Section */}
              <div className="mt-5">
                <h4 className="mb-4">
                  <i className="fas fa-comments me-2"></i>
                  نظرات ({comments.length})
                </h4>

                {/* Comment Form */}
                {isAuthenticated ? (
                  <Card className="mb-4">
                    <Card.Body>
                      <Form onSubmit={handleSubmitComment}>
                        <Form.Group className="mb-3">
                          <Form.Label>نظر شما</Form.Label>
                          <Form.Control
                            as="textarea"
                            rows={4}
                            value={commentContent}
                            onChange={(e) => {
                              setCommentContent(e.target.value);
                              setCommentError('');
                            }}
                            placeholder="نظر خود را بنویسید..."
                            required
                            disabled={commentMutation.isPending}
                          />
                        </Form.Group>
                        {commentSuccess && (
                          <Alert variant="success" className="mb-3">
                            <i className="fas fa-check-circle me-2"></i>
                            نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده خواهد شد.
                          </Alert>
                        )}
                        {commentError && (
                          <Alert variant="danger" className="mb-3">
                            <i className="fas fa-exclamation-circle me-2"></i>
                            {commentError}
                          </Alert>
                        )}
                        <Button 
                          type="submit" 
                          variant="primary"
                          disabled={commentMutation.isPending || !commentContent.trim()}
                        >
                          {commentMutation.isPending ? (
                            <>
                              <Spinner size="sm" className="me-2" />
                              در حال ارسال...
                            </>
                          ) : (
                            <>
                              <i className="fas fa-paper-plane me-2"></i>
                              ارسال نظر
                            </>
                          )}
                        </Button>
                      </Form>
                    </Card.Body>
                  </Card>
                ) : (
                  <Alert variant="info" className="mb-4">
                    <i className="fas fa-info-circle me-2"></i>
                    برای ثبت نظر، لطفاً <Link to="/login">وارد حساب کاربری</Link> خود شوید.
                  </Alert>
                )}

                {/* Comments List */}
                {commentsLoading ? (
                  <div className="text-center py-4">
                    <Spinner animation="border" />
                  </div>
                ) : organizedComments.length > 0 ? (
                  <div>
                    {organizedComments.map((comment) => (
                      <CommentItem
                        key={comment.id}
                        comment={comment}
                        isAuthenticated={isAuthenticated}
                        replyContent={replyContent}
                        setReplyContent={setReplyContent}
                        handleReply={handleReply}
                        commentMutation={commentMutation}
                      />
                    ))}
                  </div>
                ) : (
                  <Alert variant="secondary" className="text-center">
                    <i className="fas fa-comment-slash me-2"></i>
                    هنوز نظری ثبت نشده است. اولین نفری باشید که نظر می‌دهد!
                  </Alert>
                )}
              </div>
            </article>
          </Col>

          <Col lg={4}>
            <Card>
              <Card.Header>
                <h6>دسته‌بندی‌های مرتبط</h6>
              </Card.Header>
              <Card.Body>
                <p className="text-muted">به زودی...</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

// Comment Item Component
interface CommentItemProps {
  comment: Comment & { replies?: Comment[] };
  isAuthenticated: boolean;
  replyContent: { [key: number]: string };
  setReplyContent: (content: { [key: number]: string }) => void;
  handleReply: (parentId: number, content: string) => void;
  commentMutation: any;
}

const CommentItem: React.FC<CommentItemProps> = ({
  comment,
  isAuthenticated,
  replyContent,
  setReplyContent,
  handleReply,
  commentMutation,
}) => {
  const [showReplyForm, setShowReplyForm] = useState(false);

  return (
    <Card className="mb-3" style={{ marginRight: comment.parent ? '2rem' : '0' }}>
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div>
            <strong>{comment.author.full_name}</strong>
            <small className="text-muted ms-2">{comment.created_at_persian}</small>
          </div>
        </div>
        <p className="mb-2" style={{ whiteSpace: 'pre-wrap' }}>{comment.content}</p>
        
        {isAuthenticated && (
          <Button
            variant="link"
            size="sm"
            className="p-0 text-decoration-none"
            onClick={() => setShowReplyForm(!showReplyForm)}
          >
            <i className="fas fa-reply me-1"></i>
            پاسخ
          </Button>
        )}

        {showReplyForm && isAuthenticated && (
          <div className="mt-3 p-3 bg-light rounded">
            <Form
              onSubmit={(e) => {
                e.preventDefault();
                const content = replyContent[comment.id] || '';
                if (content.trim()) {
                  handleReply(comment.id, content);
                  setShowReplyForm(false);
                }
              }}
            >
              <Form.Group className="mb-2">
                <Form.Control
                  as="textarea"
                  rows={2}
                  value={replyContent[comment.id] || ''}
                  onChange={(e) =>
                    setReplyContent({ ...replyContent, [comment.id]: e.target.value })
                  }
                  placeholder="پاسخ خود را بنویسید..."
                  required
                />
              </Form.Group>
              <div className="d-flex gap-2">
                <Button type="submit" size="sm" variant="primary" disabled={commentMutation.isPending}>
                  ارسال پاسخ
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  onClick={() => {
                    setShowReplyForm(false);
                    setReplyContent({ ...replyContent, [comment.id]: '' });
                  }}
                >
                  انصراف
                </Button>
              </div>
            </Form>
          </div>
        )}

        {/* Nested Replies */}
        {comment.replies && comment.replies.length > 0 && (
          <div className="mt-3" style={{ marginRight: '1.5rem' }}>
            {comment.replies.map((reply) => (
              <CommentItem
                key={reply.id}
                comment={reply}
                isAuthenticated={isAuthenticated}
                replyContent={replyContent}
                setReplyContent={setReplyContent}
                handleReply={handleReply}
                commentMutation={commentMutation}
              />
            ))}
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default PostDetail;
