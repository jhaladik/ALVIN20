// File: src/App.tsx
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import SceneManager from './pages/SceneManager';
import Settings from './pages/Settings';
import Layout from './components/layout/Layout';
import NotFound from './pages/NotFound';
import { Suspense, lazy } from 'react';
import LoadingSpinner from './components/ui/LoadingSpinner';

// Lazy-loaded routes for better performance
const SceneEditor = lazy(() => import('./pages/SceneEditor'));
const StoryEditor = lazy(() => import('./pages/StoryPhase'));
const ObjectManager = lazy(() => import('./pages/ObjectManager'));
const AIWorkshop = lazy(() => import('./pages/AIFeaturesPage'));

function App() {
  const { isAuthenticated, isLoading } = useAuth();
  
  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
      <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />
      
      {/* Protected routes */}
      <Route element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/:projectId" element={<ProjectDetail />} />
        
        {/* Scene management routes */}
        <Route path="/projects/:projectId/scenes" element={<SceneManager />} />
        <Route path="/projects/:projectId/scenes/:sceneId" element={
          <Suspense fallback={<LoadingSpinner />}>
            <SceneEditor />
          </Suspense>
        } />
        
        {/* Other project-related routes */}
        <Route path="/projects/:projectId/story" element={
          <Suspense fallback={<LoadingSpinner />}>
            <StoryEditor />
          </Suspense>
        } />
        <Route path="/projects/:projectId/objects" element={
          <Suspense fallback={<LoadingSpinner />}>
            <ObjectManager />
          </Suspense>
        } />
        <Route path="/projects/:projectId/ai" element={
          <Suspense fallback={<LoadingSpinner />}>
            <AIWorkshop />
          </Suspense>
        } />
        
        <Route path="/settings" element={<Settings />} />
      </Route>
      
      {/* Fallback routes */}
      <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;