import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HelmetProvider } from 'react-helmet-async';
import { SnackbarProvider } from 'notistack';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { I18nProvider } from './contexts/I18nContext';
import { AdminThemeProvider } from './contexts/AdminThemeContext';
import MUIProvider from './components/MUIProvider';

// Components
import Layout from './components/Layout/Layout';
import Home from './pages/Home/Home';
import Blog from './pages/Blog/Blog';
import PostDetail from './pages/Blog/PostDetail';
import Dashboard from './pages/Dashboard/Dashboard';
import Login from './pages/Auth/Login';
import Signup from './pages/Auth/Signup';
import Tests from './pages/Tests/Tests';
import TestDetail from './pages/Tests/TestDetail';
import Courses from './pages/Courses/Courses';
import CourseDetail from './pages/Courses/CourseDetail';
import Profile from './pages/Dashboard/Profile';
import Settings from './pages/Dashboard/Settings';
import Notifications from './pages/Dashboard/Notifications';
import Cart from './pages/Payment/Cart';
import Checkout from './pages/Payment/Checkout';
import PaymentSuccess from './pages/Payment/Success';
import PaymentCancel from './pages/Payment/Cancel';
import TestSession from './pages/Tests/TestSession';
import AboutFounder from './pages/About/AboutFounder';
import AboutInstitute from './pages/About/AboutInstitute';
import Terms from './pages/Terms/Terms';
import AdminDashboard from './pages/Admin/AdminDashboard';
import NotFound from './pages/NotFound/NotFound';
import RedirectComponent from './components/Redirect/RedirectComponent';
import Workshops from './pages/Workshops/Workshops';
import WorkshopDetail from './pages/Workshops/WorkshopDetail';
import WorkshopSession from './pages/Workshops/WorkshopSession';
import WorkshopVideos from './pages/Workshops/WorkshopVideos';
import Packages from './pages/Packages/Packages';
import PackageDetail from './pages/Packages/PackageDetail';
import FinancialReport from './pages/Dashboard/FinancialReport';
import MyWorkshops from './pages/Dashboard/MyWorkshops';
import AppointmentBookingMUI from './pages/Appointments/AppointmentBookingMUI';
import AppointmentsList from './pages/Appointments/AppointmentsList';
import Therapists from './pages/Therapists/Therapists';
import TherapistProfile from './pages/Therapists/TherapistProfile';
import Coach from './pages/Coach/Coach';

// Admin Panel
import AdminLayout from './pages/AdminPanel/AdminLayout';
import DashboardOverview from './pages/AdminPanel/Dashboard/DashboardOverview';
import UsersList from './pages/AdminPanel/Users/UsersList';
import CoursesList from './pages/AdminPanel/Courses/CoursesList';
import AdminPayments from './pages/AdminPanel/Payments/Payments';

// Blog Management
import BlogList from './pages/AdminPanel/Blog/BlogList';
import BlogForm from './pages/AdminPanel/Blog/BlogForm';
import BlogPreview from './pages/AdminPanel/Blog/BlogPreview';
import CategoriesManager from './pages/AdminPanel/Blog/CategoriesManager';
import TagsManager from './pages/AdminPanel/Blog/TagsManager';
import CommentsModeration from './pages/AdminPanel/Blog/CommentsModeration';

// Workshop Management
import WorkshopsList from './pages/AdminPanel/Workshops/WorkshopsList';
import WorkshopParticipants from './pages/AdminPanel/Workshops/WorkshopParticipants';

// Package Management
import PackagesList from './pages/AdminPanel/Packages/PackagesList';
import PackageForm from './pages/AdminPanel/Packages/PackageForm';
import AdminPackageDetail from './pages/AdminPanel/Packages/PackageDetail';
import PackageCategoriesManager from './pages/AdminPanel/Packages/PackageCategoriesManager';

// Appointment Management
import AdminAppointmentsList from './pages/AdminPanel/Appointments/AppointmentsList';
import ChatManager from './pages/AdminPanel/Chat/ChatManager';

// Notifications
import AdminNotificationsList from './pages/AdminPanel/Notifications/NotificationsList';

// Styles
import 'bootstrap/dist/css/bootstrap.rtl.min.css';
import './App.css';

// BlogPreview wrapper component for routing
const BlogPreviewWrapper = () => {
  const { id } = useParams();
  const [open, setOpen] = React.useState(true);
  
  return (
    <BlogPreview
      open={open}
      onClose={() => setOpen(false)}
      post={null} // This should be fetched based on the id
    />
  );
};

// Suppress findDOMNode warnings globally
const originalError = console.error;
const originalWarn = console.warn;

console.error = (...args: any[]) => {
  const message = args[0];
  if (typeof message === 'string' && message.includes('findDOMNode')) {
    return;
  }
  originalError.apply(console, args);
};

console.warn = (...args: any[]) => {
  const message = args[0];
  if (typeof message === 'string' && message.includes('findDOMNode')) {
    return;
  }
  originalWarn.apply(console, args);
};

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  // CSRF token is fetched by AuthContext, no need to fetch here
  // This prevents duplicate requests

  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'center' }}>
          <I18nProvider>
            <ThemeProvider>
              <MUIProvider>
                <AuthProvider>
                  <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                    <div className="App">
                      <Routes>
                      {/* Admin Panel Routes - Separate from main layout */}
                      <Route path="/admin-panel" element={<AdminThemeProvider><AdminLayout /></AdminThemeProvider>}>
                        <Route index element={<DashboardOverview />} />
                        <Route path="users" element={<UsersList />} />
                        <Route path="courses" element={<CoursesList />} />
                        
                        {/* Blog Management Routes */}
                        <Route path="blog" element={<BlogList />} />
                        <Route path="blog/new" element={<BlogForm />} />
                        <Route path="blog/:id" element={<BlogPreviewWrapper />} />
                        <Route path="blog/:id/edit" element={<BlogForm />} />
                        <Route path="blog/categories" element={<CategoriesManager />} />
                        <Route path="blog/tags" element={<TagsManager />} />
                        <Route path="blog/comments" element={<CommentsModeration />} />
                        
                        {/* Workshop Management Routes */}
                        <Route path="workshops" element={<WorkshopsList />} />
                        <Route path="workshops/:id/participants" element={<WorkshopParticipants />} />
                        
                        {/* Package Management Routes */}
                        <Route path="packages" element={<PackagesList />} />
                        <Route path="packages/new" element={<PackageForm />} />
                        <Route path="packages/:id" element={<AdminPackageDetail />} />
                        <Route path="packages/:id/edit" element={<PackageForm />} />
                        <Route path="packages/categories" element={<PackageCategoriesManager />} />
                        
                        {/* Appointment Management Routes */}
                        <Route path="appointments" element={<AdminAppointmentsList />} />
                        <Route path="chat" element={<ChatManager />} />
                        
                        {/* Payments Management */}
                        <Route path="payments" element={<AdminPayments />} />
                        
                        {/* Notifications */}
                        <Route path="notifications" element={<AdminNotificationsList />} />
                        
                        {/* More admin routes will be added here */}
                      </Route>

                      {/* Main App Routes with Layout */}
                      <Route path="/*" element={
                        <Layout>
                          <Routes>
                            {/* Public Routes */}
                            <Route path="/" element={<Home />} />
                            <Route path="/blog" element={<Blog />} />
                            <Route path="/blog/post/:slug" element={<PostDetail />} />
                            <Route path="/tests" element={<Tests />} />
                            <Route path="/tests/test/:slug" element={<TestDetail />} />
                            <Route path="/courses" element={<Courses />} />
                            <Route path="/courses/course/:slug" element={<CourseDetail />} />
                            <Route path="/workshops" element={<Workshops />} />
                            <Route path="/workshops/:slug" element={<WorkshopDetail />} />
                            <Route path="/workshops/:slug/videos" element={<WorkshopVideos />} />
                            <Route path="/packages" element={<Packages />} />
                            <Route path="/packages/:slug" element={<PackageDetail />} />
                            <Route path="/therapists" element={<Therapists />} />
                            <Route path="/therapists/:id" element={<TherapistProfile />} />
                            <Route path="/coach" element={<Coach />} />
                            <Route path="/appointment/booking" element={<AppointmentBookingMUI />} />
                            <Route path="/appointments" element={<AppointmentsList />} />
                            <Route path="/about/founder" element={<AboutFounder />} />
                            <Route path="/about/institute" element={<AboutInstitute />} />
                            <Route path="/terms" element={<Terms />} />
                            <Route path="/admin" element={<AdminDashboard />} />
                            
                            {/* Redirects for common wrong URLs */}
                            <Route path="/about-founder" element={<Navigate to="/about/founder" replace />} />
                            <Route path="/about-institute" element={<Navigate to="/about/institute" replace />} />
                            <Route path="/aboutfounder" element={<Navigate to="/about/founder" replace />} />
                            <Route path="/aboutinstitute" element={<Navigate to="/about/institute" replace />} />
                            <Route path="/founder" element={<Navigate to="/about/founder" replace />} />
                            <Route path="/institute" element={<Navigate to="/about/institute" replace />} />
                            <Route path="/about_founder" element={<Navigate to="/about/founder" replace />} />
                            <Route path="/about_institute" element={<Navigate to="/about/institute" replace />} />
                            <Route path="/about" element={<Navigate to="/about/institute" replace />} />
                            <Route path="/sessions" element={<Navigate to="/appointment/booking" replace />} />
                            
                            {/* More common redirects */}
                            <Route path="/blog/posts" element={<Navigate to="/blog" replace />} />
                            <Route path="/post/:slug" element={<RedirectComponent to="/blog/post/:slug" />} />
                            <Route path="/test" element={<Navigate to="/tests" replace />} />
                            <Route path="/test/:slug" element={<RedirectComponent to="/tests/test/:slug" />} />
                            <Route path="/course" element={<Navigate to="/courses" replace />} />
                            <Route path="/course/:slug" element={<RedirectComponent to="/courses/course/:slug" />} />
                            <Route path="/accounts/login" element={<Navigate to="/login" replace />} />
                            <Route path="/accounts/signup" element={<Navigate to="/signup" replace />} />
                            <Route path="/accounts/register" element={<Navigate to="/signup" replace />} />
                            <Route path="/register" element={<Navigate to="/signup" replace />} />
                            <Route path="/signin" element={<Navigate to="/login" replace />} />
                            
                            {/* Auth Routes */}
                            <Route path="/login" element={<Login />} />
                            <Route path="/signup" element={<Signup />} />
                            
                            {/* Protected Routes */}
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/dashboard/profile" element={<Profile />} />
                            <Route path="/dashboard/settings" element={<Settings />} />
                            <Route path="/dashboard/notifications" element={<Notifications />} />
                            <Route path="/dashboard/financial-report" element={<FinancialReport />} />
                            <Route path="/financial-reports" element={<Navigate to="/dashboard/financial-report" replace />} />
                            <Route path="/dashboard/my-workshops" element={<MyWorkshops />} />
                            <Route path="/payment/cart" element={<Cart />} />
                            <Route path="/payment/checkout" element={<Checkout />} />
                            <Route path="/payment/success" element={<PaymentSuccess />} />
                            <Route path="/payment/cancel" element={<PaymentCancel />} />
                            <Route path="/tests/session/:sessionId" element={<TestSession />} />
                            <Route path="/workshops/session/:sessionId" element={<WorkshopSession />} />
                            
                            {/* 404 */}
                            <Route path="*" element={<NotFound />} />
                          </Routes>
                        </Layout>
                      } />
                    </Routes>
                  </div>
                </Router>
              </AuthProvider>
              </MUIProvider>
            </ThemeProvider>
          </I18nProvider>
        </SnackbarProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App;