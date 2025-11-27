import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';
import { useTheme } from '../../contexts/ThemeContext';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, isAuthenticated, logout } = useAuth();
  const { t, language } = useI18n();
  const { theme } = useTheme();

  return (
    <>
      <Helmet>
        <html lang={language} dir="rtl" />
        <title>{t('home.title')}</title>
        <meta name="description" content={t('home.subtitle')} />
        <meta name="theme-color" content="#2c5aa0" />
        <link rel="preconnect" href="https://cdn.jsdelivr.net" />
        <link
          href="https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css"
          rel="stylesheet"
        />
        <link
          href="https://cdn.jsdelivr.net/gh/rastikerdar/samim-font@v4.0.2/dist/font-face.css"
          rel="stylesheet"
        />
        <link
          href="https://cdn.jsdelivr.net/gh/rastikerdar/shabnam-font@v5.0.1/dist/font-face.css"
          rel="stylesheet"
        />
      </Helmet>
      
      <div className="layout" data-theme={theme}>
        <Header 
          user={user} 
          isAuthenticated={isAuthenticated} 
          onLogout={logout}
        />
        
        <main className="main-content">
          {children}
        </main>
        
        <Footer />
      </div>
    </>
  );
};

export default Layout;
