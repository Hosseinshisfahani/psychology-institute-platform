import React, { useState, useEffect, useMemo } from 'react';
import { Container, Row, Col, Card, Badge, Button, ListGroup, Tab, Tabs, Alert, Spinner, Modal } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

type ShareStatus = { type: 'success' | 'error'; message: string } | null;

interface CourseVideo {
  id: number;
  title: string;
  description: string | null;
  video_file: string | null;
  video_url: string | null;
  attachment_file: string | null;
  attachment_file_name: string | null;
  attachment_file_size: string | null;
  duration_minutes: number | null;
  order: number;
  is_preview: boolean;
  allow_download: boolean;
  is_active: boolean;
  created_at: string;
}

interface EnrollmentStatus {
  is_enrolled: boolean;
  enrolled_at?: string;
  status?: string;
  is_purchased?: boolean;
}

interface CourseDetail {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  thumbnail: string | null;
  video_intro: string | null;
  price: string;
  discount_price: string | null;
  current_price: string;
  discount_percentage: number;
  is_free: boolean;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_hours: number;
  language: string;
  level: string;
  instructor_name: string;
  category_name: string;
  category_slug: string;
  enrollment_count: number;
  rating: number;
  review_count: number;
  prerequisites: string | null;
  learning_objectives: string;
  created_at: string;
  created_at_persian: string;
  published_at: string | null;
  videos: CourseVideo[];
  enrollment_status: EnrollmentStatus;
}

const CourseDetail: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState<CourseVideo | null>(null);
  const [couponCode, setCouponCode] = useState('');
  const [showCouponAlert, setShowCouponAlert] = useState(false);
  const [couponMessage, setCouponMessage] = useState('');
  const [completedVideoIds, setCompletedVideoIds] = useState<number[]>([]);
  const [shareStatus, setShareStatus] = useState<ShareStatus>(null);
  const [commentContent, setCommentContent] = useState('');
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const [replyContent, setReplyContent] = useState('');

  // Invalidate course detail cache on mount to ensure fresh enrollment status
  useEffect(() => {
    // Invalidate the course detail query to force a fresh fetch
    // This ensures enrollment status is always up-to-date
    queryClient.invalidateQueries({ queryKey: ['course-detail', slug] });
  }, [slug, queryClient]);

  // Prevent right-click and download shortcuts globally when modal is open
  // But allow video controls to work normally
  useEffect(() => {
    if (showVideoModal) {
      const handleContextMenu = (e: MouseEvent) => {
        // Allow context menu on video controls (they handle it themselves)
        const target = e.target as HTMLElement;
        if (target.tagName === 'VIDEO' || target.closest('video')) {
          // Video element handles its own context menu prevention
          return;
        }
        e.preventDefault();
        return false;
      };

      const handleKeyDown = (e: KeyboardEvent) => {
        // Don't block keys if user is interacting with video controls
        const target = e.target as HTMLElement;
        if (target.tagName === 'VIDEO' || target.closest('video')) {
          // Allow video keyboard controls (space, arrows, etc.)
          // Only block download-related shortcuts
          if (e.ctrlKey && (e.key === 's' || e.key === 'S')) {
            e.preventDefault();
            return false;
          }
          if (e.ctrlKey && (e.key === 'u' || e.key === 'U')) {
            e.preventDefault();
            return false;
          }
          return; // Allow other keys for video control
        }
        
        // For non-video elements, block download/save shortcuts
        if (e.ctrlKey && (e.key === 's' || e.key === 'S')) {
          e.preventDefault();
          return false;
        }
        if (e.ctrlKey && (e.key === 'u' || e.key === 'U')) {
          e.preventDefault();
          return false;
        }
        if (e.key === 'F12') {
          e.preventDefault();
          return false;
        }
        // Prevent Ctrl+Shift+I (DevTools)
        if (e.ctrlKey && e.shiftKey && e.key === 'I') {
          e.preventDefault();
          return false;
        }
        // Prevent Ctrl+Shift+C (Inspect)
        if (e.ctrlKey && e.shiftKey && e.key === 'C') {
          e.preventDefault();
          return false;
        }
      };

      // Only prevent text selection outside video and modal
      const handleSelectStart = (e: Event) => {
        const target = e.target as HTMLElement;
        // Allow selection for video controls and anything within the modal
        if (target.tagName === 'VIDEO' || 
            target.closest('video') || 
            target.closest('.modal-body') ||
            target.closest('[role="progressbar"]')) {
          return; // Allow selection within video controls
        }
        e.preventDefault();
        return false;
      };

      // Only prevent drag outside video and modal
      const handleDragStart = (e: DragEvent) => {
        const target = e.target as HTMLElement;
        // Allow drag for video controls
        if (target.tagName === 'VIDEO' || 
            target.closest('video') || 
            target.closest('.modal-body')) {
          return; // Allow drag within video controls
        }
        e.preventDefault();
        return false;
      };

      document.addEventListener('contextmenu', handleContextMenu);
      document.addEventListener('keydown', handleKeyDown);
      // Don't add selectstart/dragstart listeners globally - they interfere with video controls
      
      return () => {
        document.removeEventListener('contextmenu', handleContextMenu);
        document.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [showVideoModal]);

  // Fetch course detail
  const { data: course, isLoading, error } = useQuery<CourseDetail>({
    queryKey: ['course-detail', slug],
    queryFn: async () => {
      const response = await axios.get(`/api/courses/${slug}/`);
      return response.data;
    },
    enabled: !!slug,
    // Always refetch enrollment status when window regains focus or user is authenticated
    // This ensures enrollment status is up-to-date after purchases
    refetchOnWindowFocus: true,
    // Cache for 30 seconds only to ensure enrollment status is fresh
    staleTime: 30000,
  });

  // Add to cart mutation
  const addToCartMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/courses/add-to-cart/${slug}/`);
      return response.data;
    },
    onSuccess: (data) => {
      alert(data.message || 'دوره به سبد خرید اضافه شد');
      navigate('/payment/cart');
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در افزودن به سبد خرید');
    },
  });

  // Enroll in free course mutation
  const enrollMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/courses/enroll/${slug}/`);
      return response.data;
    },
    onSuccess: (data) => {
      alert(data.message || 'با موفقیت در دوره ثبت‌نام شدید');
      navigate(`/courses/learn/${slug}`);
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در ثبت‌نام');
    },
  });

  // Purchase course directly mutation
  const purchaseMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/courses/purchase/${slug}/`);
      return response.data;
    },
    onSuccess: (data) => {
      if (data.cart_url) {
        navigate(data.cart_url);
      } else {
        alert(data.message || 'دوره به سبد خرید اضافه شد');
        navigate('/payment/cart');
      }
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در خرید دوره');
    },
  });

  // Fetch comments
  const { data: comments = [], refetch: refetchComments } = useQuery({
    queryKey: ['course-comments', slug],
    queryFn: async () => {
      const response = await axios.get(`/api/courses/${slug}/comments/`);
      return response.data;
    },
    enabled: !!slug,
  });

  // Create comment mutation
  const createCommentMutation = useMutation({
    mutationFn: async (data: { content: string; parent?: number }) => {
      const response = await axios.post(`/api/courses/${slug}/comments/`, data);
      return response.data;
    },
    onSuccess: () => {
      setCommentContent('');
      setReplyContent('');
      setReplyingTo(null);
      refetchComments();
      alert('نظر شما با موفقیت ثبت شد و پس از تایید نمایش داده خواهد شد.');
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'خطا در ثبت نظر');
    },
  });

  const handleSubmitComment = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (!commentContent.trim()) {
      alert('لطفاً متن نظر را وارد کنید');
      return;
    }
    createCommentMutation.mutate({ content: commentContent });
  };

  const handleSubmitReply = (parentId: number) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (!replyContent.trim()) {
      alert('لطفاً متن پاسخ را وارد کنید');
      return;
    }
    createCommentMutation.mutate({ content: replyContent, parent: parentId });
  };

  const formatPrice = (price: string | number) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('fa-IR').format(numPrice);
  };

  const getDifficultyBadge = (difficulty: string) => {
    const difficultyMap = {
      'beginner': { text: 'مبتدی', variant: 'success' },
      'intermediate': { text: 'متوسط', variant: 'warning' },
      'advanced': { text: 'پیشرفته', variant: 'danger' }
    };
    return difficultyMap[difficulty as keyof typeof difficultyMap] || { text: difficulty, variant: 'secondary' };
  };

  const handlePlayVideo = (video: CourseVideo) => {
    setSelectedVideo(video);
    setShowVideoModal(true);
  };

  const handleAddToCart = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    addToCartMutation.mutate();
  };

  const handleEnroll = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    enrollMutation.mutate();
  };

  const handlePurchase = () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    purchaseMutation.mutate();
  };

  const progressStorageKey = useMemo(() => {
    if (!course) return null;
    if (user?.id) {
      return `course-progress-${user.id}-${course.id}`;
    }
    return `course-progress-guest-${course.id}`;
  }, [course, user?.id]);

  useEffect(() => {
    if (!course || !progressStorageKey) {
      setCompletedVideoIds([]);
      return;
    }

    try {
      const stored = localStorage.getItem(progressStorageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          setCompletedVideoIds(
            parsed.filter((id: number) => course.videos.some((video) => video.id === id))
          );
        }
      } else {
        setCompletedVideoIds([]);
      }
    } catch (_) {
      setCompletedVideoIds([]);
    }
  }, [course, progressStorageKey]);

  useEffect(() => {
    if (!progressStorageKey) return;
    localStorage.setItem(progressStorageKey, JSON.stringify(completedVideoIds));
  }, [completedVideoIds, progressStorageKey]);

  const handleStartLearning = () => {
    if (course?.enrollment_status.is_enrolled) {
      // Scroll to videos section
      const videosSection = document.querySelector('.course-videos-section');
      if (videosSection) {
        videosSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
      
      // Optionally play first video if available
      const firstEnrolledVideo = activeVideos.find(v => v.is_preview || course.enrollment_status.is_enrolled);
      if (firstEnrolledVideo) {
        setTimeout(() => {
          handlePlayVideo(firstEnrolledVideo);
        }, 500);
      }
    }
  };

  const activeVideos = course?.videos.filter(v => v.is_active) || [];
  const previewVideos = activeVideos.filter(v => v.is_preview);
  const difficultyInfo = course ? getDifficultyBadge(course.difficulty) : null;
  const completedVideosCount = completedVideoIds.length;
  const progressPercentage = activeVideos.length
    ? Math.round((completedVideosCount / activeVideos.length) * 100)
    : 0;

  useEffect(() => {
    if (!shareStatus) return;
    const timer = window.setTimeout(() => setShareStatus(null), 3000);
    return () => window.clearTimeout(timer);
  }, [shareStatus]);

  const handleToggleVideoCompletion = (videoId: number) => {
    setCompletedVideoIds((prev) => {
      if (prev.includes(videoId)) {
        return prev.filter((id) => id !== videoId);
      }
      return [...prev, videoId];
    });
  };

  const handleAutoCompleteVideo = (videoId: number) => {
    setCompletedVideoIds((prev) => {
      if (prev.includes(videoId)) {
        return prev;
      }
      return [...prev, videoId];
    });
  };

  const handleShare = async (platform: 'telegram' | 'whatsapp' | 'copy') => {
    if (!course) return;
    const shareUrl = window.location.href;
    const shareText = `${course.title} - ${course.short_description}`.trim();

    try {
      if (platform === 'telegram') {
        const url = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;
        window.open(url, '_blank', 'noopener,noreferrer');
        setShareStatus({ type: 'success', message: 'در حال باز کردن تلگرام برای اشتراک‌گذاری لینک.' });
      } else if (platform === 'whatsapp') {
        const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(`${shareText}\n${shareUrl}`)}`;
        window.open(url, '_blank', 'noopener,noreferrer');
        setShareStatus({ type: 'success', message: 'در حال باز کردن واتساپ برای اشتراک‌گذاری لینک.' });
      } else if (platform === 'copy') {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(shareUrl);
          setShareStatus({ type: 'success', message: 'لینک دوره با موفقیت کپی شد.' });
        } else {
          const fallbackSuccess = window.prompt('برای کپی، کلیدهای Cmd+C یا Ctrl+C را فشار دهید سپس Enter را بزنید.', shareUrl);
          if (fallbackSuccess !== null) {
            setShareStatus({ type: 'success', message: 'لینک دوره آماده کپی است.' });
          }
        }
      }
    } catch (err) {
      console.error('Share error:', err);
      setShareStatus({ type: 'error', message: 'در اشتراک‌گذاری لینک مشکلی رخ داد. لطفاً دوباره تلاش کنید.' });
    }
  };

  if (isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
        <p className="mt-3 text-muted">در حال بارگذاری دوره...</p>
      </Container>
    );
  }

  if (error || !course) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          <Alert.Heading>خطا</Alert.Heading>
          <p>دوره مورد نظر یافت نشد یا در حال حاضر در دسترس نیست.</p>
          <Link to="/courses" className="btn btn-primary">
            بازگشت به لیست دوره‌ها
          </Link>
        </Alert>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>{course.title} - دوره‌های آموزشی</title>
        <meta name="description" content={course.short_description} />
      </Helmet>

      {/* Hero Section with Thumbnail */}
      {course.thumbnail && (
        <div
          style={{
            backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url(${course.thumbnail})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            minHeight: '400px',
            display: 'flex',
            alignItems: 'center',
            color: 'white',
            padding: '4rem 0',
          }}
        >
          <Container>
            <Row>
              <Col lg={8}>
                <Badge bg="info" className="mb-3">{course.category_name}</Badge>
                {difficultyInfo && (
                  <Badge bg={difficultyInfo.variant as any} className="ms-2 mb-3">
                    {difficultyInfo.text}
                  </Badge>
                )}
                {course.is_free && (
                  <Badge bg="success" className="ms-2 mb-3">رایگان</Badge>
                )}
                <h1 className="display-4 fw-bold mb-3">{course.title}</h1>
                <p className="lead mb-4">{course.short_description}</p>
                <div className="d-flex align-items-center flex-wrap gap-4">
                  <div className="d-flex align-items-center gap-2">
                    <i className="fas fa-user"></i>
                    <span>{course.instructor_name}</span>
                  </div>
                  <div className="d-flex align-items-center gap-2">
                    <i className="fas fa-clock"></i>
                    <span>{course.duration_hours} ساعت</span>
                  </div>
                  <div className="d-flex align-items-center gap-2">
                    <i className="fas fa-users"></i>
                    <span>{course.enrollment_count} دانشجو</span>
                  </div>
                  {course.rating > 0 && (
                    <div className="d-flex align-items-center gap-2">
                      <i className="fas fa-star text-warning"></i>
                      <span>{course.rating.toFixed(1)} ({course.review_count} نظر)</span>
                    </div>
                  )}
                </div>
              </Col>
            </Row>
          </Container>
        </div>
      )}

      <Container className="py-5">
        <Row>
          {/* Main Content */}
          <Col lg={8}>
            {!course.thumbnail && (
              <Card className="mb-4">
                <Card.Body>
                  <div className="mb-3">
                    <Badge bg="info" className="me-2">{course.category_name}</Badge>
                    {difficultyInfo && (
                      <Badge bg={difficultyInfo.variant as any} className="me-2">
                        {difficultyInfo.text}
                      </Badge>
                    )}
                    {course.is_free && (
                      <Badge bg="success" className="me-2">رایگان</Badge>
                    )}
                  </div>
                  <h1 className="mb-3">{course.title}</h1>
                  <p className="text-muted lead">{course.short_description}</p>
                </Card.Body>
              </Card>
            )}

            {/* Enrollment Status Alert */}
            {course.enrollment_status.is_enrolled && (
              <Alert variant="success" className="mb-4">
                <i className="fas fa-check-circle me-2"></i>
                شما در این دوره ثبت‌نام کرده‌اید
                <Button
                  variant="success"
                  className="ms-3"
                  onClick={handleStartLearning}
                >
                  شروع یادگیری
                </Button>
              </Alert>
            )}

            {/* Intro Video */}
            {course.video_intro && (
              <Card className="mb-4">
                <Card.Body>
                  <h5 className="mb-3">
                    <i className="fas fa-play-circle me-2 text-primary"></i>
                    ویدیو معرفی دوره
                  </h5>
                  <div 
                    className="ratio ratio-16x9"
                    style={{ position: 'relative', pointerEvents: 'none' }}
                  >
                    <video
                      controls
                      controlsList="nodownload noremoteplayback"
                      disablePictureInPicture
                      style={{ 
                        borderRadius: '10px', 
                        width: '100%', 
                        height: '100%',
                        pointerEvents: 'auto'
                      }}
                      src={course.video_intro}
                      poster={course.thumbnail || undefined}
                    >
                      مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
                    </video>
                  </div>
                </Card.Body>
              </Card>
            )}

            {/* Course Videos Section */}
            {activeVideos.length > 0 && (
              <Card className="mb-4 course-videos-section">
                <Card.Body>
                  <h5 className="mb-3">
                    <i className="fas fa-video me-2 text-primary"></i>
                    ویدیوهای دوره ({activeVideos.length})
                  </h5>
                  <ListGroup variant="flush">
                    {activeVideos.map((video) => (
                      <ListGroup.Item
                        key={video.id}
                        className="d-flex justify-content-between align-items-center py-3"
                        style={{ borderLeft: 'none', borderRight: 'none' }}
                      >
                        <div className="flex-grow-1">
                            <div className="d-flex align-items-center gap-2 mb-1">
                            <h6 className="mb-0">{video.title}</h6>
                            {video.is_preview && (
                              <Badge bg="info" className="ms-2">پیش‌نمایش</Badge>
                            )}
                              {completedVideoIds.includes(video.id) && (
                                <Badge bg="success" className="ms-2">
                                  <i className="fas fa-check me-1"></i>
                                  تکمیل شده
                                </Badge>
                              )}
                          </div>
                          {video.description && (
                            <p className="text-muted small mb-2">{video.description}</p>
                          )}
                          <div className="d-flex align-items-center gap-3 small text-muted">
                            {video.duration_minutes && (
                              <span>
                                <i className="fas fa-clock me-1"></i>
                                {video.duration_minutes} دقیقه
                              </span>
                            )}
                            <span>
                              <i className="fas fa-eye me-1"></i>
                              {video.is_preview ? 'رایگان' : 'نیاز به ثبت‌نام'}
                            </span>
                            {video.attachment_file && (
                              <span>
                                <i className="fas fa-paperclip me-1 text-success"></i>
                                فایل پیوست
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="d-flex gap-2 align-items-center">
                          {video.attachment_file && (video.is_preview || course.enrollment_status.is_enrolled) && (
                            <Button
                              variant="outline-success"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                if (video.attachment_file) {
                                  window.open(video.attachment_file, '_blank');
                                }
                              }}
                              title={video.attachment_file_name || 'دانلود فایل پیوست'}
                            >
                              <i className="fas fa-download me-2"></i>
                              {video.attachment_file_name ? (
                                <span style={{ maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'inline-block' }}>
                                  {video.attachment_file_name.length > 15 
                                    ? video.attachment_file_name.substring(0, 15) + '...' 
                                    : video.attachment_file_name}
                                </span>
                              ) : (
                                'فایل'
                              )}
                            </Button>
                          )}
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handlePlayVideo(video)}
                            disabled={!video.is_preview && !course.enrollment_status.is_enrolled}
                          >
                            <i className="fas fa-play me-2"></i>
                            پخش
                          </Button>
                        </div>
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                  {previewVideos.length === 0 && !course.enrollment_status.is_enrolled && (
                    <Alert variant="info" className="mt-3 mb-0">
                      برای مشاهده ویدیوهای این دوره، لطفاً در دوره ثبت‌نام کنید.
                    </Alert>
                  )}
                </Card.Body>
              </Card>
            )}

            {/* Tabs */}
        <Card>
              <Card.Body>
                <Tabs defaultActiveKey="description" className="mb-3">
                  <Tab eventKey="description" title="توضیحات">
                    <div
                      className="course-description"
                      dangerouslySetInnerHTML={{ __html: course.description }}
                      style={{ lineHeight: '1.8' }}
                    />

                    {course.learning_objectives && (
                      <>
                        <h5 className="mt-4 mb-3">
                          <i className="fas fa-bullseye me-2 text-primary"></i>
                          اهداف یادگیری
                        </h5>
                        <div
                          dangerouslySetInnerHTML={{ __html: course.learning_objectives }}
                          style={{ lineHeight: '1.8' }}
                        />
                      </>
                    )}

                    {course.prerequisites && (
                      <>
                        <h5 className="mt-4 mb-3">
                          <i className="fas fa-list-check me-2 text-primary"></i>
                          پیش‌نیازها
                        </h5>
                        <div
                          dangerouslySetInnerHTML={{ __html: course.prerequisites }}
                          style={{ lineHeight: '1.8' }}
                        />
                      </>
                    )}
                  </Tab>

                  <Tab eventKey="instructor" title="مربی">
                    <div className="text-center py-4">
                      <div className="mb-3">
                        <i className="fas fa-user-circle" style={{ fontSize: '4rem', color: '#2c5aa0' }}></i>
                      </div>
                      <h5>{course.instructor_name}</h5>
                      <p className="text-muted">مربی دوره</p>
                    </div>
                  </Tab>

                  <Tab eventKey="reviews" title={`نظرات (${comments?.length || 0})`}>
                    <div className="py-3">
                      {/* Comment Form */}
                      {isAuthenticated ? (
                        <Card className="mb-4">
                          <Card.Body>
                            <h5 className="mb-3">ثبت نظر جدید</h5>
                            <div className="mb-3">
                              <textarea
                                className="form-control"
                                rows={4}
                                placeholder="نظر خود را در مورد این دوره بنویسید..."
                                value={commentContent}
                                onChange={(e) => setCommentContent(e.target.value)}
                                disabled={createCommentMutation.isPending}
                              />
                            </div>
                            <Button
                              variant="primary"
                              onClick={handleSubmitComment}
                              disabled={createCommentMutation.isPending || !commentContent.trim()}
                            >
                              {createCommentMutation.isPending ? (
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
                          </Card.Body>
                        </Card>
                      ) : (
                        <Alert variant="info" className="mb-4">
                          <i className="fas fa-info-circle me-2"></i>
                          برای ثبت نظر، لطفاً <Link to="/login">وارد حساب کاربری</Link> خود شوید.
                        </Alert>
                      )}

                      {/* Comments List */}
                      {comments.length > 0 ? (
                        <div>
                          <h5 className="mb-3">نظرات کاربران ({comments.length})</h5>
                          {comments.map((comment: any) => (
                            <Card key={comment.id} className="mb-3">
                              <Card.Body>
                                <div className="d-flex justify-content-between align-items-start mb-2">
                                  <div>
                                    <strong>{comment.author_name}</strong>
                                    <small className="text-muted ms-2">
                                      <i className="fas fa-clock me-1"></i>
                                      {comment.created_at_persian || comment.created_at}
                                    </small>
                                  </div>
                                </div>
                                <p className="mb-2" style={{ whiteSpace: 'pre-wrap' }}>
                                  {comment.content}
                                </p>
                                {isAuthenticated && (
                                  <div>
                                    {replyingTo === comment.id ? (
                                      <div className="mt-3 p-3 bg-light rounded">
                                        <textarea
                                          className="form-control mb-2"
                                          rows={3}
                                          placeholder="پاسخ خود را بنویسید..."
                                          value={replyContent}
                                          onChange={(e) => setReplyContent(e.target.value)}
                                          disabled={createCommentMutation.isPending}
                                        />
                                        <div>
                                          <Button
                                            variant="primary"
                                            size="sm"
                                            className="me-2"
                                            onClick={() => handleSubmitReply(comment.id)}
                                            disabled={createCommentMutation.isPending || !replyContent.trim()}
                                          >
                                            {createCommentMutation.isPending ? (
                                              <>
                                                <Spinner size="sm" className="me-2" />
                                                در حال ارسال...
                                              </>
                                            ) : (
                                              'ارسال پاسخ'
                                            )}
                                          </Button>
                                          <Button
                                            variant="outline-secondary"
                                            size="sm"
                                            onClick={() => {
                                              setReplyingTo(null);
                                              setReplyContent('');
                                            }}
                                          >
                                            انصراف
                                          </Button>
                                        </div>
                                      </div>
                                    ) : (
                                      <Button
                                        variant="link"
                                        size="sm"
                                        className="p-0 text-decoration-none"
                                        onClick={() => setReplyingTo(comment.id)}
                                      >
                                        <i className="fas fa-reply me-1"></i>
                                        پاسخ
                                      </Button>
                                    )}
                                  </div>
                                )}
                                {comment.replies_count > 0 && (
                                  <div className="mt-2">
                                    <small className="text-muted">
                                      <i className="fas fa-comments me-1"></i>
                                      {comment.replies_count} پاسخ
                                    </small>
                                  </div>
                                )}
                              </Card.Body>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <Alert variant="info" className="text-center">
                          هنوز نظری برای این دوره ثبت نشده است. اولین نفری باشید که نظر می‌دهد!
                        </Alert>
                      )}
                    </div>
                  </Tab>
                </Tabs>
              </Card.Body>
            </Card>
          </Col>

          {/* Sidebar */}
          <Col lg={4}>
            <div style={{ position: 'sticky', top: '20px' }}>
              {/* Pricing Card */}
              <Card className="mb-4 shadow-sm">
                <Card.Body>
                  {course.is_free ? (
                    <div className="text-center py-3">
                      <h3 className="text-success mb-3">رایگان</h3>
                      {course.enrollment_status.is_enrolled ? (
                        <Button
                          variant="success"
                          size="lg"
                          className="w-100"
                          onClick={handleStartLearning}
                        >
                          <i className="fas fa-play me-2"></i>
                          شروع یادگیری
                        </Button>
                      ) : (
                        <Button
                          variant="success"
                          size="lg"
                          className="w-100"
                          onClick={handleEnroll}
                          disabled={enrollMutation.isPending}
                        >
                          {enrollMutation.isPending ? (
                            <>
                              <Spinner size="sm" className="me-2" />
                              در حال ثبت‌نام...
                            </>
                          ) : (
                            <>
                              <i className="fas fa-user-plus me-2"></i>
                              ثبت‌نام رایگان
                            </>
                          )}
                        </Button>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-3">
                      {course.discount_price && course.discount_price < course.price ? (
                        <div className="mb-3">
                          <small className="text-muted text-decoration-line-through d-block mb-2">
                            {formatPrice(course.price)} تومان
                          </small>
                          <h3 className="text-primary mb-2">
                            {formatPrice(course.discount_price)} تومان
                          </h3>
                          <Badge bg="danger">
                            {course.discount_percentage}% تخفیف
                          </Badge>
                        </div>
                      ) : (
                        <h3 className="text-primary mb-3">
                          {formatPrice(course.current_price)} تومان
                        </h3>
                      )}

                      {course.enrollment_status.is_enrolled ? (
                        <Button
                          variant="success"
                          size="lg"
                          className="w-100 mb-2"
                          onClick={handleStartLearning}
                        >
                          <i className="fas fa-play me-2"></i>
                          شروع یادگیری
                        </Button>
                      ) : (
                        <>
                          <Button
                            variant="primary"
                            size="lg"
                            className="w-100 mb-2"
                            onClick={handlePurchase}
                            disabled={purchaseMutation.isPending}
                          >
                            {purchaseMutation.isPending ? (
                              <>
                                <Spinner size="sm" className="me-2" />
                                در حال پردازش...
                              </>
                            ) : (
                              <>
                                <i className="fas fa-shopping-cart me-2"></i>
                                خرید دوره
                              </>
                            )}
                          </Button>
                          <Button
                            variant="outline-primary"
                            size="lg"
                            className="w-100"
                            onClick={handleAddToCart}
                            disabled={addToCartMutation.isPending}
                          >
                            {addToCartMutation.isPending ? (
                              <>
                                <Spinner size="sm" className="me-2" />
                                در حال افزودن...
                              </>
                            ) : (
                              <>
                                <i className="fas fa-plus me-2"></i>
                                افزودن به سبد خرید
                              </>
                            )}
                          </Button>
                        </>
                      )}
                    </div>
                  )}

                  <hr className="my-4" />

                  {/* Course Info */}
                  <div className="course-info">
                    <div className="d-flex justify-content-between py-2 border-bottom">
                      <span className="text-muted">
                        <i className="fas fa-clock me-2"></i>
                        مدت زمان
                      </span>
                      <strong>{course.duration_hours} ساعت</strong>
                    </div>
                    <div className="d-flex justify-content-between py-2 border-bottom">
                      <span className="text-muted">
                        <i className="fas fa-graduation-cap me-2"></i>
                        سطح
                      </span>
                      <strong>
                        {difficultyInfo?.text || course.level}
                      </strong>
                    </div>
                    <div className="d-flex justify-content-between py-2 border-bottom">
                      <span className="text-muted">
                        <i className="fas fa-video me-2"></i>
                        تعداد ویدیوها
                      </span>
                      <strong>{activeVideos.length}</strong>
                    </div>
                    <div className="d-flex justify-content-between py-2">
                      <span className="text-muted">
                        <i className="fas fa-users me-2"></i>
                        دانشجویان
                      </span>
                      <strong>{course.enrollment_count} نفر</strong>
                    </div>
                  </div>
                </Card.Body>
              </Card>

              {/* Progress Card - Only show if enrolled */}
              {course.enrollment_status.is_enrolled && (
                <Card className="shadow-sm mb-4">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <h6 className="mb-0">
                        <i className="fas fa-chart-line me-2 text-success"></i>
                        پیشرفت بسته آموزشی
                      </h6>
                      <span className="badge bg-success text-white fs-6">
                        {progressPercentage}%
                      </span>
                    </div>
                    <p className="text-muted small mb-3">
                      {completedVideosCount} از {activeVideos.length} ویدیو تماشا شده
                    </p>
                    <div className="progress" style={{ height: '10px' }}>
                      <div 
                        className="progress-bar bg-success" 
                        role="progressbar" 
                        style={{ width: `${progressPercentage}%` }}
                        aria-valuenow={progressPercentage}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      ></div>
                    </div>
                    <div className="mt-3">
                      <div className="d-grid gap-2">
                        <Button
                          variant="outline-success"
                          size="sm"
                          className="w-100"
                          onClick={handleStartLearning}
                        >
                          <i className="fas fa-play me-2"></i>
                          ادامه یادگیری
                        </Button>
                        <Button
                          variant="outline-secondary"
                          size="sm"
                          className="w-100"
                          onClick={() => setCompletedVideoIds([])}
                          disabled={completedVideosCount === 0}
                        >
                          <i className="fas fa-undo me-2"></i>
                          بازنشانی پیشرفت
                        </Button>
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              )}

              {/* Share Card */}
              <Card className="shadow-sm">
                <Card.Body>
                  <h6 className="mb-3">
                    <i className="fas fa-share-alt me-2"></i>
                    اشتراک‌گذاری
                  </h6>
                  <div className="d-flex gap-2">
                    <Button
                      variant="outline-primary"
                      size="sm"
                      className="flex-fill"
                      onClick={() => handleShare('telegram')}
                    >
                      <i className="fab fa-telegram me-1"></i>
                      تلگرام
                    </Button>
                    <Button
                      variant="outline-info"
                      size="sm"
                      className="flex-fill"
                      onClick={() => handleShare('whatsapp')}
                    >
                      <i className="fab fa-whatsapp me-1"></i>
                      واتساپ
                    </Button>
                    <Button
                      variant="outline-secondary"
                      size="sm"
                      className="flex-fill"
                      onClick={() => handleShare('copy')}
                    >
                      <i className="fas fa-link me-1"></i>
                      کپی لینک
                    </Button>
                  </div>
                  {shareStatus && (
                    <Alert
                      variant={shareStatus.type === 'success' ? 'success' : 'danger'}
                      className="mt-3 mb-0 small py-2"
                    >
                      {shareStatus.message}
                    </Alert>
                  )}
          </Card.Body>
        </Card>
            </div>
          </Col>
        </Row>
      </Container>

      {/* Video Modal */}
      <Modal
        show={showVideoModal}
        onHide={() => setShowVideoModal(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>{selectedVideo?.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedVideo && (
            <div 
              className="ratio ratio-16x9"
              style={{ position: 'relative', pointerEvents: 'none' }}
            >
              {selectedVideo.video_url ? (
                <iframe
                  src={selectedVideo.video_url}
                  allowFullScreen
                  style={{ borderRadius: '10px', border: 'none', pointerEvents: 'auto' }}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  sandbox="allow-same-origin allow-scripts allow-presentation"
                ></iframe>
              ) : selectedVideo.video_file ? (
                <video
                  controls
                  controlsList="nodownload noremoteplayback"
                  disablePictureInPicture
                  style={{ 
                    borderRadius: '10px', 
                    width: '100%', 
                    height: '100%', 
                    pointerEvents: 'auto',
                    outline: 'none'
                  }}
                  src={selectedVideo.video_file}
                  onEnded={() => handleAutoCompleteVideo(selectedVideo.id)}
                >
                  مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
                </video>
              ) : (
                <Alert variant="warning">ویدیو در دسترس نیست</Alert>
              )}
            </div>
          )}
          {selectedVideo && (
            <div className="mt-3 d-flex justify-content-between align-items-center">
              <div className="text-muted small">
                {completedVideoIds.includes(selectedVideo.id)
                  ? 'این ویدیو تکمیل شده علامت خورده است.'
                  : 'هنوز این ویدیو را به عنوان تکمیل شده علامت نزده‌اید.'}
              </div>
              <div className="d-flex gap-2">
                <Button
                  variant={completedVideoIds.includes(selectedVideo.id) ? 'outline-success' : 'success'}
                  onClick={() => handleToggleVideoCompletion(selectedVideo.id)}
                  size="sm"
                >
                  {completedVideoIds.includes(selectedVideo.id) ? (
                    <>
                      <i className="fas fa-undo me-2"></i>
                      علامت‌گذاری دوباره
                    </>
                  ) : (
                    <>
                      <i className="fas fa-check me-2"></i>
                      علامت به عنوان تکمیل شده
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
          {selectedVideo?.description && (
            <p className="mt-3" style={{ userSelect: 'text' }}>{selectedVideo.description}</p>
          )}
          {selectedVideo?.attachment_file && (
            <div className="mt-3 pt-3" style={{ borderTop: '1px solid #e9ecef' }}>
              <div className="d-flex align-items-center justify-content-between">
                <div>
                  <h6 className="mb-1">
                    <i className="fas fa-paperclip text-primary me-2"></i>
                    فایل پیوست
                  </h6>
                  {selectedVideo.attachment_file_name && (
                    <small className="text-muted">
                      {selectedVideo.attachment_file_name}
                      {selectedVideo.attachment_file_size && ` (${selectedVideo.attachment_file_size})`}
                    </small>
                  )}
                </div>
                <Button
                  variant="success"
                  size="sm"
                  onClick={() => {
                    if (selectedVideo.attachment_file) {
                      window.open(selectedVideo.attachment_file, '_blank');
                    }
                  }}
                >
                  <i className="fas fa-download me-2"></i>
                  دانلود فایل
                </Button>
              </div>
            </div>
          )}
        </Modal.Body>
      </Modal>
    </>
  );
};

export default CourseDetail;
