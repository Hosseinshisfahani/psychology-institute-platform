import React from 'react';
import { Container, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';

const NotFound: React.FC = () => {
  const { t } = useI18n();

  return (
    <>
      <Helmet>
        <title>صفحه یافت نشد - {t('home.title')}</title>
      </Helmet>

      <Container className="py-5">
        <Card>
          <Card.Body className="text-center py-5">
            <i className="fas fa-exclamation-triangle text-warning mb-3" style={{ fontSize: '4rem' }}></i>
            <h1 className="display-1">404</h1>
            <h2>صفحه یافت نشد</h2>
            <p className="text-muted mb-4">
              متأسفانه صفحه‌ای که به دنبال آن هستید وجود ندارد یا حذف شده است.
            </p>
            <Link to="/" className="btn btn-primary">
              <i className="fas fa-home me-2"></i>
              بازگشت به خانه
            </Link>
          </Card.Body>
        </Card>
      </Container>
    </>
  );
};

export default NotFound;
