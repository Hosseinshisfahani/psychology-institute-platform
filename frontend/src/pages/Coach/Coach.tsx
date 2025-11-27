import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Alert, Button, Card, Col, Container, Form, ListGroup, Row, Spinner } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import './Coach.css';

interface ContactFormState {
  fullName: string;
  phone: string;
  topic: string;
  message: string;
}

interface ChatMessage {
  id: number;
  message: string;
  is_from_admin: boolean;
  created_at: string;
  sender_name: string;
  attachment?: string;
  attachment_name?: string;
}

interface ChatThread {
  id: number;
  assigned_admin_name: string | null;
  messages: ChatMessage[];
}


const initialFormState: ContactFormState = {
  fullName: '',
  phone: '',
  topic: '',
  message: '',
};

const Coach: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [form, setForm] = useState<ContactFormState>(initialFormState);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chatThread, setChatThread] = useState<ChatThread | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [chatInput, setChatInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!form.fullName.trim() || !form.phone.trim() || !form.topic.trim()) {
      setError('لطفاً نام، شماره تماس و موضوع درخواست را وارد کنید.');
      setSubmitted(false);
      return;
    }

    setError(null);
    setSubmitted(true);
    setForm(initialFormState);
  };

  const fetchThread = useCallback(async () => {
    if (!isAuthenticated) {
      return;
    }

    try {
      const response = await axios.get<ChatThread>('/api/chat/thread/');
      setChatThread(response.data);
      setChatMessages(response.data.messages || []);
      setChatError(null);
    } catch (err) {
      setChatError('امکان بارگذاری گفتگو وجود ندارد. لطفاً دوباره تلاش کنید.');
    } finally {
      setChatLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      setChatThread(null);
      setChatMessages([]);
      return;
    }

    setChatLoading(true);
    fetchThread();
    const interval = setInterval(fetchThread, 15000);

    return () => clearInterval(interval);
  }, [isAuthenticated, fetchThread]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file size (5MB limit)
      if (file.size > 5 * 1024 * 1024) {
        setChatError('حجم فایل نباید بیشتر از ۵ مگابایت باشد.');
        return;
      }
      setSelectedFile(file);
      // Create preview for images
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setFilePreview(reader.result as string);
        };
        reader.readAsDataURL(file);
      } else {
        setFilePreview(null);
      }
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setFilePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleChatSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = chatInput.trim();
    if (!trimmed && !selectedFile) {
      return;
    }

    try {
      const formData = new FormData();
      formData.append('message', trimmed || '');
      if (selectedFile) {
        formData.append('attachment', selectedFile);
      }

      const response = await axios.post<ChatMessage>('/api/chat/message/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setChatMessages((prev) => [...prev, response.data]);
      setChatThread((prev) =>
        prev
          ? {
              ...prev,
              messages: [...prev.messages, response.data],
            }
          : prev
      );
      setChatInput('');
      setSelectedFile(null);
      setFilePreview(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setChatError(null);
    } catch (err) {
      setChatError('امکان ارسال پیام وجود ندارد. لطفاً دوباره تلاش کنید.');
    }
  };

  return (
    <>
      <Helmet>
        <title>ارتباط با ادمین - مرکز روانشناسی امامی</title>
        <meta
          name="description"
          content="در ارتباط با ادمین مرکز روانشناسی امامی می‌توانید درخواست خود را ثبت یا جلسه مشاوره رزرو کنید."
        />
      </Helmet>

      <div className="coach-page">
        <section className="coach-hero">
          <Container>
            <Row className="align-items-center g-4 justify-content-center">
              <Col lg={8} xl={7} className="coach-hero-content text-center text-lg-start">
                <span className="coach-hero-badge">پشتیبانی کاربران</span>
                <h1 className="coach-hero-title">همیشه در کنار شما؛ ارتباط مستقیم با کلینیک</h1>
                <p className="coach-hero-subtitle">
                  تنها در چند دقیقه می‌توانید با تیم پشتیبانی در ارتباط باشید یا برای جلسه مشاوره اختصاصی اقدام کنید.
                </p>

                <div className="d-flex flex-wrap gap-3 mt-4">
                  <Link to="/therapists" className="btn btn-primary btn-lg d-flex align-items-center gap-3">
                    <i className="fas fa-calendar-alt"></i>
                    <span>رزرو مشاوره</span>
                  </Link>
                  <a href="#live-chat" className="btn btn-outline-primary btn-lg d-flex align-items-center gap-3">
                    <i className="fas fa-comments"></i>
                    <span>گفت‌وگو با ادمین</span>
                  </a>
                </div>
              </Col>
            </Row>
          </Container>
        </section>

        <section className="coach-chat" id="live-chat">
          <Container>
            <Row className="g-4 align-items-stretch">
              <Col lg={7}>
                <Card className="coach-chat-card shadow-sm h-100">
                  <div className="coach-chat-header">
                    <div className="coach-chat-header-main">
                      <div className="coach-chat-header-icon">
                        <i className="fas fa-comments"></i>
                      </div>
                      <div>
                        <h4 className="coach-chat-header-title mb-1">ارتباط با کلینیک</h4>
                        <p className="coach-chat-header-text mb-0">
                          پشتیبانی قدم‌به‌قدم و پاسخ سریع در ساعات اداری.
                        </p>
                      </div>
                    </div>
                    <div className="coach-chat-header-tags">
                      <span className="coach-chat-header-tag d-flex align-items-center gap-3">
                        <i className="fas fa-shield-alt"></i>
                        <span>گفتگوها محرمانه‌اند</span>
                      </span>
                    </div>
                  </div>
                  <Card.Body className="d-flex flex-column">
                    <div className="coach-chat-meta-bar mb-3">
                      <div className="coach-chat-meta">
                        <span className="coach-chat-meta-label">وضعیت</span>
                        <span className="coach-chat-meta-value">
                          <span className="coach-online-dot"></span>
                          آنلاین
                        </span>
                      </div>
                      <div className="coach-chat-meta">
                        <span className="coach-chat-meta-label">ادمین مسئول</span>
                        <span className="coach-chat-meta-value">
                          {chatThread?.assigned_admin_name
                            ? chatThread.assigned_admin_name
                            : 'اولین ادمین آزاد پاسخ می‌دهد'}
                        </span>
                      </div>
                      <div className="coach-chat-meta">
                        <span className="coach-chat-meta-label">به‌روزرسانی</span>
                        <span className="coach-chat-meta-value">هر ۱۵ ثانیه</span>
                      </div>
                    </div>

                    {chatError && (
                      <Alert variant="danger" onClose={() => setChatError(null)} dismissible>
                        {chatError}
                      </Alert>
                    )}

                    {!isAuthenticated ? (
                      <div className="coach-chat-placeholder flex-grow-1 d-flex flex-column align-items-center justify-content-center text-center">
                        <i className="fas fa-lock mb-3 fa-2x text-primary"></i>
                        <p className="text-muted mb-3">برای شروع گفت‌وگو لازم است وارد حساب کاربری خود شوید.</p>
                        <div className="d-flex gap-2">
                          <Link to="/login" className="btn btn-primary">
                            ورود به حساب
                          </Link>
                          <Link to="/signup" className="btn btn-outline-primary">
                            ثبت‌نام سریع
                          </Link>
                        </div>
                      </div>
                    ) : (
                      <>
                    <div className="coach-chat-window flex-grow-1">
                          {chatLoading ? (
                            <div className="coach-chat-loader">
                              <Spinner animation="border" variant="primary" />
                            </div>
                          ) : chatMessages.length === 0 ? (
                            <div className="coach-chat-empty text-center text-muted">
                              <i className="fas fa-comments fa-2x mb-3"></i>
                              <p className="mb-0">برای شروع گفتگو پیام خود را ارسال کنید.</p>
                            </div>
                          ) : (
                            <div className="coach-chat-messages">
                        {chatMessages.map((message) => (
                                <div
                            key={message.id}
                            className={`coach-chat-message ${
                                    message.is_from_admin ? 'coach-chat-message-admin' : 'coach-chat-message-user'
                            }`}
                          >
                            <div className="d-flex align-items-center justify-content-between mb-1">
                                    <span className="fw-semibold" style={{ color: message.is_from_admin ? '#1f2f4d' : '#ffffff' }}>{message.sender_name}</span>
                                    <small style={{ color: message.is_from_admin ? '#6a7a95' : 'rgba(255, 255, 255, 0.8)' }}>
                                      {new Date(message.created_at).toLocaleTimeString('fa-IR', {
                                        hour: '2-digit',
                                        minute: '2-digit',
                                      })}
                                    </small>
                              </div>
                                  {message.message && <div style={{ color: message.is_from_admin ? '#1f2f4d' : '#ffffff' }}>{message.message}</div>}
                                  {message.attachment && (
                                    <div className="mt-2">
                                      <a 
                                        href={message.attachment} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="d-inline-flex align-items-center gap-2 text-decoration-none"
                                        style={{ color: message.is_from_admin ? '#2c5aa0' : '#ffffff' }}
                                      >
                                        <i className="fas fa-paperclip"></i>
                                        <span>{message.attachment_name || 'فایل پیوست'}</span>
                                        <i className="fas fa-external-link-alt"></i>
                                      </a>
                                    </div>
                                  )}
                            </div>
                              ))}
                              <div ref={messagesEndRef}></div>
                            </div>
                        )}
                    </div>

                        <Form onSubmit={handleChatSubmit} className="coach-chat-form mt-3">
                        {filePreview && (
                          <div className="mb-2 position-relative" style={{ maxWidth: '200px' }}>
                            <img 
                              src={filePreview} 
                              alt="Preview" 
                              className="img-thumbnail"
                              style={{ maxHeight: '100px', width: 'auto' }}
                            />
                            <button
                              type="button"
                              className="btn btn-sm btn-danger position-absolute top-0 start-0 m-1"
                              onClick={removeFile}
                              style={{ padding: '0.25rem 0.5rem' }}
                            >
                              <i className="fas fa-times"></i>
                            </button>
                          </div>
                        )}
                        {selectedFile && !filePreview && (
                          <div className="mb-2 d-flex align-items-center gap-2">
                            <span className="badge bg-secondary">
                              <i className="fas fa-paperclip me-2"></i>
                              {selectedFile.name}
                            </span>
                            <button
                              type="button"
                              className="btn btn-sm btn-link text-danger p-0"
                              onClick={removeFile}
                            >
                              <i className="fas fa-times"></i>
                            </button>
                          </div>
                        )}
                        <Form.Control
                            as="textarea"
                            rows={2}
                            placeholder="پیام خود را بنویسید..."
                            value={chatInput}
                            onChange={(event) => setChatInput(event.target.value)}
                          />
                          <div className="d-flex justify-content-between align-items-center mt-2 flex-wrap gap-2">
                            <div>
                              <input
                                ref={fileInputRef}
                                type="file"
                                id="chat-file-input"
                                className="d-none"
                                onChange={handleFileSelect}
                                accept="image/*,.pdf,.doc,.docx"
                              />
                              <label 
                                htmlFor="chat-file-input" 
                                className="btn btn-outline-secondary btn-sm mb-0"
                                style={{ cursor: 'pointer' }}
                              >
                                <i className="fas fa-paperclip me-2"></i>
                                پیوست
                              </label>
                            </div>
                            <Button 
                              type="submit" 
                              disabled={!chatInput.trim() && !selectedFile} 
                              className="d-flex align-items-center gap-3"
                            >
                              <span>ارسال پیام</span>
                          <i className="fas fa-paper-plane"></i>
                        </Button>
                      </div>
                    </Form>
                      </>
                    )}
                  </Card.Body>
                </Card>
              </Col>
              <Col lg={5}>
                <Card className="coach-chat-sidecard shadow-sm h-100 coach-expectation-card">
                  <div className="coach-expectation-header">
                    <div className="coach-expectation-header-main">
                      <div className="coach-expectation-icon">
                        <i className="fas fa-seedling"></i>
                      </div>
                      <div>
                        <h5 className="coach-expectation-title mb-1">چه انتظاری داشته باشم؟</h5>
                        <p className="coach-expectation-subtitle mb-0">
                          تصویری کوتاه از مسیری که پس از ارسال پیام تا دریافت پاسخ طی می‌کنید.
                        </p>
                        <span className="coach-expectation-badge mt-3 d-inline-block">همراهی گام‌به‌گام</span>
                      </div>
                    </div>
                  </div>
                  <Card.Body>
                    <ListGroup variant="flush" className="coach-chat-side-list coach-expectation-list">
                      <ListGroup.Item className="coach-expectation-item">
                        <div className="coach-expectation-step">
                          <span className="coach-expectation-step-icon">
                            <i className="fas fa-clock"></i>
                          </span>
                          <div>
                            <div className="coach-expectation-item-title">پاسخ اولیه سریع</div>
                            <p className="coach-expectation-item-text mb-0">
                              پاسخ اولیه در ساعات اداری به سرعت و بدون تأخیر دریافت می‌کنید.
                            </p>
                          </div>
                        </div>
                        <span className="coach-expectation-meta">پاسخ سریع</span>
                      </ListGroup.Item>
                      <ListGroup.Item className="coach-expectation-item">
                        <div className="coach-expectation-step">
                          <span className="coach-expectation-step-icon">
                            <i className="fas fa-user-shield"></i>
                          </span>
                          <div>
                            <div className="coach-expectation-item-title">حریم خصوصی کامل</div>
                            <p className="coach-expectation-item-text mb-0">
                              تنها ادمین‌های موسسه به پیام‌های شما دسترسی دارند.
                            </p>
                          </div>
                        </div>
                        <span className="coach-expectation-meta">دسترسی محدود</span>
                      </ListGroup.Item>
                      <ListGroup.Item className="coach-expectation-item">
                        <div className="coach-expectation-step">
                          <span className="coach-expectation-step-icon">
                            <i className="fas fa-file-alt"></i>
                          </span>
                          <div>
                            <div className="coach-expectation-item-title">سوابق همیشه در دسترس</div>
                            <p className="coach-expectation-item-text mb-0">
                              سابقه گفتگو برای پیگیری‌های بعدی ذخیره می‌شود.
                            </p>
                          </div>
                        </div>
                        <span className="coach-expectation-meta">پیگیری آسان</span>
                      </ListGroup.Item>
                    </ListGroup>

                    <div className="coach-expectation-progress mt-4">
                      <div className="coach-expectation-progress-track">
                        <span className="coach-expectation-progress-node">ارسال پیام</span>
                        <span className="coach-expectation-progress-node">هماهنگی ادمین</span>
                        <span className="coach-expectation-progress-node">پیگیری نهایی</span>
                      </div>
                    </div>

                    <div className="coach-chat-tip coach-expectation-tip mt-4">
                      <div className="coach-expectation-tip-icon">
                        <i className="fas fa-info-circle"></i>
                      </div>
                      <div>
                        <div className="fw-semibold mb-1">نیاز فوری دارید؟</div>
                        <div>اگر نیاز فوری دارید، می‌توانید با شماره <span dir="ltr">۰۳۱-۳۲۲۹۶۳۱۲</span> تماس بگیرید.</div>
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Container>
        </section>

        <section className="coach-contact">
          <Container>
            <Row className="g-4 align-items-stretch justify-content-center">
              <Col lg={6}>
                <Card className="coach-contact-card shadow-sm h-100 coach-contact-enhanced">
                  <div className="coach-contact-header">
                    <div className="coach-contact-icon">
                      <i className="fas fa-headset"></i>
                    </div>
                    <div>
                      <span className="coach-contact-badge">تماس مستقیم</span>
                      <h4 className="coach-contact-title mb-1">راه‌های ارتباطی مستقیم</h4>
                      <p className="coach-contact-subtitle mb-0">
                        تیم پشتیبانی سرمد کلینیک در ساعات اداری کنار شماست؛ خارج از این ساعات، اولین فرصت کاری پاسخگو هستیم.
                      </p>
                    </div>
                  </div>

                  <Card.Body>
                    <ListGroup variant="flush" className="coach-contact-list mb-4">
                      <ListGroup.Item className="coach-contact-item">
                        <span className="coach-contact-item-icon">
                          <i className="fas fa-map-marker-alt"></i>
                        </span>
                        <div>
                          <div className="coach-contact-item-label">آدرس کلینیک</div>
                          <p className="coach-contact-item-text mb-0">
                            اصفهان، میدان احمدآباد، ابتدای خیابان ولیعصر، جنب بانک مسکن، ساختمان پزشکی، طبقه اول
                          </p>
                        </div>
                      </ListGroup.Item>
                      <ListGroup.Item className="coach-contact-item">
                        <span className="coach-contact-item-icon">
                          <i className="fas fa-phone"></i>
                        </span>
                        <div>
                          <div className="coach-contact-item-label">شماره‌های ثابت</div>
                          <p className="coach-contact-item-text mb-0"><span dir="ltr">۰۳۱-۳۲۲۹۶۳۱۲ | ۰۳۱-۳۲۲۹۲۷۹۷</span></p>
                        </div>
                      </ListGroup.Item>
                      <ListGroup.Item className="coach-contact-item">
                        <span className="coach-contact-item-icon">
                          <i className="fas fa-mobile-alt"></i>
                        </span>
                        <div>
                          <div className="coach-contact-item-label">شماره‌های همراه</div>
                          <p className="coach-contact-item-text mb-0"><span dir="ltr">۰۹۳۸۳۸۲۱۱۰۰ | ۰۹۰۵۳۰۰۰۲۱۳ | ۰۹۱۹۰۹۱۹۹۵۰</span></p>
                        </div>
                      </ListGroup.Item>
                      <ListGroup.Item className="coach-contact-item">
                        <span className="coach-contact-item-icon">
                          <i className="fas fa-envelope"></i>
                        </span>
                        <div>
                          <div className="coach-contact-item-label">ایمیل</div>
                          <p className="coach-contact-item-text mb-0">info@sarmadclinic.ir</p>
                        </div>
                      </ListGroup.Item>
                    </ListGroup>

                    <div className="coach-contact-actions mb-4">
                      <a href="tel:03132296312" className="coach-contact-action d-flex align-items-center gap-3">
                        <i className="fas fa-phone-alt"></i>
                        <span>تماس تلفنی</span>
                      </a>
                      <a href="mailto:info@sarmadclinic.ir" className="coach-contact-action coach-contact-action-outline d-flex align-items-center gap-3">
                        <i className="fas fa-envelope-open-text"></i>
                        <span>ارسال ایمیل</span>
                      </a>
                    </div>

                    <div className="coach-contact-note coach-contact-tip">
                      <div className="coach-contact-tip-icon">
                        <i className="fas fa-info-circle"></i>
                      </div>
                      <div>
                        <div className="fw-semibold mb-1">همراه شما تا پایان مسیر درمان</div>
                        <div>پس از هر جلسه، پیگیری و پشتیبانی تا رسیدن به نتیجه مطلوب ادامه خواهد داشت.</div>
                      </div>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Container>
        </section>

      </div>
    </>
  );
};

export default Coach;
