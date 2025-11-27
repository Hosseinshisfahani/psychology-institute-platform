import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, ProgressBar, Alert, Form } from 'react-bootstrap';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

interface Question {
  id: number;
  text: string;
  question_type: 'multiple_choice' | 'scale' | 'text';
  choices?: string[];
  scale_min?: number;
  scale_max?: number;
  required: boolean;
}

interface TestSession {
  id: number;
  test: {
    id: number;
    title: string;
    description: string;
    time_limit?: number;
    questions_count: number;
  };
  questions: Question[];
  start_time: string;
  time_remaining?: number;
}

const TestSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  // Fetch test session
  const { data: session, isLoading } = useQuery<TestSession>({
    queryKey: ['test-session', sessionId],
    queryFn: async () => {
      const response = await axios.get(`/api/tests/session/${sessionId}/`);
      return response.data;
    },
    enabled: !!sessionId,
  });

  // Submit answer mutation
  const submitAnswerMutation = useMutation({
    mutationFn: async ({ questionId, answer }: { questionId: number; answer: any }) => {
      await axios.post(`/api/tests/session/${sessionId}/answer/`, {
        question_id: questionId,
        answer: answer
      });
    },
  });

  // Submit test mutation
  const submitTestMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.post(`/api/tests/session/${sessionId}/submit/`, { answers });
      return response.data;
    },
    onSuccess: (data) => {
      navigate(`/tests/result/${data.result_id}`);
    },
  });

  // Timer effect
  useEffect(() => {
    if (session?.time_remaining) {
      setTimeRemaining(session.time_remaining);
      
      const timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev && prev <= 1) {
            clearInterval(timer);
            submitTestMutation.mutate();
            return 0;
          }
          return prev ? prev - 1 : 0;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [session, submitTestMutation]);

  const handleAnswerChange = (questionId: number, answer: any) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
    submitAnswerMutation.mutate({ questionId, answer });
  };

  const goToNextQuestion = () => {
    if (session && currentQuestionIndex < session.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getCurrentQuestion = () => session?.questions[currentQuestionIndex];
  const progress = session ? ((currentQuestionIndex + 1) / session.questions.length) * 100 : 0;

  if (isLoading) {
    return (
      <Container className="py-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">در حال بارگذاری...</span>
          </div>
        </div>
      </Container>
    );
  }

  if (!session) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          جلسه تست یافت نشد یا منقضی شده است.
        </Alert>
      </Container>
    );
  }

  const currentQuestion = getCurrentQuestion();

  return (
    <>
      <Helmet>
        <title>تست: {session.test.title}</title>
      </Helmet>

      <Container fluid className="test-session-container">
        <Row className="h-100">
          {/* Main Content */}
          <Col lg={9} className="test-content">
            <Card className="h-100">
              <Card.Header className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="mb-0">{session.test.title}</h5>
                  <small className="text-muted">
                    سوال {currentQuestionIndex + 1} از {session.questions.length}
                  </small>
                </div>
                
                {timeRemaining && (
                  <div className="text-center">
                    <div className="fs-4 fw-bold text-danger">
                      {formatTime(timeRemaining)}
                    </div>
                    <small className="text-muted">زمان باقی‌مانده</small>
                  </div>
                )}
              </Card.Header>
              
              <Card.Body className="d-flex flex-column">
                {/* Progress */}
                <div className="mb-4">
                  <ProgressBar now={progress} className="mb-2" />
                  <div className="d-flex justify-content-between text-muted small">
                    <span>پیشرفت تست</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                </div>

                {/* Question */}
                {currentQuestion && (
                  <div className="flex-grow-1 d-flex flex-column">
                    <div className="question-content flex-grow-1">
                      <h4 className="mb-4">{currentQuestion.text}</h4>
                      
                      {/* Multiple Choice */}
                      {currentQuestion.question_type === 'multiple_choice' && currentQuestion.choices && (
                        <div className="choices">
                          {currentQuestion.choices.map((choice, index) => (
                            <Form.Check
                              key={index}
                              type="radio"
                              name={`question-${currentQuestion.id}`}
                              id={`choice-${index}`}
                              label={choice}
                              checked={answers[currentQuestion.id] === choice}
                              onChange={() => handleAnswerChange(currentQuestion.id, choice)}
                              className="mb-3 p-3 border rounded choice-option"
                            />
                          ))}
                        </div>
                      )}

                      {/* Scale */}
                      {currentQuestion.question_type === 'scale' && (
                        <div className="scale-container">
                          <div className="d-flex justify-content-between mb-3">
                            <span>کاملاً مخالفم</span>
                            <span>کاملاً موافقم</span>
                          </div>
                          
                          <div className="d-flex justify-content-between">
                            {Array.from({ length: (currentQuestion.scale_max || 5) - (currentQuestion.scale_min || 1) + 1 }, (_, i) => {
                              const value = (currentQuestion.scale_min || 1) + i;
                              return (
                                <Form.Check
                                  key={value}
                                  type="radio"
                                  name={`scale-${currentQuestion.id}`}
                                  id={`scale-${value}`}
                                  label={value.toString()}
                                  checked={answers[currentQuestion.id] === value}
                                  onChange={() => handleAnswerChange(currentQuestion.id, value)}
                                  className="text-center scale-option"
                                />
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Text */}
                      {currentQuestion.question_type === 'text' && (
                        <Form.Group>
                          <Form.Control
                            as="textarea"
                            rows={4}
                            value={answers[currentQuestion.id] || ''}
                            onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                            placeholder="پاسخ خود را بنویسید..."
                          />
                        </Form.Group>
                      )}
                    </div>

                    {/* Navigation */}
                    <div className="question-navigation d-flex justify-content-between mt-4">
                      <Button
                        variant="outline-secondary"
                        onClick={goToPreviousQuestion}
                        disabled={currentQuestionIndex === 0}
                      >
                        <i className="fas fa-chevron-right me-2"></i>
                        قبلی
                      </Button>
                      
                      {currentQuestionIndex === session.questions.length - 1 ? (
                        <Button
                          variant="success"
                          onClick={() => submitTestMutation.mutate()}
                          disabled={submitTestMutation.isPending}
                        >
                          {submitTestMutation.isPending ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2"></span>
                              در حال ارسال...
                            </>
                          ) : (
                            <>
                              <i className="fas fa-check me-2"></i>
                              اتمام تست
                            </>
                          )}
                        </Button>
                      ) : (
                        <Button
                          variant="primary"
                          onClick={goToNextQuestion}
                        >
                          بعدی
                          <i className="fas fa-chevron-left ms-2"></i>
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>

          {/* Sidebar */}
          <Col lg={3} className="test-sidebar">
            <Card>
              <Card.Header>
                <h6 className="mb-0">نقشه سوالات</h6>
              </Card.Header>
              <Card.Body>
                <div className="question-map">
                  {session.questions.map((_, index) => (
                    <Button
                      key={index}
                      variant={
                        index === currentQuestionIndex ? 'primary' :
                        answers[session.questions[index].id] ? 'success' : 'outline-secondary'
                      }
                      size="sm"
                      className="m-1"
                      onClick={() => setCurrentQuestionIndex(index)}
                      style={{ width: '40px', height: '40px' }}
                    >
                      {index + 1}
                    </Button>
                  ))}
                </div>
                
                <div className="mt-3">
                  <div className="d-flex align-items-center mb-2">
                    <div className="bg-success rounded me-2" style={{ width: '12px', height: '12px' }}></div>
                    <small>پاسخ داده شده</small>
                  </div>
                  <div className="d-flex align-items-center mb-2">
                    <div className="bg-primary rounded me-2" style={{ width: '12px', height: '12px' }}></div>
                    <small>سوال فعلی</small>
                  </div>
                  <div className="d-flex align-items-center">
                    <div className="border rounded me-2" style={{ width: '12px', height: '12px' }}></div>
                    <small>پاسخ داده نشده</small>
                  </div>
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      <style>{`
        .test-session-container {
          min-height: 100vh;
          background-color: #f8f9fa;
          padding: 20px 0;
        }
        
        .choice-option:hover {
          background-color: #f8f9fa;
          cursor: pointer;
        }
        
        .choice-option input[type="radio"]:checked + label {
          color: #007bff;
          font-weight: 500;
        }
        
        .scale-option {
          flex-direction: column;
          align-items: center;
        }
        
        .question-map {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
        
        @media (max-width: 768px) {
          .test-sidebar {
            order: -1;
            margin-bottom: 20px;
          }
        }
      `}</style>
    </>
  );
};

export default TestSession;
