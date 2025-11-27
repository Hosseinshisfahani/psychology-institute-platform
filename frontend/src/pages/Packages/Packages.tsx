import React, { useState } from 'react';
import { Container, Row, Col, Card, Badge, Button, Form, Spinner, Alert } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import CourseHoverCard from '../../components/CourseHoverCard';

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

interface Package {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  category_name: string;
  price: string;
  discount_price: string | null;
  current_price: string;
  discount_percentage: number;
  is_featured: boolean;
  total_courses: number;
  total_hours: number;
  duration_months: number;
  thumbnail: string | null;
  rating: number;
  purchase_count: number;
  savings_amount: string;
  savings_percentage: number;
}

const Packages: React.FC = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);
  const [hoveredPackageSlug, setHoveredPackageSlug] = useState<string | null>(null);

  const { data: packages, isLoading, error } = useQuery<Package[]>({
    queryKey: ['packages', selectedCategory, showFeaturedOnly],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      if (showFeaturedOnly) params.append('featured', 'true');
      
      const response = await axios.get(`/api/packages/?${params.toString()}`);
      // Handle paginated response from Django REST Framework
      return response.data.results || response.data;
    },
  });

  // Fetch courses for hovered package
  const { data: hoveredPackageCourses } = useQuery<Course[]>({
    queryKey: ['package-courses', hoveredPackageSlug],
    queryFn: async () => {
      if (!hoveredPackageSlug) return [];
      const response = await axios.get(`/api/packages/${hoveredPackageSlug}/`);
      return response.data.courses || [];
    },
    enabled: !!hoveredPackageSlug,
  });

  return (
    <>
      <Helmet>
        <title>بسته‌های آموزشی - {t('home.title')}</title>
        <meta name="description" content="بسته‌های آموزشی روان‌شناسی" />
      </Helmet>

      <Container className="py-5">
        {/* Header */}
        <div className="mb-5 text-center">
          <h1 className="mb-3">
            <i className="fas fa-box-open text-primary ms-2"></i>
            بسته‌های آموزشی
          </h1>
          <p className="text-muted">
            با خرید بسته‌های آموزشی تا 50% صرفه‌جویی کنید
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-4">
          <Card.Body>
            <Row>
              <Col md={6} className="mb-3 mb-md-0">
                <Form.Group>
                  <Form.Label>دسته‌بندی</Form.Label>
                  <Form.Select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                  >
                    <option value="">همه دسته‌ها</option>
                    <option value="therapy">درمان</option>
                    <option value="counseling">مشاوره</option>
                    <option value="development">توسعه فردی</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group>
                  <Form.Label>نمایش</Form.Label>
                  <Form.Check
                    type="checkbox"
                    label="فقط بسته‌های ویژه"
                    checked={showFeaturedOnly}
                    onChange={(e) => setShowFeaturedOnly(e.target.checked)}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Card.Body>
        </Card>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-5">
            <Spinner animation="border" variant="primary" />
            <p className="mt-3 text-muted">در حال بارگذاری بسته‌ها...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <Alert variant="danger" className="mb-4">
            <Alert.Heading>خطا در بارگذاری بسته‌ها</Alert.Heading>
            <p>متأسفانه در بارگذاری بسته‌ها خطایی رخ داده است. لطفاً صفحه را مجدداً بارگذاری کنید.</p>
          </Alert>
        )}

        {/* Packages Grid */}
        {!isLoading && !error && packages && Array.isArray(packages) && (
          <>
            {packages.length === 0 ? (
              <Card>
                <Card.Body className="text-center py-5">
                  <i className="fas fa-inbox text-muted mb-3" style={{ fontSize: '3rem' }}></i>
                  <h5>بسته‌ای یافت نشد</h5>
                  <p className="text-muted">در حال حاضر بسته‌ای با این فیلترها وجود ندارد</p>
                </Card.Body>
              </Card>
            ) : (
              <Row>
                {packages.map((pkg) => (
                  <Col key={pkg.id} md={6} lg={4} className="mb-4">
                    <Card className="h-100 shadow-sm hover-shadow">
                      {pkg.thumbnail && (
                        <Card.Img
                          variant="top"
                          src={pkg.thumbnail}
                          style={{ height: '200px', objectFit: 'cover' }}
                        />
                      )}
                      <Card.Body className="d-flex flex-column">
                        <div className="mb-2">
                          <Badge bg="info" className="ms-2">
                            {pkg.category_name}
                          </Badge>
                          {pkg.is_featured && (
                            <Badge bg="warning" text="dark">
                              <i className="fas fa-star ms-1"></i>
                              ویژه
                            </Badge>
                          )}
                        </div>

                        <Card.Title className="mb-2">{pkg.title}</Card.Title>
                        <Card.Text className="text-muted small mb-3">
                          {pkg.short_description}
                        </Card.Text>

                        <div className="mb-3">
                          <div 
                            className="d-flex align-items-center mb-2 small position-relative"
                            onMouseEnter={() => setHoveredPackageSlug(pkg.slug)}
                            onMouseLeave={() => setHoveredPackageSlug(null)}
                            style={{ cursor: 'pointer' }}
                          >
                            <i className="fas fa-book text-primary ms-2"></i>
                            <span>{pkg.total_courses} بسته</span>
                            {hoveredPackageSlug === pkg.slug && hoveredPackageCourses && hoveredPackageCourses.length > 0 && (
                              <CourseHoverCard
                                courses={hoveredPackageCourses}
                                show={true}
                                onMouseEnter={() => setHoveredPackageSlug(pkg.slug)}
                                onMouseLeave={() => setHoveredPackageSlug(null)}
                                position="bottom"
                              />
                            )}
                          </div>
                          <div className="d-flex align-items-center mb-2 small">
                            <i className="fas fa-clock text-primary ms-2"></i>
                            <span>{pkg.total_hours} ساعت</span>
                          </div>
                          <div className="d-flex align-items-center mb-2 small">
                            <i className="fas fa-calendar text-primary ms-2"></i>
                            <span>{pkg.duration_months} ماه دسترسی</span>
                          </div>
                          <div className="d-flex align-items-center mb-2 small">
                            <i className="fas fa-users text-primary ms-2"></i>
                            <span>{pkg.purchase_count} خریدار</span>
                          </div>
                          <div className="d-flex align-items-center small">
                            <i className="fas fa-star text-warning ms-2"></i>
                            <span>{pkg.rating.toFixed(1)}</span>
                          </div>
                        </div>

                        {pkg.savings_percentage > 0 && (
                          <Alert variant="success" className="py-2 px-3 mb-3 small">
                            <i className="fas fa-percentage ms-1"></i>
                            <strong>{pkg.savings_percentage}% صرفه‌جویی</strong>
                            {' '}({parseInt(pkg.savings_amount).toLocaleString()} تومان)
                          </Alert>
                        )}

                        <div className="mt-auto">
                          <div className="d-flex justify-content-between align-items-center mb-3">
                            <div>
                              {pkg.discount_price ? (
                                <>
                                  <span className="text-decoration-line-through text-muted small ms-2">
                                    {parseInt(pkg.price).toLocaleString()} تومان
                                  </span>
                                  <span className="h5 text-primary mb-0">
                                    {parseInt(pkg.current_price).toLocaleString()} تومان
                                  </span>
                                  <Badge bg="danger" className="me-2">
                                    {pkg.discount_percentage}%
                                  </Badge>
                                </>
                              ) : (
                                <span className="h5 text-primary mb-0">
                                  {parseInt(pkg.price).toLocaleString()} تومان
                                </span>
                              )}
                            </div>
                          </div>

                          <div className="d-grid gap-2">
                            <Button
                              variant="primary"
                              onClick={() => navigate(`/packages/${pkg.slug}`)}
                            >
                              مشاهده جزئیات
                            </Button>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
            )}
          </>
        )}
      </Container>
    </>
  );
};

export default Packages;

