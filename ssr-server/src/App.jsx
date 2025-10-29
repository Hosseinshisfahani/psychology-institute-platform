import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

// Layout components
import Layout from './components/Layout/Layout';

// Page components
import Home from './components/Pages/Home';
import Blog from './components/Pages/Blog/Blog';
import PostDetail from './components/Pages/Blog/PostDetail';
import CategoryArchive from './components/Pages/Blog/CategoryArchive';
import TagArchive from './components/Pages/Blog/TagArchive';
import Workshops from './components/Pages/Workshops/Workshops';
import WorkshopDetail from './components/Pages/Workshops/WorkshopDetail';
import Courses from './components/Pages/Courses/Courses';
import CourseDetail from './components/Pages/Courses/CourseDetail';
import Packages from './components/Pages/Packages/Packages';
import PackageDetail from './components/Pages/Packages/PackageDetail';
import Therapists from './components/Pages/Therapists/Therapists';
import TherapistDetail from './components/Pages/Therapists/TherapistDetail';
import AboutFounder from './components/Pages/About/AboutFounder';
import AboutInstitute from './components/Pages/About/AboutInstitute';
import NotFound from './components/Pages/NotFound';

const App = () => {
  return (
    <>
      <Helmet>
        <html lang="fa" dir="rtl" />
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#007bff" />
      </Helmet>
      
      <Layout>
        <Routes>
          {/* Home */}
          <Route path="/" element={<Home />} />
          
          {/* Blog Routes */}
          <Route path="/blog" element={<Blog />} />
          <Route path="/blog/post/:slug" element={<PostDetail />} />
          <Route path="/blog/category/:slug" element={<CategoryArchive />} />
          <Route path="/blog/tag/:slug" element={<TagArchive />} />
          <Route path="/blog/search" element={<Blog />} />
          
          {/* Workshop Routes */}
          <Route path="/workshops" element={<Workshops />} />
          <Route path="/workshops/:slug" element={<WorkshopDetail />} />
          
          {/* Course Routes */}
          <Route path="/courses" element={<Courses />} />
          <Route path="/courses/course/:slug" element={<CourseDetail />} />
          
          {/* Package Routes */}
          <Route path="/packages" element={<Packages />} />
          <Route path="/packages/:slug" element={<PackageDetail />} />
          
          {/* Therapist Routes */}
          <Route path="/therapists" element={<Therapists />} />
          <Route path="/therapists/:id" element={<TherapistDetail />} />
          
          {/* About Routes */}
          <Route path="/about/founder" element={<AboutFounder />} />
          <Route path="/about/institute" element={<AboutInstitute />} />
          
          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </>
  );
};

export default App;



