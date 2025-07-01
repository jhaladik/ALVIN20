// File: src/pages/ProjectDetail.tsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Project, Scene } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Button from '../components/ui/Button';
import EditProjectModal from '../components/projects/EditProjectModal.tsx';
import DeleteProjectModal from '../components/projects/DeleteProjectModal';
import ProjectPhaseSelector from '../components/projects/ProjectPhaseSelector.tsx';
import { useSocket } from '../hooks/useSocket';
import {
  PencilIcon,
  TrashIcon,
  UserIcon,
  ClockIcon,
  DocumentTextIcon,
  // ViewBoardsIcon doesn't exist in current Heroicons version
  // Replacing with appropriate alternatives:
  Squares2X2Icon, // Replacement for ViewBoardsIcon
  CubeIcon,
  SparklesIcon,
  ExclamationCircleIcon,
  ArrowLeftIcon,
  PlusIcon,
  AnnotationIcon
} from '@heroicons/react/24/outline';

const ProjectDetail = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { socket, isConnected } = useSocket();
  
  const [project, setProject] = useState<Project | null>(null);
  const [recentScenes, setRecentScenes] = useState<Scene[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [error, setError] = useState('');
  
  // Load project data
  useEffect(() => {
    const loadProjectData = async () => {
      if (!projectId) return;
      
      try {
        setIsLoading(true);
        
        // Load project and recent scenes in parallel
        const [projectResponse, scenesResponse] = await Promise.all([
          api.get(`/api/projects/${projectId}`),
          api.get(`/api/projects/${projectId}/scenes?limit=5&sort=last_modified`)
        ]);
        
        setProject(projectResponse.data);
        setRecentScenes(scenesResponse.data);
        setError('');
      } catch (err) {
        console.error('Failed to load project data', err);
        setError('Failed to load project data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadProjectData();
  }, [projectId]);
  
  // Socket connection for real-time updates
  useEffect(() => {
    if (!socket || !isConnected || !projectId) return;
    
    // Join project room
    socket.emit('join_project', projectId);
    
    // Listen for project updates
    socket.on('project_updated', (updatedProject: Project) => {
      if (updatedProject.id === projectId) {
        setProject(updatedProject);
      }
    });
    
    // Listen for scene updates
    socket.on('scene_updated', () => {
      // Refresh scenes list
      api.get(`/api/projects/${projectId}/scenes?limit=5&sort=last_modified`)
        .then(response => setRecentScenes(response.data))
        .catch(err => console.error('Failed to refresh scenes', err));
    });
    
    return () => {
      // Leave project room and remove listeners
      socket.emit('leave_project', projectId);
      socket.off('project_updated');
      socket.off('scene_updated');
    };
  }, [socket, isConnected, projectId]);
  
  // Project operations
  const handleUpdateProject = async (updatedProject: Partial<Project>) => {
    if (!projectId || !project) return;
    
    try {
      const response = await api.patch(`/api/projects/${projectId}`, updatedProject);
      setProject({...project, ...response.data});
      setIsEditModalOpen(false);
    } catch (err) {
      console.error('Failed to update project', err);
    }
  };
  
  const handleDeleteProject = async () => {
    if (!projectId) return;
    
    try {
      await api.delete(`/api/projects/${projectId}`);
      navigate('/projects', { replace: true });
    } catch (err) {
      console.error('Failed to delete project', err);
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  if (error || !project) {
    return (
      <div className="text-center py-10">
        <ExclamationCircleIcon className="h-12 w-12 text-red-500 mx-auto" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
        <p className="mt-1 text-sm text-gray-500">{error || 'Project not found'}</p>
        <div className="mt-6">
          <Button onClick={() => navigate('/projects')}>
            <ArrowLeftIcon className="h-5 w-5 mr-1" />
            Back to Projects
          </Button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-5xl mx-auto">
      {/* Project Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
        <div>
          <div className="flex items-center">
            <Link 
              to="/projects" 
              className="text-gray-500 hover:text-gray-700 mr-2"
            >
              <ArrowLeftIcon className="h-5 w-5" />
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">{project.title}</h1>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Created {new Date(project.createdAt).toLocaleDateString()}
          </p>
        </div>
        
        <div className="flex mt-4 sm:mt-0 space-x-2">
          <Button 
            variant="secondary"
            onClick={() => setIsEditModalOpen(true)}
          >
            <PencilIcon className="h-5 w-5 mr-1" />
            Edit
          </Button>
          <Button 
            variant="danger"
            onClick={() => setIsDeleteModalOpen(true)}
          >
            <TrashIcon className="h-5 w-5 mr-1" />
            Delete
          </Button>
        </div>
      </div>
      
      {/* Project Info */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <div className="prose max-w-none">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
            <p className="text-gray-600">
              {project.description || 'No description provided.'}
            </p>
            
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Project Phase</h3>
              <ProjectPhaseSelector 
                currentPhase={project.phase} 
                onPhaseChange={(phase) => handleUpdateProject({ phase })}
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Project Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Recent Scenes</h3>
                <Link 
                  to={`/projects/${projectId}/scenes`}
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  <div className="flex items-center">
                    <Squares2X2Icon className="h-4 w-4 mr-1" /> {/* Using Squares2X2Icon instead of ViewBoardsIcon */}
                    View All Scenes
                  </div>
                </Link>
              </div>
              
              {recentScenes.length > 0 ? (
                <div className="space-y-3">
                  {recentScenes.map(scene => (
                    <Link 
                      key={scene.id}
                      to={`/projects/${projectId}/scenes/${scene.id}`}
                      className="block p-3 border border-gray-200 rounded-md hover:bg-gray-50"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium text-gray-900">{scene.title}</h4>
                          <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                            {scene.description || 'No description'}
                          </p>
                        </div>
                        <div className="text-xs text-gray-400">
                          {new Date(scene.updatedAt).toLocaleDateString()}
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 border border-dashed border-gray-300 rounded-md">
                  <DocumentTextIcon className="h-10 w-10 text-gray-400 mx-auto" />
                  <p className="mt-2 text-sm text-gray-500">No scenes created yet</p>
                  <Link 
                    to={`/projects/${projectId}/scenes`}
                    className="mt-3 inline-block"
                  >
                    <Button size="sm">
                      <PlusIcon className="h-4 w-4 mr-1" />
                      Create Scene
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="bg-white shadow rounded-lg p-4">
              <Link 
                to={`/projects/${projectId}/story`}
                className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-md"
              >
                <DocumentTextIcon className="h-10 w-10 text-indigo-500" />
                <h3 className="mt-2 font-medium text-gray-900">Story Editor</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Develop your story's narrative and structure
                </p>
              </Link>
            </div>
            
            <div className="bg-white shadow rounded-lg p-4">
              <Link 
                to={`/projects/${projectId}/objects`}
                className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-md"
              >
                <CubeIcon className="h-10 w-10 text-indigo-500" />
                <h3 className="mt-2 font-medium text-gray-900">Story Objects</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Manage characters, locations, and items
                </p>
              </Link>
            </div>
            
            <div className="bg-white shadow rounded-lg p-4">
              <Link 
                to={`/projects/${projectId}/ai`}
                className="flex flex-col items-center p-4 text-center hover:bg-gray-50 rounded-md"
              >
                <SparklesIcon className="h-10 w-10 text-indigo-500" />
                <h3 className="mt-2 font-medium text-gray-900">AI Workshop</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Use AI tools to enhance your story
                </p>
              </Link>
            </div>
          </div>
        </div>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Contributors</h3>
            <div className="bg-white shadow rounded-lg p-3">
              {project.contributors && project.contributors.length > 0 ? (
                <div className="space-y-2">
                  {project.contributors.map((contributor, index) => (
                    <div key={index} className="flex items-center text-sm">
                      <div className="bg-gray-100 rounded-full p-2 mr-3">
                        <UserIcon className="h-4 w-4 text-gray-500" />
                      </div>
                      <div>
                        <p className="font-medium">{contributor.username}</p>
                        <p className="text-xs text-gray-500">{contributor.role}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No contributors yet</p>
              )}
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Comments</h3>
            <div className="bg-white shadow rounded-lg p-3">
              {project.recentComments && project.recentComments.length > 0 ? (
                <div className="space-y-2">
                  {project.recentComments.map(comment => (
                    <div key={comment.id} className="text-sm">
                      <div className="flex items-center">
                        <span className="font-medium">{comment.username}</span>
                        <span className="text-gray-500 text-xs ml-2">
                          {new Date(comment.createdAt).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-gray-600">{comment.content}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No comments yet</p>
              )}
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Activity</h3>
            <div className="bg-gray-50 p-3 rounded-lg min-h-16">
              {project.recentActivity && project.recentActivity.length > 0 ? (
                <div className="space-y-2">
                  {project.recentActivity.map((activity, index) => (
                    <div key={index} className="text-sm flex items-center">
                      <ClockIcon className="h-4 w-4 text-gray-400 mr-1" />
                      <span className="text-gray-600">{activity}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No recent activity</p>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Modals */}
      <EditProjectModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        project={project}
        onSubmit={handleUpdateProject}
      />
      
      <DeleteProjectModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        projectTitle={project.title}
        onDelete={handleDeleteProject}
      />
    </div>
  );
};

export default ProjectDetail;