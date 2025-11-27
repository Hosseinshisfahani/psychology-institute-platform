import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translation resources
const resources = {
  fa: {
    translation: {
      // Navigation
      'nav.home': 'خانه',
      'nav.blog': 'وبلاگ',
      'nav.tests': 'تست‌های روانشناسی',
      'nav.courses': 'بسته‌های آموزشی',
      'nav.dashboard': 'داشبورد',
      'nav.profile': 'پروفایل',
      'nav.adminPanel': 'پنل مدیریت',
      'nav.login': 'ورود',
      'nav.signup': 'ثبت‌نام',
      'nav.logout': 'خروج',
      
      // Home page
      'home.title': 'مرکز مشاوره و خدمات روانشناسی سرمد',
      'home.subtitle': 'ارائه خدمات روانشناسی و مشاوره آنلاین با بالاترین کیفیت و تخصص. ما در کنار شما هستیم تا زندگی بهتری داشته باشید.',
      'home.cta.tests': 'تست‌های روانشناسی',
      'home.cta.courses': 'بسته‌های آموزشی',
      'home.cta.sessions': 'جلسات آنلاین',
      'home.services.title': 'خدمات ما',
      'home.services.tests': 'تست‌های روانشناسی',
      'home.services.tests.desc': 'تست‌های معتبر و علمی برای شناخت بهتر خودتان',
      'home.services.courses': 'بسته‌های آموزشی',
      'home.services.courses.desc': 'بسته‌های تخصصی روانشناسی و مشاوره',
      'home.services.sessions': 'نوبت دهی آنلاین',
      'home.services.sessions.desc': 'رزرو نوبت آنلاین با بهترین متخصصان',
      'home.services.articles': 'مقالات تخصصی',
      'home.services.articles.desc': 'آخرین مقالات و مطالب روانشناسی',
      'home.stats.tests': 'تست روانشناسی',
      'home.stats.courses': 'بسته آموزشی',
      'home.stats.therapists': 'متخصص روانشناسی',
      'home.stats.users': 'کاربر راضی',
      'home.latest_posts': 'آخرین مقالات',
      'home.newsletter.title': 'عضویت در خبرنامه',
      'home.newsletter.desc': 'از آخرین مقالات و مطالب ما باخبر شوید',
      'home.newsletter.placeholder': 'ایمیل شما',
      'home.newsletter.subscribe': 'عضویت',
      'home.quick_links': 'دسترسی سریع',
      'home.quick_links.free_tests': 'تست‌های رایگان',
      'home.quick_links.free_courses': 'بسته‌های رایگان',
      'home.quick_links.therapists': 'متخصصان ما',
      'home.quick_links.contact': 'تماس با ما',
      
      // Blog
      'blog.title': 'وبلاگ',
      'blog.read_more': 'ادامه مطلب',
      'blog.author': 'نویسنده',
      'blog.views': 'بازدید',
      'blog.comments': 'نظرات',
      'blog.likes': 'لایک',
      'blog.search': 'جستجو',
      'blog.categories': 'دسته‌بندی‌ها',
      'blog.tags': 'برچسب‌ها',
      'blog.no_posts': 'هیچ مقاله‌ای یافت نشد',
      
      // Dashboard
      'dashboard.welcome': 'خوش آمدید',
      'dashboard.stats.enrolled_courses': 'بسته‌های ثبت‌نام شده',
      'dashboard.stats.completed_tests': 'تست‌های تکمیل شده',
      'dashboard.stats.upcoming_sessions': 'جلسات پیش رو',
      'dashboard.stats.certificates': 'گواهینامه‌ها',
      'dashboard.recent_activities': 'فعالیت‌های اخیر',
      'dashboard.quick_actions': 'دسترسی سریع',
      'dashboard.quick_actions.search_course': 'جستجوی بسته',
      'dashboard.quick_actions.take_test': 'انجام تست',
      'dashboard.quick_actions.book_session': 'رزرو جلسه',
      'dashboard.quick_actions.read_articles': 'مطالب روانشناسی',
      'dashboard.notifications': 'اعلان‌های جدید',
      'dashboard.notifications.view_all': 'مشاهده همه',
      'dashboard.no_activities': 'هیچ فعالیتی یافت نشد',
      'dashboard.no_notifications': 'اعلان جدیدی ندارید',
      
      // Auth
      'auth.login.title': 'ورود به حساب کاربری',
      'auth.login.email': 'ایمیل',
      'auth.login.password': 'رمز عبور',
      'auth.login.submit': 'ورود',
      'auth.login.forgot_password': 'فراموشی رمز عبور',
      'auth.login.no_account': 'حساب کاربری ندارید؟',
      'auth.login.signup_link': 'ثبت‌نام کنید',
      'auth.signup.title': 'ثبت‌نام',
      'auth.signup.email': 'ایمیل',
      'auth.signup.password': 'رمز عبور',
      'auth.signup.confirm_password': 'تکرار رمز عبور',
      'auth.signup.first_name': 'نام',
      'auth.signup.last_name': 'نام خانوادگی',
      'auth.signup.submit': 'ثبت‌نام',
      'auth.signup.have_account': 'حساب کاربری دارید؟',
      'auth.signup.login_link': 'وارد شوید',
      
      // Common
      'common.loading': 'در حال بارگذاری...',
      'common.error': 'خطا',
      'common.success': 'موفق',
      'common.save': 'ذخیره',
      'common.cancel': 'لغو',
      'common.edit': 'ویرایش',
      'common.delete': 'حذف',
      'common.view': 'مشاهده',
      'common.back': 'بازگشت',
      'common.next': 'بعدی',
      'common.previous': 'قبلی',
      'common.submit': 'ارسال',
      'common.search': 'جستجو',
      'common.filter': 'فیلتر',
      'common.sort': 'مرتب‌سازی',
      'common.date': 'تاریخ',
      'common.time': 'زمان',
      'common.status': 'وضعیت',
      'common.actions': 'عملیات',
    }
  },
  en: {
    translation: {
      // Navigation
      'nav.home': 'Home',
      'nav.blog': 'Blog',
      'nav.tests': 'Psychological Tests',
      'nav.courses': 'Courses',
      'nav.dashboard': 'Dashboard',
      'nav.profile': 'Profile',
      'nav.adminPanel': 'Admin Panel',
      'nav.login': 'Login',
      'nav.signup': 'Sign Up',
      'nav.logout': 'Logout',
      
      // Home page
      'home.title': 'Sarmad Psychology Institute',
      'home.subtitle': 'Providing psychology and counseling services online with the highest quality and expertise. We are with you to have a better life.',
      'home.cta.tests': 'Psychological Tests',
      'home.cta.courses': 'Educational Courses',
      'home.cta.sessions': 'Online Sessions',
      'home.services.title': 'Our Services',
      'home.services.tests': 'Psychological Tests',
      'home.services.tests.desc': 'Valid and scientific tests for better self-knowledge',
      'home.services.courses': 'Educational Courses',
      'home.services.courses.desc': 'Specialized psychology and counseling courses',
      'home.services.sessions': 'Online Appointment Booking',
      'home.services.sessions.desc': 'Book online appointments with the best specialists',
      'home.services.articles': 'Specialized Articles',
      'home.services.articles.desc': 'Latest psychology articles and materials',
      'home.stats.tests': 'Psychological Tests',
      'home.stats.courses': 'Educational Courses',
      'home.stats.therapists': 'Psychology Specialists',
      'home.stats.users': 'Satisfied Users',
      'home.latest_posts': 'Latest Articles',
      'home.newsletter.title': 'Newsletter Subscription',
      'home.newsletter.desc': 'Stay updated with our latest articles and materials',
      'home.newsletter.placeholder': 'Your Email',
      'home.newsletter.subscribe': 'Subscribe',
      'home.quick_links': 'Quick Links',
      'home.quick_links.free_tests': 'Free Tests',
      'home.quick_links.free_courses': 'Free Courses',
      'home.quick_links.therapists': 'Our Specialists',
      'home.quick_links.contact': 'Contact Us',
      
      // Blog
      'blog.title': 'Blog',
      'blog.read_more': 'Read More',
      'blog.author': 'Author',
      'blog.views': 'Views',
      'blog.comments': 'Comments',
      'blog.likes': 'Likes',
      'blog.search': 'Search',
      'blog.categories': 'Categories',
      'blog.tags': 'Tags',
      'blog.no_posts': 'No articles found',
      
      // Dashboard
      'dashboard.welcome': 'Welcome',
      'dashboard.stats.enrolled_courses': 'Enrolled Courses',
      'dashboard.stats.completed_tests': 'Completed Tests',
      'dashboard.stats.upcoming_sessions': 'Upcoming Sessions',
      'dashboard.stats.certificates': 'Certificates',
      'dashboard.recent_activities': 'Recent Activities',
      'dashboard.quick_actions': 'Quick Actions',
      'dashboard.quick_actions.search_course': 'Search Course',
      'dashboard.quick_actions.take_test': 'Take Test',
      'dashboard.quick_actions.book_session': 'Book Session',
      'dashboard.quick_actions.read_articles': 'Psychology Articles',
      'dashboard.notifications': 'New Notifications',
      'dashboard.notifications.view_all': 'View All',
      'dashboard.no_activities': 'No activities found',
      'dashboard.no_notifications': 'No new notifications',
      
      // Auth
      'auth.login.title': 'Login to Your Account',
      'auth.login.email': 'Email',
      'auth.login.password': 'Password',
      'auth.login.submit': 'Login',
      'auth.login.forgot_password': 'Forgot Password',
      'auth.login.no_account': "Don't have an account?",
      'auth.login.signup_link': 'Sign Up',
      'auth.signup.title': 'Sign Up',
      'auth.signup.email': 'Email',
      'auth.signup.password': 'Password',
      'auth.signup.confirm_password': 'Confirm Password',
      'auth.signup.first_name': 'First Name',
      'auth.signup.last_name': 'Last Name',
      'auth.signup.submit': 'Sign Up',
      'auth.signup.have_account': 'Have an account?',
      'auth.signup.login_link': 'Login',
      
      // Common
      'common.loading': 'Loading...',
      'common.error': 'Error',
      'common.success': 'Success',
      'common.save': 'Save',
      'common.cancel': 'Cancel',
      'common.edit': 'Edit',
      'common.delete': 'Delete',
      'common.view': 'View',
      'common.back': 'Back',
      'common.next': 'Next',
      'common.previous': 'Previous',
      'common.submit': 'Submit',
      'common.search': 'Search',
      'common.filter': 'Filter',
      'common.sort': 'Sort',
      'common.date': 'Date',
      'common.time': 'Time',
      'common.status': 'Status',
      'common.actions': 'Actions',
    }
  }
};

// Initialize i18next
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: 'fa', // default language
    fallbackLng: 'fa',
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
  });

interface I18nContextType {
  language: string;
  changeLanguage: (lng: string) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const I18nProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<string>('fa');

  useEffect(() => {
    setLanguage(i18n.language);
  }, []);

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    setLanguage(lng);
  };

  const t = (key: string): string => {
    return i18n.t(key);
  };

  const value: I18nContextType = {
    language,
    changeLanguage,
    t,
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (context === undefined) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};
