import React from 'react';
import { Card, Badge, Button, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { Course } from '../../types/Course';

interface CourseCardProps {
  course: Course;
  onAddToCart?: (course: Course) => void;
}

const CourseCard: React.FC<CourseCardProps> = ({ course, onAddToCart }) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fa-IR').format(price);
  };

  const getDifficultyBadge = (difficulty: string) => {
    const difficultyMap = {
      'beginner': { text: 'مبتدی', variant: 'success', icon: 'fa-seedling' },
      'intermediate': { text: 'متوسط', variant: 'warning', icon: 'fa-chart-line' },
      'advanced': { text: 'پیشرفته', variant: 'danger', icon: 'fa-trophy' }
    };
    return difficultyMap[difficulty as keyof typeof difficultyMap] || { 
      text: difficulty, 
      variant: 'secondary', 
      icon: 'fa-circle' 
    };
  };

  const difficultyInfo = getDifficultyBadge(course.difficulty);

  return (
    <Card 
      className="h-100 shadow-sm"
      style={{
        border: 'none',
        borderRadius: '20px',
        overflow: 'hidden',
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        cursor: 'pointer',
        position: 'relative'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-8px) scale(1.02)';
        e.currentTarget.style.boxShadow = '0 20px 40px rgba(44, 90, 160, 0.15)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0) scale(1)';
        e.currentTarget.style.boxShadow = '0 2px 10px rgba(0,0,0,0.08)';
      }}
    >
      {/* Image Container with Overlay */}
      <div style={{ position: 'relative', overflow: 'hidden' }}>
        {course.thumbnail ? (
          <>
            <Card.Img
              variant="top"
              src={course.thumbnail}
              alt={course.title}
              loading="lazy"
              style={{ 
                height: '220px', 
                objectFit: 'cover',
                transition: 'transform 0.4s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
              }}
            />
            {/* Gradient Overlay */}
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: '60%',
                background: 'linear-gradient(to top, rgba(0,0,0,0.4), transparent)',
                pointerEvents: 'none'
              }}
            />
          </>
        ) : (
          <div
            style={{
              height: '220px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <i className="fas fa-graduation-cap" style={{ fontSize: '4rem', color: 'white', opacity: 0.5 }}></i>
          </div>
        )}
        
        {/* Badges Overlay */}
        <div 
          style={{ 
            position: 'absolute', 
            top: '15px', 
            right: '15px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            zIndex: 2
          }}
        >
          {course.is_free && (
            <Badge 
              bg="success" 
              style={{ 
                fontSize: '0.75rem', 
                padding: '0.5rem 0.75rem',
                borderRadius: '20px',
                fontWeight: 600,
                boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
              }}
            >
              <i className="fas fa-gift me-1"></i>
              رایگان
            </Badge>
          )}
          {course.discount_percentage > 0 && (
            <Badge 
              bg="danger" 
              style={{ 
                fontSize: '0.75rem', 
                padding: '0.5rem 0.75rem',
                borderRadius: '20px',
                fontWeight: 600,
                boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
              }}
            >
              <i className="fas fa-percent me-1"></i>
              {course.discount_percentage}% تخفیف
            </Badge>
          )}
        </div>
      </div>
      
      <Card.Body className="d-flex flex-column p-4">
        {/* Category and Difficulty */}
        <div className="mb-3 d-flex flex-wrap gap-2">
          <Badge 
            bg="info" 
            style={{ 
              fontSize: '0.75rem', 
              padding: '0.4rem 0.8rem',
              borderRadius: '15px',
              fontWeight: 500
            }}
          >
            <i className="fas fa-folder me-1"></i>
            {course.category_name}
          </Badge>
          <Badge 
            bg={difficultyInfo.variant as any}
            style={{ 
              fontSize: '0.75rem', 
              padding: '0.4rem 0.8rem',
              borderRadius: '15px',
              fontWeight: 500
            }}
          >
            <i className={`fas ${difficultyInfo.icon} me-1`}></i>
            {difficultyInfo.text}
          </Badge>
        </div>

        {/* Title */}
        <Card.Title 
          className="mb-2" 
          style={{ 
            fontSize: '1.2rem', 
            fontWeight: 700,
            lineHeight: '1.4',
            minHeight: '3.5rem',
            color: '#2c3e50'
          }}
        >
          {course.title}
        </Card.Title>
        
        {/* Description */}
        <Card.Text 
          className="text-muted mb-3" 
          style={{ 
            fontSize: '0.9rem', 
            lineHeight: '1.7',
            minHeight: '3.5rem',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}
        >
          {course.short_description}
        </Card.Text>

        {/* Course Info */}
        <div className="mb-3 pb-3" style={{ borderBottom: '1px solid #e9ecef' }}>
          <Row className="g-2">
            <Col xs={6}>
              <div className="d-flex align-items-center gap-2">
                <div 
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: '#e7f3ff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <i className="fas fa-user text-primary" style={{ fontSize: '0.8rem' }}></i>
                </div>
                <div>
                  <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>مدرس</small>
                  <small className="fw-semibold d-block" style={{ fontSize: '0.85rem' }}>
                    {course.instructor_name}
                  </small>
                </div>
              </div>
            </Col>
            <Col xs={6}>
              <div className="d-flex align-items-center gap-2">
                <div 
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: '#fff4e6',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <i className="fas fa-clock text-warning" style={{ fontSize: '0.8rem' }}></i>
                </div>
                <div>
                  <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>مدت زمان</small>
                  <small className="fw-semibold d-block" style={{ fontSize: '0.85rem' }}>
                    {course.duration_hours} ساعت
                  </small>
                </div>
              </div>
            </Col>
          </Row>
          
          <Row className="g-2 mt-2">
            <Col xs={6}>
              <div className="d-flex align-items-center gap-2">
                <div 
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: '#f0f9ff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <i className="fas fa-users text-info" style={{ fontSize: '0.8rem' }}></i>
                </div>
                <div>
                  <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>دانشجویان</small>
                  <small className="fw-semibold d-block" style={{ fontSize: '0.85rem' }}>
                    {course.enrollment_count} نفر
                  </small>
                </div>
              </div>
            </Col>
            <Col xs={6}>
              {course.rating > 0 && (
                <div className="d-flex align-items-center gap-2">
                  <div 
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      background: '#fffbf0',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <i className="fas fa-star text-warning" style={{ fontSize: '0.8rem' }}></i>
                  </div>
                  <div>
                    <small className="text-muted d-block" style={{ fontSize: '0.7rem' }}>امتیاز</small>
                    <small className="fw-semibold d-block" style={{ fontSize: '0.85rem' }}>
                      {course.rating.toFixed(1)} ⭐
                    </small>
                  </div>
                </div>
              )}
            </Col>
          </Row>
        </div>

        {/* Price and Actions */}
        <div className="mt-auto">
          <div className="d-flex justify-content-between align-items-center mb-3">
            {course.is_free ? (
              <div>
                <span className="h4 text-success mb-0 fw-bold">رایگان</span>
              </div>
            ) : (
              <div>
                {course.discount_price && course.discount_price < course.price ? (
                  <div>
                    <div className="d-flex align-items-baseline gap-2">
                      <span className="h4 text-primary mb-0 fw-bold">
                        {formatPrice(course.discount_price)} تومان
                      </span>
                    </div>
                    <div className="d-flex align-items-center gap-2 mt-1">
                      <small className="text-muted text-decoration-line-through" style={{ fontSize: '0.85rem' }}>
                        {formatPrice(course.price)}
                      </small>
                    </div>
                  </div>
                ) : (
                  <span className="h4 text-primary mb-0 fw-bold">
                    {formatPrice(course.current_price)} تومان
                  </span>
                )}
              </div>
            )}
          </div>

          <div className="d-grid gap-2">
            <Link 
              to={`/courses/course/${course.slug}`}
              className="btn btn-outline-primary w-100"
              style={{ 
                borderRadius: '12px',
                padding: '0.75rem',
                fontWeight: 600,
                borderWidth: '2px',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(44, 90, 160, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <i className="fas fa-eye me-2"></i>
              مشاهده جزئیات
            </Link>
            
            {onAddToCart && !course.is_free && (
              <Button
                variant="primary"
                className="w-100"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onAddToCart(course);
                }}
                style={{ 
                  borderRadius: '12px',
                  padding: '0.75rem',
                  fontWeight: 600,
                  border: 'none',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(44, 90, 160, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <i className="fas fa-shopping-cart me-2"></i>
                افزودن به سبد خرید
              </Button>
            )}
          </div>
        </div>
      </Card.Body>
    </Card>
  );
};

export default CourseCard;
