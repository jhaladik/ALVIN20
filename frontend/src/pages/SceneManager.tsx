// File: src/pages/SceneManager.tsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Scene } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Button from '../components/ui/Button.tsx';
import KanbanBoard from '../components/scenes/KanbanBoard.tsx';
import TimelineView from '../components/scenes/TimelineView';
import { useSocket } from '../hooks/useSocket';
import {
  ArrowLeftIcon,
  Squares2X2Icon, // Replacement for ViewBoardsIcon
  ListBulletIcon, // Replacement for ViewListIcon
  PlusIcon,
  MagnifyingGlassIcon, // Replacement for SearchIcon
  ArrowDownTrayIcon, // Replacement for DownloadIcon
  ArrowPathIcon, // Replacement for RefreshIcon
  SparklesIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';

type ViewMode = 'kanban' | 'timeline';

const SceneManager = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { socket, isConnected } = useSocket();
  
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>('kanban');
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isGeneratingScenes, setIsGeneratingScenes] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');
  
  // Load scenes for the current project
  useEffect(() => {
    const loadScenes = async () => {
      if (!projectId) return;
      
      try {
        setIsLoading(true);
        const response = await api.get(`/api/projects/${projectId}/scenes`);
        setScenes(response.data);
        setError('');
      } catch (err) {
        console.error('Failed to load scenes', err);
        setError('Failed to load scenes. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadScenes();
  }, [projectId]);
  
  // Setup real-time socket for collaborative editing
  useEffect(() => {
    if (!socket || !isConnected || !projectId) return;
    
    // Join project room
    socket.emit('join_project', { projectId });
    
    // Listen for scene updates
    socket.on('scene_updated', (updatedScene: Scene) => {
      setScenes(prev => 
        prev.map(scene => scene.id === updatedScene.id ? updatedScene : scene)
      );
    });
    
    // Listen for scene creations
    socket.on('scene_created', (newScene: Scene) => {
      setScenes(prev => [...prev, newScene]);
    });
    
    // Listen for scene deletions
    socket.on('scene_deleted', (deletedSceneId: string) => {
      setScenes(prev => prev.filter(scene => scene.id !== deletedSceneId));
    });
    
    return () => {
      socket.off('scene_updated');
      socket.off('scene_created');
      socket.off('scene_deleted');
      socket.emit('leave_project', { projectId });
    };
  }, [socket, isConnected, projectId]);
  
  // Handle scene ordering change
  const handleSceneOrderChange = async (sceneOrder: { id: string, order: number, sceneType?: string }[]) => {
    if (!projectId) return;
    
    try {
      setIsUpdating(true);
      await api.post(`/api/projects/${projectId}/scenes/reorder`, { scenes: sceneOrder });
      
      // Update scenes locally (refresh from API to ensure consistency)
      const response = await api.get(`/api/projects/${projectId}/scenes`);
      setScenes(response.data);
    } catch (err) {
      console.error('Failed to update scene order', err);
      showError('Failed to update scene order');
    } finally {
      setIsUpdating(false);
    }
  };
  
  // Handle creating a new scene
  const handleCreateScene = () => {
    navigate(`/projects/${projectId}/scenes/new`);
  };
  
  // Generate scenes with AI
  const handleGenerateScenes = async () => {
    if (!projectId) return;
    
    try {
      setIsGeneratingScenes(true);
      const response = await api.post(`/api/projects/${projectId}/ai/generate-scenes`);
      setScenes(prev => [...prev, ...response.data]);
      showSuccess('Generated scenes successfully');
    } catch (err) {
      console.error('Failed to generate scenes', err);
      showError('Failed to generate scenes');
    } finally {
      setIsGeneratingScenes(false);
    }
  };
  
  // Export scenes
  const handleExport = async () => {
    if (!projectId) return;
    
    try {
      const response = await api.get(`/api/projects/${projectId}/scenes/export`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `scenes-${projectId}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to export scenes', err);
      showError('Failed to export scenes');
    }
  };
  
  // Filter scenes based on search query
  const filteredScenes = scenes.filter(scene => 
    scene.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (scene.description && scene.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );
  
  // Helper to show error message
  const showError = (message: string) => {
    setError(message);
    setTimeout(() => setError(''), 5000);
  };
  
  // Helper to show success message (placeholder for a toast system)
  const showSuccess = (message: string) => {
    console.log('Success:', message);
    // In a real app, you would show a toast notification
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center">
            <button
              className="text-gray-500 hover:text-gray-700 mr-2"
              onClick={() => navigate(`/projects/${projectId}`)}
            >
              <ArrowLeftIcon className="h-5 w-5" />
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Scene Manager</h1>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Organize and edit the scenes of your story
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button onClick={handleCreateScene}>
            <PlusIcon className="h-5 w-5 mr-1" />
            Add Scene
          </Button>
          
          <Button 
            variant="secondary"
            onClick={handleGenerateScenes}
            isLoading={isGeneratingScenes}
          >
            <SparklesIcon className="h-5 w-5 mr-1" />
            Generate Scenes
          </Button>
        </div>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-start">
          <ExclamationCircleIcon className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}
      
      {/* Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          {/* View toggle */}
          <div className="bg-gray-100 rounded-lg p-1 flex space-x-1">
            <button
              className={`px-3 py-1.5 rounded text-sm flex items-center ${
                viewMode === 'kanban' 
                  ? 'bg-white shadow-sm' 
                  : 'text-gray-600'
              }`}
              onClick={() => setViewMode('kanban')}
            >
              <Squares2X2Icon className="h-4 w-4 mr-1.5" />
              Kanban
            </button>
            <button
              className={`px-3 py-1.5 rounded text-sm flex items-center ${
                viewMode === 'timeline' 
                  ? 'bg-white shadow-sm' 
                  : 'text-gray-600'
              }`}
              onClick={() => setViewMode('timeline')}
            >
              <ListBulletIcon className="h-4 w-4 mr-1.5" />
              Timeline
            </button>
          </div>
          
          {/* Export button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleExport}
            disabled={!scenes.length}
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
            Export
          </Button>
        </div>
        
        {/* Search */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="input-standard pl-10 w-64"
            placeholder="Search scenes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>
      
      {/* Scene count */}
      <div className="text-sm text-gray-500">
        {filteredScenes.length} {filteredScenes.length === 1 ? 'scene' : 'scenes'} 
        {searchQuery && ` matching "${searchQuery}"`}
        
        {searchQuery && (
          <button
            className="ml-2 text-indigo-600 hover:text-indigo-500"
            onClick={() => setSearchQuery('')}
          >
            Clear search
          </button>
        )}
      </div>
      
      {/* Scene view */}
      {filteredScenes.length > 0 ? (
        viewMode === 'kanban' ? (
          <KanbanBoard
            projectId={projectId || ''}
            scenes={filteredScenes}
            onSceneOrderChange={handleSceneOrderChange}
          />
        ) : (
          <TimelineView
            projectId={projectId || ''}
            scenes={filteredScenes}
            onSceneOrderChange={handleSceneOrderChange}
          />
        )
      ) : (
        <div className="text-center py-16 border border-dashed border-gray-300 rounded-md">
          <SparklesIcon className="h-12 w-12 text-gray-400 mx-auto" />
          <h3 className="mt-4 text-sm font-medium text-gray-900">
            {searchQuery 
              ? 'No scenes match your search' 
              : 'No scenes created yet'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery 
              ? 'Try a different search term' 
              : 'Get started by creating your first scene'}
          </p>
          <div className="mt-6 flex justify-center space-x-3">
            <Button onClick={handleCreateScene}>
              <PlusIcon className="h-5 w-5 mr-1" />
              Add Scene
            </Button>
            <Button
              variant="secondary"
              onClick={handleGenerateScenes}
              isLoading={isGeneratingScenes}
            >
              <SparklesIcon className="h-5 w-5 mr-1" />
              Generate Scenes
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SceneManager;