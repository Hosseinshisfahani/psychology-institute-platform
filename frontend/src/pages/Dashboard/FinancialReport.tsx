import React from 'react';
import { Container, Row, Col, Card, Table, Badge, Alert, Spinner, Tab, Tabs } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface SuccessfulPayment {
  id: number;
  order_number: string;
  order_id: number;
  amount: string;
  payment_method: string;
  transaction_id: string;
  workshop_title: string | null;
  completed_at: string;
  created_at: string;
}

interface RemainingInstallment {
  id: number;
  workshop_title: string;
  workshop_slug: string;
  installment_number: number;
  total_installments: number;
  amount: string;
  due_date: string;
  due_date_persian: string;
  is_overdue: boolean;
  registration_id: number;
}

interface InstallmentPayment {
  id: number;
  installment_number: number;
  amount: string;
  due_date: string;
  due_date_persian: string;
  status: string;
  paid_at: string | null;
  is_overdue: boolean;
}

interface WorkshopRegistration {
  id: number;
  workshop: {
    id: number;
    title: string;
    slug: string;
  };
  status: string;
  payment_type: string;
  amount_paid: string;
  total_amount: string;
  progress_percentage: number;
  registered_at: string;
  installment_plan?: {
    total_amount: string;
    number_of_installments: number;
    installment_amount: string;
    total_paid: string;
    remaining_amount: string;
    is_fully_paid: boolean;
    payments: InstallmentPayment[];
  };
}

interface PackagePurchase {
  id: number;
  package: {
    id: number;
    title: string;
    slug: string;
  };
  amount_paid: string;
  purchased_at: string;
  progress?: {
    overall_progress_percentage: number;
    completed_courses: number;
    total_courses: number;
  };
}

interface CoursePurchase {
  id: number;
  course: {
    id: number;
    title: string;
    slug: string;
  };
  amount_paid: string;
  purchased_at: string;
}

interface Order {
  id: number;
  order_number: string;
  status: string;
  total_amount: string;
  created_at: string;
}

interface FinancialData {
  orders: Order[];
  workshop_registrations: WorkshopRegistration[];
  package_purchases: PackagePurchase[];
  course_purchases: CoursePurchase[];
  installment_payments: InstallmentPayment[];
  successful_payments: SuccessfulPayment[];
  remaining_installments: RemainingInstallment[];
  total_spent: string;
  pending_installments_count: number;
  overdue_installments_count: number;
  total_orders: number;
}

const FinancialReport: React.FC = () => {
  const { data: financialData, isLoading } = useQuery<FinancialData>({
    queryKey: ['financial-report'],
    queryFn: async () => {
      const response = await axios.get('/api/dashboard/financial-report/');
      return response.data;
    },
  });

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      pending: 'warning',
      paid: 'success',
      overdue: 'danger',
      active: 'success',
      pending_payment: 'warning',
      completed: 'info',
      cancelled: 'secondary',
    };
    return variants[status] || 'secondary';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      pending: 'در انتظار پرداخت',
      paid: 'پرداخت شده',
      overdue: 'معوق',
      active: 'فعال',
      pending_payment: 'در انتظار پرداخت',
      completed: 'تکمیل شده',
      cancelled: 'لغو شده',
    };
    return texts[status] || status;
  };

  if (isLoading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3 text-muted">در حال بارگذاری...</p>
      </Container>
    );
  }

  if (!financialData) {
    return (
      <Container className="py-5">
        <Alert variant="danger">خطا در بارگذاری اطلاعات مالی</Alert>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>گزارش مالی - داشبورد</title>
      </Helmet>

      <Container className="py-5">
        <h2 className="mb-4">
          <i className="fas fa-file-invoice-dollar ms-2"></i>
          گزارش مالی
        </h2>

        {/* Summary Cards */}
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted">مجموع خریدها</h6>
                <h4 className="text-primary mb-0">
                  {parseInt(financialData.total_spent).toLocaleString()} تومان
                </h4>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted">تعداد سفارشات</h6>
                <h4 className="text-primary mb-0">{financialData.total_orders}</h4>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted">اقساط در انتظار</h6>
                <h4 className="text-warning mb-0">{financialData.pending_installments_count}</h4>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h6 className="text-muted">اقساط معوق</h6>
                <h4 className="text-danger mb-0">{financialData.overdue_installments_count}</h4>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Tabs */}
        <Card>
          <Card.Body>
            <Tabs defaultActiveKey="orders" className="mb-3">
              {/* Orders */}
              <Tab eventKey="orders" title="سفارشات">
                {financialData.orders.length === 0 ? (
                  <Alert variant="info">هنوز سفارشی ثبت نشده است</Alert>
                ) : (
                  <Table responsive hover>
                    <thead>
                      <tr>
                        <th>شماره سفارش</th>
                        <th>مبلغ</th>
                        <th>وضعیت</th>
                        <th>تاریخ</th>
                      </tr>
                    </thead>
                    <tbody>
                      {financialData.orders.map((order) => (
                        <tr key={order.id}>
                          <td><code>{order.order_number}</code></td>
                          <td>{parseInt(order.total_amount).toLocaleString()} تومان</td>
                          <td>
                            <Badge bg={getStatusBadge(order.status)}>
                              {getStatusText(order.status)}
                            </Badge>
                          </td>
                          <td>{new Date(order.created_at).toLocaleDateString('fa-IR')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </Tab>

              {/* Workshops */}
              <Tab eventKey="workshops" title="کارگاه‌ها">
                {financialData.workshop_registrations.length === 0 ? (
                  <Alert variant="info">هنوز در کارگاهی ثبت‌نام نکرده‌اید</Alert>
                ) : (
                  <Table responsive hover>
                    <thead>
                      <tr>
                        <th>عنوان کارگاه</th>
                        <th>نوع پرداخت</th>
                        <th>مبلغ پرداختی</th>
                        <th>مبلغ کل</th>
                        <th>وضعیت</th>
                        <th>پیشرفت</th>
                      </tr>
                    </thead>
                    <tbody>
                      {financialData.workshop_registrations.map((registration) => (
                        <tr key={registration.id}>
                          <td>{registration.workshop.title}</td>
                          <td>
                            {registration.payment_type === 'full_payment' ? 'کامل' : 'قسطی'}
                          </td>
                          <td>{parseInt(registration.amount_paid).toLocaleString()} تومان</td>
                          <td>{parseInt(registration.total_amount).toLocaleString()} تومان</td>
                          <td>
                            <Badge bg={getStatusBadge(registration.status)}>
                              {getStatusText(registration.status)}
                            </Badge>
                          </td>
                          <td>{registration.progress_percentage.toFixed(0)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </Tab>

              {/* Packages */}
              <Tab eventKey="packages" title="بسته‌ها">
                {financialData.package_purchases.length === 0 ? (
                  <Alert variant="info">هنوز بسته‌ای خریداری نکرده‌اید</Alert>
                ) : (
                  <Table responsive hover>
                    <thead>
                      <tr>
                        <th>عنوان بسته</th>
                        <th>مبلغ پرداختی</th>
                        <th>تاریخ خرید</th>
                        <th>پیشرفت</th>
                      </tr>
                    </thead>
                    <tbody>
                      {financialData.package_purchases.map((purchase) => (
                        <tr key={purchase.id}>
                          <td>{purchase.package.title}</td>
                          <td>{parseInt(purchase.amount_paid).toLocaleString()} تومان</td>
                          <td>{new Date(purchase.purchased_at).toLocaleDateString('fa-IR')}</td>
                          <td>
                            {purchase.progress ? (
                              <>
                                {purchase.progress.overall_progress_percentage.toFixed(0)}%
                                {' '}
                                ({purchase.progress.completed_courses}/{purchase.progress.total_courses} بسته)
                              </>
                            ) : (
                              '-'
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </Tab>

              {/* Courses */}
              <Tab eventKey="courses" title="بسته‌های آموزشی">
                {financialData.course_purchases.length === 0 ? (
                  <Alert variant="info">هنوز بسته آموزشی خریداری نکرده‌اید</Alert>
                ) : (
                  <Table responsive hover>
                    <thead>
                      <tr>
                        <th>عنوان بسته آموزشی</th>
                        <th>مبلغ پرداختی</th>
                        <th>تاریخ خرید</th>
                      </tr>
                    </thead>
                    <tbody>
                      {financialData.course_purchases.map((purchase) => (
                        <tr key={purchase.id}>
                          <td>{purchase.course.title}</td>
                          <td>{parseInt(purchase.amount_paid).toLocaleString()} تومان</td>
                          <td>{new Date(purchase.purchased_at).toLocaleDateString('fa-IR')}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </Tab>

              {/* Installments */}
              <Tab eventKey="installments" title={`اقساط (${financialData.installment_payments.length})`}>
                {financialData.installment_payments.length === 0 ? (
                  <Alert variant="info">اقساطی وجود ندارد</Alert>
                ) : (
                  <Table responsive hover>
                    <thead>
                      <tr>
                        <th>قسط</th>
                        <th>مبلغ</th>
                        <th>سررسید</th>
                        <th>وضعیت</th>
                        <th>تاریخ پرداخت</th>
                      </tr>
                    </thead>
                    <tbody>
                      {financialData.installment_payments.map((payment) => (
                        <tr key={payment.id} className={payment.is_overdue ? 'table-danger' : ''}>
                          <td>قسط {payment.installment_number}</td>
                          <td>{parseInt(payment.amount).toLocaleString()} تومان</td>
                          <td>{payment.due_date_persian}</td>
                          <td>
                            <Badge bg={getStatusBadge(payment.status)}>
                              {getStatusText(payment.status)}
                            </Badge>
                          </td>
                          <td>
                            {payment.paid_at ? new Date(payment.paid_at).toLocaleDateString('fa-IR') : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </Tab>

              {/* Successful Payments */}
              <Tab eventKey="payments" title={`پرداخت‌های موفق (${financialData.successful_payments?.length || 0})`}>
                {!financialData.successful_payments || financialData.successful_payments.length === 0 ? (
                  <Alert variant="info">پرداخت موفقی وجود ندارد</Alert>
                ) : (
                  <Table responsive hover>
                    <thead>
                      <tr>
                        <th>شماره سفارش</th>
                        <th>مبلغ</th>
                        <th>روش پرداخت</th>
                        <th>شناسه تراکنش</th>
                        <th>کارگاه</th>
                        <th>تاریخ پرداخت</th>
                      </tr>
                    </thead>
                    <tbody>
                      {financialData.successful_payments.map((payment) => (
                        <tr key={payment.id} className="table-success">
                          <td><code>{payment.order_number}</code></td>
                          <td>{parseInt(payment.amount).toLocaleString()} تومان</td>
                          <td>{payment.payment_method}</td>
                          <td>
                            {payment.transaction_id ? (
                              <code className="small">{payment.transaction_id}</code>
                            ) : (
                              '-'
                            )}
                          </td>
                          <td>{payment.workshop_title || '-'}</td>
                          <td>
                            {new Date(payment.completed_at || payment.created_at).toLocaleDateString('fa-IR')}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </Tab>

              {/* Remaining Installments */}
              <Tab eventKey="remaining" title={`اقساط باقیمانده (${financialData.remaining_installments?.length || 0})`}>
                {!financialData.remaining_installments || financialData.remaining_installments.length === 0 ? (
                  <Alert variant="success">هیچ قسطی باقی نمانده است - همه پرداخت شده است!</Alert>
                ) : (
                  <Table responsive hover>
                    <thead>
                      <tr>
                        <th>کارگاه</th>
                        <th>قسط</th>
                        <th>مبلغ</th>
                        <th>سررسید</th>
                        <th>وضعیت</th>
                      </tr>
                    </thead>
                    <tbody>
                      {financialData.remaining_installments.map((installment) => (
                        <tr 
                          key={installment.id} 
                          className={installment.is_overdue ? 'table-danger' : ''}
                        >
                          <td>{installment.workshop_title}</td>
                          <td>
                            قسط {installment.installment_number} از {installment.total_installments}
                          </td>
                          <td>{parseInt(installment.amount).toLocaleString()} تومان</td>
                          <td>{installment.due_date_persian}</td>
                          <td>
                            {installment.is_overdue ? (
                              <Badge bg="danger">معوق</Badge>
                            ) : (
                              <Badge bg="warning">در انتظار</Badge>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                )}
              </Tab>
            </Tabs>
          </Card.Body>
        </Card>
      </Container>
    </>
  );
};

export default FinancialReport;

