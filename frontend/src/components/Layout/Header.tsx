import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

interface HeaderProps {
  user?: any;
  isAuthenticated?: boolean;
  onLogout?: () => void;
}

const Header: React.FC<HeaderProps> = ({ user, isAuthenticated, onLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const profileDropdownRef = useRef<HTMLDivElement>(null);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  const toggleProfileDropdown = () => setIsProfileDropdownOpen(!isProfileDropdownOpen);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileDropdownRef.current && !profileDropdownRef.current.contains(event.target as Node)) {
        setIsProfileDropdownOpen(false);
      }
    };

    if (isProfileDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isProfileDropdownOpen]);

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          {/* Logo */}
          <div className="header-logo">
            <Link to="/" className="logo-link">
              <div className="logo-container">
                <img 
                  src="/images/1744027219152.png" 
                  alt="مرکز مشاوره سرمد" 
                  className="logo-image"
                  loading="eager"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                    if (nextElement) {
                      nextElement.style.display = 'flex';
                    }
                  }}
                />
                <div className="logo-fallback" style={{ display: 'none' }}>
                  <i className="fas fa-heart"></i>
                </div>
              </div>
              <div className="logo-text">
                <h1 className="logo-title">مرکز مشاوره سرمد</h1>
                <p className="logo-subtitle">ارائه برترین خدمات روانشناسی</p>
              </div>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="header-nav">
            <ul className="nav-list">
              <li><Link to="/" className="nav-link">خانه</Link></li>
              <li><Link to="/blog" className="nav-link">وبلاگ</Link></li>
              <li><Link to="/tests" className="nav-link">تستها</Link></li>
              <li><Link to="/workshops" className="nav-link">کارگاه ها</Link></li>
              <li><Link to="/packages" className="nav-link">پکیج های آموزشی</Link></li>
              <li><Link to="/therapists" className="nav-link">درمانگران</Link></li>
              <li><Link to="/about" className="nav-link">درباره ما</Link></li>
            </ul>
          </nav>

          {/* User Actions */}
          <div className="header-actions">
            {/* User Section */}
            {isAuthenticated && user ? (
              <div className="user-section dropdown" ref={profileDropdownRef}>
                <button 
                  className="user-profile-button"
                  onClick={toggleProfileDropdown}
                  aria-expanded={isProfileDropdownOpen}
                >
                  <div className="user-avatar">
                    <img 
                      src={user.profile_image || "/images/default-avatar.png"} 
                      alt="User Avatar" 
                      loading="lazy"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                        const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                        if (nextElement) {
                          nextElement.style.display = 'flex';
                        }
                      }}
                    />
                    <div className="avatar-placeholder">
                      <i className="fas fa-user"></i>
                    </div>
                  </div>
                  <span className="user-name">{user.full_name || `${user.first_name} ${user.last_name}`}</span>
                  <i className="fas fa-chevron-down dropdown-arrow"></i>
                </button>
                
                {isProfileDropdownOpen && (
                  <div className="profile-dropdown-menu">
                    <div className="dropdown-header">
                      <div className="dropdown-user-info">
                        <div className="dropdown-avatar">
                          <img 
                            src={user.profile_image || "/images/default-avatar.png"} 
                            alt="User Avatar" 
                            loading="lazy"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              const nextElement = e.currentTarget.nextElementSibling as HTMLElement;
                              if (nextElement) {
                                nextElement.style.display = 'flex';
                              }
                            }}
                          />
                          <div className="avatar-placeholder">
                            <i className="fas fa-user"></i>
                          </div>
                        </div>
                        <div className="dropdown-user-details">
                          <span className="dropdown-user-name">{user.full_name || `${user.first_name} ${user.last_name}`}</span>
                          <span className="dropdown-user-role">{user.user_type === 'admin' ? 'مدیر سیستم' : 'کاربر'}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="dropdown-divider"></div>
                    
                    <div className="dropdown-items">
                      <Link to="/dashboard/profile" className="dropdown-item profile-item" onClick={toggleProfileDropdown}>
                        <div className="dropdown-item-icon profile-icon">
                          <i className="fas fa-user-circle"></i>
                        </div>
                        <div className="dropdown-item-content">
                          <span className="dropdown-item-title">پروفایل</span>
                          <span className="dropdown-item-subtitle">مدیریت اطلاعات شخصی</span>
                        </div>
                      </Link>
                      
                      <Link to="/dashboard" className="dropdown-item dashboard-item" onClick={toggleProfileDropdown}>
                        <div className="dropdown-item-icon dashboard-icon">
                          <i className="fas fa-chart-line"></i>
                        </div>
                        <div className="dropdown-item-content">
                          <span className="dropdown-item-title">داشبورد</span>
                          <span className="dropdown-item-subtitle">نمای کلی فعالیت‌ها</span>
                        </div>
                      </Link>
                      
                      {user.user_type === 'admin' && (
                        <>
                          <div className="dropdown-divider"></div>
                          <Link to="/admin-panel" className="dropdown-item admin-item" onClick={toggleProfileDropdown}>
                            <div className="dropdown-item-icon admin-icon">
                              <i className="fas fa-shield-alt"></i>
                            </div>
                            <div className="dropdown-item-content">
                              <span className="dropdown-item-title">پنل مدیریت</span>
                              <span className="dropdown-item-subtitle">مدیریت سیستم</span>
                            </div>
                          </Link>
                        </>
                      )}
                      
                      <div className="dropdown-divider"></div>
                      <button className="dropdown-item logout-item" onClick={() => {
                        if (onLogout) onLogout();
                        toggleProfileDropdown();
                      }}>
                        <div className="dropdown-item-icon logout-icon">
                          <i className="fas fa-power-off"></i>
                        </div>
                        <div className="dropdown-item-content">
                          <span className="dropdown-item-title">خروج</span>
                          <span className="dropdown-item-subtitle">خروج از حساب کاربری</span>
                        </div>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="auth-section">
                <Link to="/login" className="auth-link">ورود</Link>
                <Link to="/signup" className="auth-link primary">ثبت نام</Link>
              </div>
            )}

            {/* Mobile Menu Toggle */}
            <button 
              className="mobile-toggle"
              onClick={toggleMenu}
              aria-label="منوی موبایل"
            >
              <span className={`hamburger-line ${isMenuOpen ? 'active' : ''}`}></span>
              <span className={`hamburger-line ${isMenuOpen ? 'active' : ''}`}></span>
              <span className={`hamburger-line ${isMenuOpen ? 'active' : ''}`}></span>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="mobile-menu">
            <nav className="mobile-nav">
              <ul className="mobile-nav-list">
                <li><Link to="/" onClick={toggleMenu}>خانه</Link></li>
                <li><Link to="/blog" onClick={toggleMenu}>وبلاگ</Link></li>
                <li><Link to="/tests" onClick={toggleMenu}>تستها</Link></li>
                <li><Link to="/workshops" onClick={toggleMenu}>کارگاه ها</Link></li>
                <li><Link to="/packages" onClick={toggleMenu}>پکیج های آموزشی</Link></li>
                <li><Link to="/therapists" onClick={toggleMenu}>درمانگران</Link></li>
                <li><Link to="/about" onClick={toggleMenu}>درباره ما</Link></li>
              </ul>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
