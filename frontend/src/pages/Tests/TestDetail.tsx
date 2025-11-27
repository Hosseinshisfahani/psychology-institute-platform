import React from 'react';
import { Container, Card } from 'react-bootstrap';
import { Helmet } from 'react-helmet-async';
import { useI18n } from '../../contexts/I18nContext';

const TestDetail: React.FC = () => {
  const { t } = useI18n();

  return (
    <>
      <Helmet>
        <title>جزئیات تست - {t('home.title')}</title>
      </Helmet>

      <Container className="py-5">
        <Card>
          <Card.Body className="text-center py-5">
            <i className="fas fa-clipboard-list text-primary mb-3" style={{ fontSize: '4rem' }}></i>
            <h2>جزئیات تست</h2>
            <p className="text-muted">صفحه جزئیات تست در حال توسعه است</p>
          </Card.Body>
        </Card>
      </Container>
    </>
  );
};

export default TestDetail;
