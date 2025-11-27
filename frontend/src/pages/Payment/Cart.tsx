import React from 'react';
import { Container, Row, Col, Card, Button, ListGroup, Badge, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';
import axios from 'axios';

interface CartCourseItem {
  id: number;
  title: string;
  slug: string;
  thumbnail?: string | null;
  featured_image?: string | null;
  price: number;
  discount_price?: number | null;
  instructor_name: string;
}

interface CartPackageItem {
  id: number;
  title: string;
  slug: string;
  thumbnail?: string | null;
  price: number;
  discount_price?: number | null;
  current_price: number;
  total_courses: number;
  category_name?: string | null;
}

interface CartItem {
  id: number;
  item_type: 'course' | 'package' | string;
  item_id: number;
  item_title?: string;
  course?: CartCourseItem | null;
  package?: CartPackageItem | null;
  quantity: number;
  unit_price: number;
  total_price: number;
  added_at: string | null;
}

interface CartData {
  items: CartItem[];
  total_items: number;
  subtotal: number;
  discount: number;
  total: number;
}

const Cart: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const { t } = useI18n();
  const queryClient = useQueryClient();

  // Fetch cart data
  const { data: cart, isLoading } = useQuery<CartData>({
    queryKey: ['cart'],
    queryFn: async () => {
      const response = await axios.get('/api/payment/cart/');
      return response.data;
    },
    enabled: isAuthenticated,
  });

  // Remove item mutation
  const removeItemMutation = useMutation({
    mutationFn: async (itemId: number) => {
      await axios.delete(`/api/payment/cart/${itemId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  // Update quantity mutation
  const updateQuantityMutation = useMutation({
    mutationFn: async ({ itemId, quantity }: { itemId: number; quantity: number }) => {
      await axios.patch(`/api/payment/cart/${itemId}/`, { quantity });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  // Clear cart mutation
  const clearCartMutation = useMutation({
    mutationFn: async () => {
      await axios.delete('/api/payment/cart/clear/');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fa-IR').format(price);
  };

  if (!isAuthenticated) {
    return (
      <Container className="py-5">
        <Alert variant="warning">
          برای مشاهده سبد خرید ابتدا وارد حساب کاربری خود شوید.
        </Alert>
      </Container>
    );
  }

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

  if (!cart || cart.items.length === 0) {
    return (
      <>
        <Helmet>
          <title>سبد خرید - خالی</title>
        </Helmet>
        
        <Container className="py-5">
          <Row className="justify-content-center">
            <Col lg={6} className="text-center">
              <i className="fas fa-shopping-cart text-muted mb-4" style={{ fontSize: '5rem' }}></i>
              <h3 className="mb-3">سبد خرید خالی است</h3>
              <p className="text-muted mb-4">
                هنوز هیچ دوره یا پکیجی به سبد خرید اضافه نکرده‌اید. از پیشنهادهای متنوع ما دیدن کنید.
              </p>
              <div className="d-flex justify-content-center gap-2 flex-wrap">
                <Link to="/courses">
                  <Button variant="primary" size="lg">
                    <i className="fas fa-book me-2"></i>
                    مشاهده دوره‌ها
                  </Button>
                </Link>
                <Link to="/packages">
                  <Button variant="outline-primary" size="lg">
                    <i className="fas fa-box me-2"></i>
                    مشاهده پکیج‌ها
                  </Button>
                </Link>
              </div>
            </Col>
          </Row>
        </Container>
      </>
    );
  }

  return (
    <>
      <Helmet>
        <title>{`سبد خرید (${cart.total_items} مورد)`}</title>
        <meta name="description" content="سبد خرید شما حاوی بسته‌های آموزشی انتخابی برای خرید" />
      </Helmet>

      <Container className="py-4">
        <Row>
          <Col lg={8}>
            <Card>
              <Card.Header className="d-flex justify-content-between align-items-center">
                <h4 className="mb-0">
                  <i className="fas fa-shopping-cart me-2"></i>
                  سبد خرید ({cart.total_items} مورد)
                </h4>
                {cart.items.length > 0 && (
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={() => clearCartMutation.mutate()}
                    disabled={clearCartMutation.isPending}
                  >
                    <i className="fas fa-trash me-2"></i>
                    پاک کردن همه
                  </Button>
                )}
              </Card.Header>
              
              <ListGroup variant="flush">
                {cart.items.map((item) => {
                  const isCourseItem = item.item_type === 'course' && item.course;
                  const isPackageItem = item.item_type === 'package' && item.package;

                  if (!isCourseItem && !isPackageItem) {
                    return (
                      <ListGroup.Item key={item.id} className="py-3">
                        <Alert variant="warning" className="mb-0">
                          <i className="fas fa-exclamation-triangle me-2"></i>
                          اطلاعات آیتم در دسترس نیست
                        </Alert>
                      </ListGroup.Item>
                    );
                  }

                  const imageSource = isCourseItem
                    ? item.course!.thumbnail || item.course!.featured_image || '/images/course-placeholder.jpg'
                    : item.package!.thumbnail || '/images/course-placeholder.jpg';

                  const itemLink = isCourseItem
                    ? `/courses/course/${item.course!.slug}`
                    : `/packages/${item.package!.slug}`;

                  const itemTitle = isCourseItem
                    ? item.course!.title
                    : item.package!.title;

                  const subtitle = isCourseItem
                    ? `مدرس: ${item.course!.instructor_name || 'نامشخص'}`
                    : `${item.package!.total_courses} دوره${item.package!.category_name ? ` | ${item.package!.category_name}` : ''}`;

                  const originalPrice = isCourseItem
                    ? item.course!.price
                    : item.package!.price;

                  const discountPrice = isCourseItem
                    ? item.course!.discount_price ?? null
                    : item.package!.discount_price ?? null;

                  const currentPrice = discountPrice ?? (isPackageItem ? item.package!.current_price : item.unit_price);

                  const canAdjustQuantity = isCourseItem;

                  return (
                    <ListGroup.Item key={item.id} className="py-3">
                      <Row className="align-items-center">
                        <Col md={2}>
                          <img
                            src={imageSource}
                            alt={itemTitle}
                            className="img-fluid rounded"
                            style={{ width: '100%', height: '80px', objectFit: 'cover' }}
                            onError={(e) => {
                              e.currentTarget.src = '/images/course-placeholder.jpg';
                            }}
                          />
                        </Col>

                        <Col md={5}>
                          <h6 className="mb-1">
                            <Link to={itemLink} className="text-decoration-none">
                              {itemTitle}
                            </Link>
                          </h6>
                          <small className="text-muted">{subtitle}</small>
                        </Col>

                        <Col md={2}>
                          <div className="text-center">
                            {discountPrice ? (
                              <>
                                <div className="text-decoration-line-through text-muted small">
                                  {formatPrice(originalPrice)} تومان
                                </div>
                                <div className="fw-bold text-success">
                                  {formatPrice(discountPrice as number)} تومان
                                </div>
                              </>
                            ) : (
                              <div className="fw-bold">
                                {formatPrice(currentPrice)} تومان
                              </div>
                            )}
                          </div>
                        </Col>

                        <Col md={2}>
                          <div className="d-flex align-items-center justify-content-center">
                            <Button
                              variant="outline-secondary"
                              size="sm"
                              onClick={() => updateQuantityMutation.mutate({
                                itemId: item.id,
                                quantity: Math.max(1, item.quantity - 1)
                              })}
                              disabled={!canAdjustQuantity || item.quantity <= 1}
                            >
                              <i className="fas fa-minus"></i>
                            </Button>

                            <span className="mx-3 fw-bold">{item.quantity}</span>

                            <Button
                              variant="outline-secondary"
                              size="sm"
                              onClick={() => updateQuantityMutation.mutate({
                                itemId: item.id,
                                quantity: item.quantity + 1
                              })}
                              disabled={!canAdjustQuantity}
                            >
                              <i className="fas fa-plus"></i>
                            </Button>
                          </div>
                        </Col>

                        <Col md={1}>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => removeItemMutation.mutate(item.id)}
                            disabled={removeItemMutation.isPending}
                          >
                            <i className="fas fa-trash"></i>
                          </Button>
                        </Col>
                      </Row>
                    </ListGroup.Item>
                  );
                })}
              </ListGroup>
            </Card>
          </Col>
          
          {/* Order Summary */}
          <Col lg={4}>
            <Card>
              <Card.Header>
                <h5 className="mb-0">خلاصه سفارش</h5>
              </Card.Header>
              
              <Card.Body>
                <div className="d-flex justify-content-between mb-2">
                  <span>جمع کل ({cart.total_items} مورد):</span>
                  <span>{formatPrice(cart.subtotal)} تومان</span>
                </div>
                
                {cart.discount > 0 && (
                  <div className="d-flex justify-content-between mb-2 text-success">
                    <span>تخفیف:</span>
                    <span>-{formatPrice(cart.discount)} تومان</span>
                  </div>
                )}
                
                <hr />
                
                <div className="d-flex justify-content-between mb-3 fs-5 fw-bold">
                  <span>مبلغ نهایی:</span>
                  <span className="text-primary">{formatPrice(cart.total)} تومان</span>
                </div>
                
                <div className="d-grid gap-2">
                  <Link to="/payment/checkout">
                    <Button variant="primary" size="lg" className="w-100">
                      <i className="fas fa-credit-card me-2"></i>
                      ادامه خرید
                    </Button>
                  </Link>
                  
                  <Link to="/courses">
                    <Button variant="outline-primary" className="w-100">
                      <i className="fas fa-arrow-right me-2"></i>
                      مشاهده دوره‌ها
                    </Button>
                  </Link>

                  <Link to="/packages">
                    <Button variant="outline-secondary" className="w-100">
                      <i className="fas fa-box-open me-2"></i>
                      مشاهده پکیج‌ها
                    </Button>
                  </Link>
                </div>
              </Card.Body>
            </Card>
            
            {/* Security Badge */}
            <Card className="mt-3">
              <Card.Body className="text-center">
                <i className="fas fa-shield-alt text-success mb-2" style={{ fontSize: '2rem' }}></i>
                <p className="small text-muted mb-0">
                  تمامی پرداخت‌ها از طریق درگاه‌های امن انجام می‌شود
                </p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
};

export default Cart;
