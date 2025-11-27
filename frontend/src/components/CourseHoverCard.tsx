import React from 'react';
import { Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import './CourseHoverCard.css';

interface Course {
  id: number;
  title: string;
  slug: string;
  short_description?: string;
  instructor_name?: string;
  duration_hours?: number;
  thumbnail?: string | null;
  difficulty?: string;
}

interface CourseHoverCardProps {
  courses: Course[];
  show: boolean;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

const CourseHoverCard: React.FC<CourseHoverCardProps> = ({
  courses,
  show,
  onMouseEnter,
  onMouseLeave,
  position = 'bottom'
}) => {
  if (!show || !courses || courses.length === 0) {
    return null;
  }

  const getDifficultyBadge = (difficulty?: string) => {
    if (!difficulty) return null;
    const badges: Record<string, { label: string; bg: string }> = {
      beginner: { label: 'مقدماتی', bg: 'success' },
      intermediate: { label: 'متوسط', bg: 'warning' },
      advanced: { label: 'پیشرفته', bg: 'danger' }
    };
    const badge = badges[difficulty];
    return badge ? (
      <span className={`badge bg-${badge.bg} me-1`} style={{ fontSize: '0.7rem' }}>
        {badge.label}
      </span>
    ) : null;
  };

  return (
    <div
      className={`course-hover-card course-hover-card-${position}`}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <Card className="shadow-lg border-0">
        <Card.Header className="bg-primary text-white">
          <h6 className="mb-0">
            <i className="fas fa-graduation-cap me-2"></i>
            دوره‌های بسته ({courses.length})
          </h6>
        </Card.Header>
        <Card.Body className="p-0" style={{ maxHeight: '400px', overflowY: 'auto' }}>
          <div className="list-group list-group-flush">
            {courses.map((course, index) => (
              <Link
                key={course.id}
                to={`/courses/course/${course.slug}`}
                className="list-group-item list-group-item-action course-hover-item"
                style={{
                  borderBottom: index < courses.length - 1 ? '1px solid #e9ecef' : 'none',
                  textDecoration: 'none',
                  color: 'inherit'
                }}
              >
                <div className="d-flex align-items-start">
                  {course.thumbnail && (
                    <img
                      src={course.thumbnail}
                      alt={course.title}
                      className="me-3"
                      style={{
                        width: '60px',
                        height: '60px',
                        objectFit: 'cover',
                        borderRadius: '4px',
                        flexShrink: 0
                      }}
                    />
                  )}
                  <div className="flex-grow-1">
                    <div className="d-flex align-items-start justify-content-between mb-1">
                      <h6 className="mb-0" style={{ fontSize: '0.9rem', fontWeight: 600 }}>
                        {course.title}
                      </h6>
                    </div>
                    {course.short_description && (
                      <p className="text-muted small mb-1" style={{ fontSize: '0.75rem' }}>
                        {course.short_description.substring(0, 60)}
                        {course.short_description.length > 60 ? '...' : ''}
                      </p>
                    )}
                    <div className="d-flex align-items-center gap-2 flex-wrap">
                      {getDifficultyBadge(course.difficulty)}
                      {course.instructor_name && (
                        <span className="text-muted small">
                          <i className="fas fa-user me-1" style={{ fontSize: '0.7rem' }}></i>
                          {course.instructor_name}
                        </span>
                      )}
                      {course.duration_hours && (
                        <span className="text-muted small">
                          <i className="fas fa-clock me-1" style={{ fontSize: '0.7rem' }}></i>
                          {course.duration_hours} ساعت
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default CourseHoverCard;

