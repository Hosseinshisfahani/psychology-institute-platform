import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, InputGroup, Button, Spinner, Alert, Badge, ButtonGroup } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useI18n } from '../../contexts/I18nContext';
import CourseCard from '../../components/Courses/CourseCard';
import { Course, CourseCategory, CourseFilters } from '../../types/Course';

const Courses: React.FC = () => {
  const { t } = useI18n();
  const [filters, setFilters] = useState<CourseFilters>({
    search: '',
    category: undefined,
    difficulty: undefined,
    is_free: undefined,
    ordering: '-created_at'
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(12);
  const [showFilters, setShowFilters] = useState(false);

  // Fetch courses
  const { data: coursesData, isLoading: coursesLoading, error: coursesError } = useQuery({
    queryKey: ['courses', filters, currentPage],
    queryFn: async () => {
      const params = new URLSearchParams();
      
      if (filters.search) params.append('search', filters.search);
      if (filters.category) params.append('category', filters.category.toString());
      if (filters.difficulty) params.append('difficulty', filters.difficulty);
      if (filters.is_free !== undefined) params.append('is_free', filters.is_free.toString());
      if (filters.ordering) params.append('ordering', filters.ordering);
      
      params.append('page', currentPage.toString());
      params.append('page_size', pageSize.toString());

      const response = await axios.get(`/api/courses/?${params.toString()}`);
      return response.data;
    },
  });

  // Fetch categories
  const { data: categories = [], error: categoriesError } = useQuery({
    queryKey: ['course-categories'],
    queryFn: async () => {
      const response = await axios.get('/api/courses/categories/');
      return response.data.results || response.data;
    },
  });

  const courses = coursesData?.results || [];
  const totalPages = Math.ceil((coursesData?.count || 0) / pageSize);

  const handleFilterChange = (key: keyof CourseFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
  };

  const handleAddToCart = async (course: Course) => {
    try {
      await axios.post(`/api/courses/add-to-cart/${course.slug}/`);
      alert('دوره به سبد خرید اضافه شد!');
    } catch (error: any) {
      console.error('Error adding to cart:', error);
      if (error.response?.status === 401) {
        alert('لطفاً ابتدا وارد حساب کاربری خود شوید');
      } else {
        alert(error.response?.data?.error || 'خطا در افزودن به سبد خرید');
      }
    }
  };

  const handleCategoryClick = (categoryId: number | undefined) => {
    handleFilterChange('category', categoryId);
    setShowFilters(false);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: undefined,
      difficulty: undefined,
      is_free: undefined,
      ordering: '-created_at'
    });
    setCurrentPage(1);
  };

  const hasActiveFilters = filters.search || filters.category || filters.difficulty || filters.is_free !== undefined;

  const difficultyOptions = [
    { value: '', label: 'همه سطوح', icon: 'fa-list' },
    { value: 'beginner', label: 'مبتدی', icon: 'fa-seedling', color: 'success' },
    { value: 'intermediate', label: 'متوسط', icon: 'fa-chart-line', color: 'warning' },
    { value: 'advanced', label: 'پیشرفته', icon: 'fa-trophy', color: 'danger' }
  ];

  const orderingOptions = [
    { value: '-created_at', label: 'جدیدترین', icon: 'fa-clock' },
    { value: 'created_at', label: 'قدیمی‌ترین', icon: 'fa-calendar' },
    { value: '-rating', label: 'بیشترین امتیاز', icon: 'fa-star' },
    { value: '-enrollment_count', label: 'محبوب‌ترین', icon: 'fa-fire' },
    { value: 'price', label: 'کمترین قیمت', icon: 'fa-arrow-down' },
    { value: '-price', label: 'بیشترین قیمت', icon: 'fa-arrow-up' }
  ];

  // Generate pagination items
  const getPaginationItems = () => {
    const items = [];
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    if (startPage > 1) {
      items.push(1);
      if (startPage > 2) items.push('ellipsis-start');
    }

    for (let i = startPage; i <= endPage; i++) {
      items.push(i);
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) items.push('ellipsis-end');
      items.push(totalPages);
    }

    return items;
  };

  return (
    <>
      <Helmet>
        <title>دوره‌های آموزشی - {t('home.title')}</title>
        <meta name="description" content="مشاهده و ثبت‌نام در دوره‌های جامع و تخصصی روانشناسی" />
      </Helmet>

      {/* Hero Section */}
      <section 
        className="py-5 mb-4"
        style={{
          background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
          color: 'white',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 0%, transparent 50%)',
            pointerEvents: 'none'
          }}
        />
        <Container style={{ position: 'relative', zIndex: 1 }}>
          <Row className="align-items-center">
            <Col lg={8} className="mx-auto text-center">
              <div className="mb-4">
                <i className="fas fa-graduation-cap" style={{ fontSize: '4rem', opacity: 0.9 }}></i>
              </div>
              <h1 className="display-4 fw-bold mb-3">
                دوره‌های آموزشی
              </h1>
              <p className="lead mb-4" style={{ fontSize: '1.2rem', opacity: 0.95 }}>
                دوره‌های جامع و تخصصی روانشناسی برای یادگیری عمیق و حرفه‌ای
              </p>
            </Col>
          </Row>
        </Container>
      </section>

      <Container>
        {/* Category Pills */}
        {Array.isArray(categories) && categories.length > 0 && (
          <div className="mb-4">
            <div className="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-2">
              <h5 className="mb-0">
                <i className="fas fa-folder-open text-primary me-2"></i>
                دسته‌بندی‌ها:
              </h5>
              <Button
                variant="outline-primary"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                className="d-md-none"
              >
                <i className={`fas fa-${showFilters ? 'times' : 'filter'} me-2`}></i>
                فیلترها
              </Button>
            </div>
            <div className="d-flex flex-wrap gap-2">
              <Button
                variant={filters.category === undefined ? 'primary' : 'outline-primary'}
                size="sm"
                onClick={() => handleCategoryClick(undefined)}
                style={{ borderRadius: '20px' }}
              >
                همه دسته‌ها
              </Button>
              {categories.map((category: CourseCategory) => (
                <Button
                  key={category.id}
                  variant={filters.category === category.id ? 'primary' : 'outline-primary'}
                  size="sm"
                  onClick={() => handleCategoryClick(category.id)}
                  style={{ borderRadius: '20px' }}
                >
                  {category.icon && <i className={`${category.icon} me-2`}></i>}
                  {category.name}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Advanced Filters */}
        <Card 
          className={`mb-4 ${showFilters ? '' : 'd-none d-md-block'}`}
          style={{ 
            borderRadius: '20px',
            border: '1px solid #e9ecef',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
            transition: 'all 0.3s ease',
            background: '#ffffff'
          }}
        >
          <Card.Body className="p-4">
            {/* Header */}
            <div className="d-flex align-items-center justify-content-between mb-4">
              <div className="d-flex align-items-center gap-2">
                <div 
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white'
                  }}
                >
                  <i className="fas fa-filter"></i>
                </div>
                <div>
                  <h6 className="mb-0 fw-bold" style={{ color: '#2c3e50' }}>
                    فیلترهای پیشرفته
                  </h6>
                  <small className="text-muted">جستجو و فیلتر دقیق‌تر دوره‌ها</small>
                </div>
              </div>
              {hasActiveFilters && (
                <Button
                  variant="link"
                  size="sm"
                  onClick={clearFilters}
                  className="text-danger p-0"
                  style={{ fontWeight: 600 }}
                >
                  <i className="fas fa-times-circle me-1"></i>
                  پاک کردن همه
                </Button>
              )}
            </div>

            <Form onSubmit={handleSearch}>
              {/* Search Row - Full Width */}
              <div className="mb-4">
                <label className="form-label fw-semibold mb-2" style={{ color: '#495057', fontSize: '0.9rem' }}>
                  <i className="fas fa-search text-primary me-2"></i>
                  جستجو
                </label>
                <InputGroup style={{ borderRadius: '12px', overflow: 'hidden', border: '2px solid #e9ecef' }}>
                  <InputGroup.Text 
                    style={{ 
                      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)', 
                      border: 'none',
                      paddingLeft: '1.25rem',
                      paddingRight: '1.25rem'
                    }}
                  >
                    <i className="fas fa-search text-primary"></i>
                  </InputGroup.Text>
                  <Form.Control
                    type="text"
                    placeholder="جستجو در دوره‌ها... (عنوان، مدرس، توضیحات)"
                    value={filters.search || ''}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    style={{ 
                      border: 'none', 
                      background: '#f8f9fa',
                      padding: '0.75rem 1rem',
                      fontSize: '0.95rem'
                    }}
                    onFocus={(e) => {
                      e.target.style.background = 'white';
                      e.target.style.boxShadow = '0 0 0 0.2rem rgba(44, 90, 160, 0.15)';
                      e.target.closest('.input-group')?.setAttribute('style', 'border: 2px solid #2c5aa0; border-radius: 12px;');
                    }}
                    onBlur={(e) => {
                      e.target.style.background = '#f8f9fa';
                      e.target.style.boxShadow = 'none';
                      e.target.closest('.input-group')?.setAttribute('style', 'border: 2px solid #e9ecef; border-radius: 12px;');
                    }}
                  />
                  {filters.search && (
                    <Button
                      variant="link"
                      onClick={() => handleFilterChange('search', '')}
                      style={{ 
                        border: 'none',
                        background: '#f8f9fa',
                        color: '#6c757d',
                        padding: '0.75rem 1rem'
                      }}
                    >
                      <i className="fas fa-times"></i>
                    </Button>
                  )}
                </InputGroup>
              </div>

              {/* Filter Row */}
              <Row className="g-3 mb-3">
                {/* Category Filter */}
                <Col md={6} lg={4}>
                  <label className="form-label fw-semibold mb-2" style={{ color: '#495057', fontSize: '0.9rem' }}>
                    <i className="fas fa-folder text-primary me-2"></i>
                    دسته‌بندی
                  </label>
                  <Form.Select
                    value={filters.category || ''}
                    onChange={(e) => handleFilterChange('category', e.target.value ? parseInt(e.target.value) : undefined)}
                    style={{ 
                      borderRadius: '12px', 
                      border: '2px solid #e9ecef',
                      padding: '0.75rem 1rem',
                      fontSize: '0.95rem',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#2c5aa0';
                      e.target.style.boxShadow = '0 0 0 0.2rem rgba(44, 90, 160, 0.15)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e9ecef';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    <option value="">همه دسته‌بندی‌ها</option>
                    {Array.isArray(categories) && categories.map((category: CourseCategory) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
                
                {/* Difficulty Filter */}
                <Col md={6} lg={4}>
                  <label className="form-label fw-semibold mb-2" style={{ color: '#495057', fontSize: '0.9rem' }}>
                    <i className="fas fa-signal text-primary me-2"></i>
                    سطح دشواری
                  </label>
                  <Form.Select
                    value={filters.difficulty || ''}
                    onChange={(e) => handleFilterChange('difficulty', e.target.value || undefined)}
                    style={{ 
                      borderRadius: '12px', 
                      border: '2px solid #e9ecef',
                      padding: '0.75rem 1rem',
                      fontSize: '0.95rem',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#2c5aa0';
                      e.target.style.boxShadow = '0 0 0 0.2rem rgba(44, 90, 160, 0.15)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e9ecef';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    {difficultyOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
                
                {/* Ordering */}
                <Col md={12} lg={4}>
                  <label className="form-label fw-semibold mb-2" style={{ color: '#495057', fontSize: '0.9rem' }}>
                    <i className="fas fa-sort-amount-down text-primary me-2"></i>
                    مرتب‌سازی
                  </label>
                  <Form.Select
                    value={filters.ordering || ''}
                    onChange={(e) => handleFilterChange('ordering', e.target.value)}
                    style={{ 
                      borderRadius: '12px', 
                      border: '2px solid #e9ecef',
                      padding: '0.75rem 1rem',
                      fontSize: '0.95rem',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#2c5aa0';
                      e.target.style.boxShadow = '0 0 0 0.2rem rgba(44, 90, 160, 0.15)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#e9ecef';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    {orderingOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
              </Row>
              
              {/* Free Courses Toggle */}
              <div className="mb-3">
                <div 
                  className="d-flex align-items-center justify-content-between p-3"
                  style={{
                    background: filters.is_free === true 
                      ? 'linear-gradient(135deg, #e7f3ff 0%, #d0e7ff 100%)' 
                      : '#f8f9fa',
                    borderRadius: '12px',
                    border: filters.is_free === true ? '2px solid #2c5aa0' : '2px solid #e9ecef',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                  onClick={() => handleFilterChange('is_free', filters.is_free === true ? undefined : true)}
                  onMouseEnter={(e) => {
                    if (filters.is_free !== true) {
                      e.currentTarget.style.borderColor = '#2c5aa0';
                      e.currentTarget.style.background = '#f0f7ff';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (filters.is_free !== true) {
                      e.currentTarget.style.borderColor = '#e9ecef';
                      e.currentTarget.style.background = '#f8f9fa';
                    }
                  }}
                >
                  <div className="d-flex align-items-center gap-3">
                    <div
                      style={{
                        width: '24px',
                        height: '24px',
                        borderRadius: '6px',
                        border: '2px solid',
                        borderColor: filters.is_free === true ? '#2c5aa0' : '#adb5bd',
                        background: filters.is_free === true ? '#2c5aa0' : 'transparent',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      {filters.is_free === true && (
                        <i className="fas fa-check text-white" style={{ fontSize: '0.75rem' }}></i>
                      )}
                    </div>
                    <div>
                      <div className="fw-semibold" style={{ color: filters.is_free === true ? '#2c5aa0' : '#495057' }}>
                        فقط دوره‌های رایگان
                      </div>
                      <small className="text-muted" style={{ fontSize: '0.8rem' }}>
                        نمایش فقط دوره‌های رایگان
                      </small>
                    </div>
                  </div>
                  <div
                    style={{
                      width: '48px',
                      height: '24px',
                      borderRadius: '12px',
                      background: filters.is_free === true ? '#2c5aa0' : '#adb5bd',
                      position: 'relative',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <div
                      style={{
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        background: 'white',
                        position: 'absolute',
                        top: '2px',
                        right: filters.is_free === true ? '2px' : '26px',
                        transition: 'all 0.3s ease',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {hasActiveFilters && (
                <div className="d-flex gap-2 mt-3 pt-3" style={{ borderTop: '1px solid #e9ecef' }}>
                  <Button
                    variant="danger"
                    className="flex-fill"
                    onClick={clearFilters}
                    style={{ 
                      borderRadius: '12px',
                      padding: '0.75rem',
                      fontWeight: 600,
                      border: 'none'
                    }}
                  >
                    <i className="fas fa-redo me-2"></i>
                    پاک کردن فیلترها
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    className="flex-fill"
                    style={{ 
                      borderRadius: '12px',
                      padding: '0.75rem',
                      fontWeight: 600,
                      background: 'linear-gradient(135deg, #2c5aa0 0%, #3498db 100%)',
                      border: 'none'
                    }}
                  >
                    <i className="fas fa-search me-2"></i>
                    اعمال فیلترها
                  </Button>
                </div>
              )}
            </Form>
          </Card.Body>
        </Card>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="mb-4">
            <div className="d-flex flex-wrap gap-2 align-items-center">
              <small className="text-muted me-2">فیلترهای فعال:</small>
              {filters.search && (
                <Badge bg="primary" className="d-flex align-items-center gap-2" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
                  جستجو: {filters.search}
                  <i 
                    className="fas fa-times cursor-pointer" 
                    onClick={() => handleFilterChange('search', '')}
                    style={{ cursor: 'pointer' }}
                  ></i>
                </Badge>
              )}
              {filters.category && (
                <Badge bg="info" className="d-flex align-items-center gap-2" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
                  دسته: {categories.find((c: CourseCategory) => c.id === filters.category)?.name}
                  <i 
                    className="fas fa-times cursor-pointer" 
                    onClick={() => handleFilterChange('category', undefined)}
                    style={{ cursor: 'pointer' }}
                  ></i>
                </Badge>
              )}
              {filters.difficulty && (
                <Badge bg="warning" className="d-flex align-items-center gap-2" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
                  سطح: {difficultyOptions.find(o => o.value === filters.difficulty)?.label}
                  <i 
                    className="fas fa-times cursor-pointer" 
                    onClick={() => handleFilterChange('difficulty', undefined)}
                    style={{ cursor: 'pointer' }}
                  ></i>
                </Badge>
              )}
              {filters.is_free === true && (
                <Badge bg="success" className="d-flex align-items-center gap-2" style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
                  فقط رایگان
                  <i 
                    className="fas fa-times cursor-pointer" 
                    onClick={() => handleFilterChange('is_free', undefined)}
                    style={{ cursor: 'pointer' }}
                  ></i>
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Results Section */}
        {coursesLoading ? (
          <div className="text-center py-5">
            <Spinner animation="border" role="status" style={{ width: '3rem', height: '3rem' }}>
              <span className="visually-hidden">در حال بارگذاری...</span>
            </Spinner>
            <p className="text-muted mt-3">در حال بارگذاری دوره‌ها...</p>
          </div>
        ) : coursesError ? (
          <Alert variant="danger" className="text-center" style={{ borderRadius: '15px' }}>
            <i className="fas fa-exclamation-triangle me-2"></i>
            <strong>خطا در بارگذاری دوره‌ها</strong>
            <p className="mb-0 mt-2">لطفاً دوباره تلاش کنید یا صفحه را رفرش کنید.</p>
          </Alert>
        ) : courses.length === 0 ? (
          <Card className="text-center py-5" style={{ borderRadius: '15px', border: 'none', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
            <Card.Body>
              <div className="mb-4">
                <i className="fas fa-search text-muted" style={{ fontSize: '5rem', opacity: 0.5 }}></i>
              </div>
              <h4 className="mb-3">دوره‌ای یافت نشد</h4>
              <p className="text-muted mb-4">
                با فیلترهای انتخابی شما دوره‌ای یافت نشد. لطفاً فیلترها را تغییر دهید.
              </p>
              {hasActiveFilters && (
                <Button variant="primary" onClick={clearFilters} style={{ borderRadius: '10px' }}>
                  <i className="fas fa-redo me-2"></i>
                  پاک کردن فیلترها
                </Button>
              )}
            </Card.Body>
          </Card>
        ) : (
          <>
            {/* Results Header */}
            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
              <div className="d-flex align-items-center gap-3">
                <Badge bg="primary" className="fs-6 px-3 py-2" style={{ borderRadius: '10px' }}>
                  <i className="fas fa-book me-2"></i>
                  {coursesData?.count || 0} دوره یافت شد
                </Badge>
                {filters.ordering && (
                  <small className="text-muted">
                    مرتب‌سازی: {orderingOptions.find(o => o.value === filters.ordering)?.label}
                  </small>
                )}
              </div>
            </div>

            {/* Courses Grid */}
            <Row className="g-4">
              {courses.map((course: Course, index: number) => (
                <Col 
                  key={course.id} 
                  lg={4} 
                  md={6}
                  style={{
                    animation: `fadeInUp 0.5s ease ${index * 0.1}s both`
                  }}
                >
                  <CourseCard 
                    course={course} 
                    onAddToCart={handleAddToCart}
                  />
                </Col>
              ))}
            </Row>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="d-flex justify-content-center mt-5 mb-4">
                <nav>
                  <ul className="pagination mb-0" style={{ gap: '0.5rem' }}>
                    <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                      <Button
                        variant="outline-primary"
                        className="page-link"
                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                        disabled={currentPage === 1}
                        style={{ borderRadius: '10px', border: 'none' }}
                      >
                        <i className="fas fa-chevron-right"></i>
                      </Button>
                    </li>
                    
                    {getPaginationItems().map((item, idx) => {
                      if (item === 'ellipsis-start' || item === 'ellipsis-end') {
                        return (
                          <li key={idx} className="page-item disabled">
                            <span className="page-link" style={{ border: 'none', background: 'transparent' }}>...</span>
                          </li>
                        );
                      }
                      return (
                        <li key={item} className={`page-item ${currentPage === item ? 'active' : ''}`}>
                          <Button
                            variant={currentPage === item ? 'primary' : 'outline-primary'}
                            className="page-link"
                            onClick={() => setCurrentPage(item as number)}
                            style={{ 
                              borderRadius: '10px', 
                              border: 'none',
                              minWidth: '40px'
                            }}
                          >
                            {item}
                          </Button>
                        </li>
                      );
                    })}
                    
                    <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                      <Button
                        variant="outline-primary"
                        className="page-link"
                        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                        disabled={currentPage === totalPages}
                        style={{ borderRadius: '10px', border: 'none' }}
                      >
                        <i className="fas fa-chevron-left"></i>
                      </Button>
                    </li>
                  </ul>
                </nav>
              </div>
            )}
          </>
        )}
      </Container>

      {/* Add CSS animations */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .cursor-pointer {
          cursor: pointer;
        }
        
        .page-link {
          transition: all 0.3s ease;
        }
        
        .page-link:hover {
          transform: translateY(-2px);
        }
      `}</style>
    </>
  );
};

export default Courses;
