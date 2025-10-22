import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-dark text-light py-5">
      <div className="container">
        <div className="row">
          <div className="col-lg-4 mb-4">
            <h5 className="text-primary mb-3">
              <i className="fas fa-heart me-2"></i>
              مرکز مشاوره سرمد
            </h5>
            <p className="text-muted">
              مرکز تخصصی مشاوره و خدمات روانشناسی با ارائه خدمات حرفه‌ای 
              و تیم متخصص درمانگران
            </p>
            <div className="d-flex gap-3">
              <a href="#" className="text-light">
                <i className="fab fa-telegram fa-lg"></i>
              </a>
              <a href="#" className="text-light">
                <i className="fab fa-instagram fa-lg"></i>
              </a>
              <a href="#" className="text-light">
                <i className="fab fa-whatsapp fa-lg"></i>
              </a>
            </div>
          </div>
          
          <div className="col-lg-2 col-md-6 mb-4">
            <h6 className="text-primary mb-3">خدمات</h6>
            <ul className="list-unstyled">
              <li className="mb-2">
                <Link to="/workshops" className="text-muted text-decoration-none">
                  کارگاه‌ها
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/courses" className="text-muted text-decoration-none">
                  دوره‌ها
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/packages" className="text-muted text-decoration-none">
                  پکیج‌ها
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/therapists" className="text-muted text-decoration-none">
                  درمانگران
                </Link>
              </li>
            </ul>
          </div>
          
          <div className="col-lg-2 col-md-6 mb-4">
            <h6 className="text-primary mb-3">اطلاعات</h6>
            <ul className="list-unstyled">
              <li className="mb-2">
                <Link to="/about/institute" className="text-muted text-decoration-none">
                  درباره موسسه
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/about/founder" className="text-muted text-decoration-none">
                  درباره بنیان‌گذار
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/blog" className="text-muted text-decoration-none">
                  وبلاگ
                </Link>
              </li>
            </ul>
          </div>
          
          <div className="col-lg-4 mb-4">
            <h6 className="text-primary mb-3">تماس با ما</h6>
            <div className="text-muted">
              <p className="mb-2">
                <i className="fas fa-map-marker-alt me-2"></i>
                تهران، خیابان ولیعصر
              </p>
              <p className="mb-2">
                <i className="fas fa-phone me-2"></i>
                021-12345678
              </p>
              <p className="mb-2">
                <i className="fas fa-envelope me-2"></i>
                info@sarmadclinic.ir
              </p>
            </div>
          </div>
        </div>
        
        <hr className="my-4" />
        
        <div className="row align-items-center">
          <div className="col-md-6">
            <p className="text-muted mb-0">
              © 2024 مرکز مشاوره و خدمات روانشناسی سرمد. تمامی حقوق محفوظ است.
            </p>
          </div>
          <div className="col-md-6 text-md-end">
            <div className="d-flex justify-content-md-end gap-3">
              <a href="/privacy" className="text-muted text-decoration-none">
                حریم خصوصی
              </a>
              <a href="/terms" className="text-muted text-decoration-none">
                شرایط استفاده
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
