import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, InputGroup, Button, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';
import { blogApi } from '../../services/blogApi';

interface Post {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  featured_image?: string;
  category: {
    name: string;
    slug: string;
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

interface Category {
  id: number;
  name: string;
  slug: string;
}

const Blog: React.FC = () => {
  const { t } = useI18n();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  // Ensure we always have valid arrays
  const ensureArray = (data: any): any[] => {
    return Array.isArray(data) ? data : [];
  };

  // Fetch posts
  const { data: postsData, isLoading: postsLoading } = useQuery({
    queryKey: ['blog-posts', searchTerm, selectedCategory],
    queryFn: async () => {
      try {
        return await blogApi.getPosts({
          search: searchTerm || undefined,
          category: selectedCategory || undefined,
        });
      } catch (error) {
        console.error('Error fetching posts:', error);
        return { results: [], count: 0 };
      }
    },
  });

  // Extract posts from the paginated response
  const posts = postsData?.results || [];

  // Fetch categories
  const { data: categories = [], error: categoriesError } = useQuery({
    queryKey: ['blog-categories'],
    queryFn: async () => {
      try {
        return await blogApi.getCategories();
      } catch (error) {
        console.error('Error fetching categories:', error);
        return [];
      }
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // The query will automatically refetch due to the searchTerm dependency
  };

  return (
    <>
      <Helmet>
        <title>{t('nav.blog')} - {t('home.title')}</title>
        <meta name="description" content="آخرین مقالات و مطالب روانشناسی" />
      </Helmet>

      <Container className="py-5">
        <Row>
          <Col lg={8}>
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h1>{t('nav.blog')}</h1>
            </div>

            {/* Search and Filter */}
            <Card className="mb-4">
              <Card.Body>
                <Form onSubmit={handleSearch}>
                  <Row>
                    <Col md={8}>
                      <InputGroup>
                        <Form.Control
                          type="text"
                          placeholder={t('blog.search')}
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <Button type="submit" variant="outline-primary">
                          <i className="fas fa-search"></i>
                        </Button>
                      </InputGroup>
                    </Col>
                    <Col md={4}>
                      <Form.Select
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                      >
                        <option value="">همه دسته‌بندی‌ها</option>
                        {ensureArray(categories).map((category) => (
                          <option key={category.id} value={category.slug}>
                            {category.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Col>
                  </Row>
                </Form>
              </Card.Body>
            </Card>

            {/* Posts */}
            {postsLoading ? (
              <div className="text-center py-5">
                <Spinner animation="border" role="status">
                  <span className="visually-hidden">{t('common.loading')}</span>
                </Spinner>
              </div>
            ) : ensureArray(posts).length > 0 ? (
              <Row>
                {ensureArray(posts).map((post) => (
                  <Col md={6} lg={4} key={post.id} className="mb-4">
                    <Card className="h-100">
                      {post.featured_image && (
                        <Card.Img 
                          variant="top" 
                          src={post.featured_image} 
                          alt={post.title}
                          loading="lazy"
                          style={{ height: '200px', objectFit: 'cover' }}
                        />
                      )}
                      <Card.Body>
                        <div className="d-flex align-items-center mb-2">
                          <span className="badge bg-primary me-2">{post.category.name}</span>
                          <small className="text-muted">{post.created_at_persian}</small>
                        </div>
                        <Card.Title>
                          <Link 
                            to={`/blog/post/${post.slug}`} 
                            className="text-decoration-none text-dark"
                          >
                            {post.title}
                          </Link>
                        </Card.Title>
                        <Card.Text>{post.excerpt}</Card.Text>
                        <div className="d-flex justify-content-between align-items-center">
                          <small className="text-muted">
                            <i className="fas fa-user me-1"></i>
                            {post.author_name}
                          </small>
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
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
            ) : (
              <Card>
                <Card.Body className="text-center py-5">
                  <i className="fas fa-newspaper text-muted mb-3" style={{ fontSize: '3rem' }}></i>
                  <h5>{t('blog.no_posts')}</h5>
                  <p className="text-muted">لطفاً جستجوی خود را تغییر دهید</p>
                </Card.Body>
              </Card>
            )}
          </Col>

          <Col lg={4}>
            {/* Categories */}
            <Card className="mb-4">
              <Card.Header>
                <h6>{t('blog.categories')}</h6>
              </Card.Header>
              <Card.Body>
                <div className="list-group list-group-flush">
                  <button
                    className={`list-group-item list-group-item-action ${!selectedCategory ? 'active' : ''}`}
                    onClick={() => setSelectedCategory('')}
                  >
                    همه دسته‌بندی‌ها
                  </button>
                  {ensureArray(categories).map((category) => (
                    <button
                      key={category.id}
                      className={`list-group-item list-group-item-action ${selectedCategory === category.slug ? 'active' : ''}`}
                      onClick={() => setSelectedCategory(category.slug)}
                    >
                      {category.name}
                    </button>
                  ))}
                </div>
              </Card.Body>
            </Card>

            {/* Popular Posts */}
            <Card>
              <Card.Header>
                <h6>مقالات محبوب</h6>
              </Card.Header>
              <Card.Body>
                <p className="text-muted text-center">به زودی...</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Blog;
