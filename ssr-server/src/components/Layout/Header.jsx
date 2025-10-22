import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="bg-white shadow-sm">
      <nav className="navbar navbar-expand-lg navbar-light">
        <div className="container">
          <Link className="navbar-brand fw-bold" to="/">
            <i className="fas fa-heart text-primary me-2"></i>
            مرکز مشاوره سرمد
          </Link>
          
          <button 
            className="navbar-toggler" 
            type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#navbarNav"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav me-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/">خانه</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/blog">وبلاگ</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/workshops">کارگاه‌ها</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/courses">دوره‌ها</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/packages">پکیج‌ها</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/therapists">درمانگران</Link>
              </li>
              <li className="nav-item dropdown">
                <a 
                  className="nav-link dropdown-toggle" 
                  href="#" 
                  role="button" 
                  data-bs-toggle="dropdown"
                >
                  درباره ما
                </a>
                <ul className="dropdown-menu">
                  <li>
                    <Link className="dropdown-item" to="/about/institute">
                      درباره موسسه
                    </Link>
                  </li>
                  <li>
                    <Link className="dropdown-item" to="/about/founder">
                      درباره بنیان‌گذار
                    </Link>
                  </li>
                </ul>
              </li>
            </ul>
            
            <div className="d-flex">
              <Link className="btn btn-outline-primary me-2" to="/login">
                ورود
              </Link>
              <Link className="btn btn-primary" to="/signup">
                ثبت‌نام
              </Link>
            </div>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
