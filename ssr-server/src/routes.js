import React from 'react';
import { Routes, Route } from 'react-router-dom';

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

// Route configuration for both server and client
export const routes = [
  { path: '/', component: Home },
  { path: '/blog', component: Blog },
  { path: '/blog/post/:slug', component: PostDetail },
  { path: '/blog/category/:slug', component: CategoryArchive },
  { path: '/blog/tag/:slug', component: TagArchive },
  { path: '/blog/search', component: Blog },
  { path: '/workshops', component: Workshops },
  { path: '/workshops/:slug', component: WorkshopDetail },
  { path: '/courses', component: Courses },
  { path: '/courses/course/:slug', component: CourseDetail },
  { path: '/packages', component: Packages },
  { path: '/packages/:slug', component: PackageDetail },
  { path: '/therapists', component: Therapists },
  { path: '/therapists/:id', component: TherapistDetail },
  { path: '/about/founder', component: AboutFounder },
  { path: '/about/institute', component: AboutInstitute }
];

// React Router Routes component
export const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/blog" element={<Blog />} />
      <Route path="/blog/post/:slug" element={<PostDetail />} />
      <Route path="/blog/category/:slug" element={<CategoryArchive />} />
      <Route path="/blog/tag/:slug" element={<TagArchive />} />
      <Route path="/blog/search" element={<Blog />} />
      <Route path="/workshops" element={<Workshops />} />
      <Route path="/workshops/:slug" element={<WorkshopDetail />} />
      <Route path="/courses" element={<Courses />} />
      <Route path="/courses/course/:slug" element={<CourseDetail />} />
      <Route path="/packages" element={<Packages />} />
      <Route path="/packages/:slug" element={<PackageDetail />} />
      <Route path="/therapists" element={<Therapists />} />
      <Route path="/therapists/:id" element={<TherapistDetail />} />
      <Route path="/about/founder" element={<AboutFounder />} />
      <Route path="/about/institute" element={<AboutInstitute />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default AppRoutes;
