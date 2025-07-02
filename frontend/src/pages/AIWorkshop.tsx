// frontend/src/pages/AIWorkshop.tsx - Complete AI Workshop Implementation
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../services/api';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  SparklesIcon,
  LightBulbIcon,
  DocumentTextIcon,
  CpuChipIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface AITask {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  result?: any;
  error?: string;
}

interface Project {
  id: string;
  title: string;
  description: string;
  current_phase: string;
  scenes: any[];
}

const AIWorkshop: React.FC = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [aiTasks, setAiTasks] = useState<AITask[]>([]);
  const [activeOperation, setActiveOperation] = useState<string | null>(null);
  const [results, setResults] = useState<{[key: string]: any}>({});

  // AI Operation states
  const [ideaText, setIdeaText] = useState('');
  const [storyIntent, setStoryIntent] = useState('');
  const [analysisResults, setAnalysisResults] = useState<any>(null);

  useEffect(() => {
    if (projectId) {
      fetchProject();
      fetchAITasks();
    }
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const response = await api.get(`/api/projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to fetch project:', error);
    }
  };

  const fetchAITasks = async () => {
    try {
      const response = await api.get('/api/ai/tasks', { params: { limit: 10 } });
      setAiTasks(response.data.tasks || []);
    } catch (error) {
      console.error('Failed to fetch AI tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const executeAIOperation = async (operation: string, data: any) => {
    setActiveOperation(operation);
    try {
      let response;
      switch (operation) {
        case 'analyze-idea':
          response = await api.post('/api/ai/analyze-idea', data);
          setAnalysisResults(response.data);
          setResults(prev => ({ ...prev, 'analyze-idea': response.data }));
          break;
        
        case 'analyze-structure':
          response = await api.post(`/api/ai/projects/${projectId}/analyze-structure`);
          setResults(prev => ({ ...prev, 'analyze-structure': response.data }));
          break;
        
        case 'suggest-scenes':
          response = await api.post(`/api/ai/projects/${projectId}/suggest-scenes`);
          setResults(prev => ({ ...prev, 'suggest-scenes': response.data }));
          break;
        
        case 'generate-story':
          response = await api.post(`/api/ai/projects/${projectId}/generate-story`);
          setResults(prev => ({ ...prev, 'generate-story': response.data }));
          break;
        
        case 'create-from-idea':
          response = await api.post('/api/ai/create-project-from-idea', data);
          setResults(prev => ({ ...prev, 'create-from-idea': response.data }));
          break;
      }
      
      // Refresh tasks after operation
      await fetchAITasks();
    } catch (error: any) {
      console.error(`AI operation ${operation} failed:`, error);
      setResults(prev => ({ 
        ...prev, 
        [operation]: { 
          error: error.response?.data?.message || 'Operation failed' 
        } 
      }));
    } finally {
      setActiveOperation(null);
    }
  };

  const handleAnalyzeIdea = () => {
    if (!ideaText.trim()) return;
    executeAIOperation('analyze-idea', {
      idea: ideaText,
      story_intent: storyIntent
    });
  };

  const handleCreateFromIdea = () => {
    if (!analysisResults) return;
    executeAIOperation('create-from-idea', {
      idea: ideaText,
      analysis_id: analysisResults.analysis_id
    });
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <SparklesIcon className="h-6 w-6 text-purple-500" />
          AI Workshop
        </h1>
        <p className="text-gray-600 mt-1">
          {project ? `Enhance "${project.title}" with AI assistance` : 'AI-powered writing tools'}
        </p>
      </div>

      {/* AI Operations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Idea Analysis */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <LightBulbIcon className="h-5 w-5 text-yellow-500" />
            <h3 className="text-lg font-medium text-gray-900">Story Idea Analysis</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Story Idea
              </label>
              <textarea
                value={ideaText}
                onChange={(e) => setIdeaText(e.target.value)}
                rows={4}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Describe your story idea..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Story Intent (Optional)
              </label>
              <input
                type="text"
                value={storyIntent}
                onChange={(e) => setStoryIntent(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="What do you want to achieve with this story?"
              />
            </div>
            
            <button
              onClick={handleAnalyzeIdea}
              disabled={!ideaText.trim() || activeOperation === 'analyze-idea'}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {activeOperation === 'analyze-idea' ? (
                <>
                  <LoadingSpinner size="sm" />
                  Analyzing...
                </>
              ) : (
                <>
                  <SparklesIcon className="h-4 w-4" />
                  Analyze Idea
                </>
              )}
            </button>
          </div>

          {/* Analysis Results */}
          {results['analyze-idea'] && (
            <div className="mt-6 p-4 bg-purple-50 rounded-md">
              <h4 className="font-medium text-purple-900 mb-2">Analysis Results</h4>
              {results['analyze-idea'].error ? (
                <p className="text-red-600 text-sm">{results['analyze-idea'].error}</p>
              ) : (
                <div className="space-y-2 text-sm">
                  <p><strong>Genre:</strong> {results['analyze-idea'].suggested_genre}</p>
                  <p><strong>Themes:</strong> {results['analyze-idea'].themes?.join(', ')}</p>
                  <p><strong>Potential:</strong> {results['analyze-idea'].story_potential}</p>
                  <p className="text-purple-700">{results['analyze-idea'].feedback}</p>
                  
                  {analysisResults && (
                    <button
                      onClick={handleCreateFromIdea}
                      disabled={activeOperation === 'create-from-idea'}
                      className="mt-3 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 disabled:opacity-50 text-sm"
                    >
                      {activeOperation === 'create-from-idea' ? 'Creating...' : 'Create Project from Idea'}
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Project Structure Analysis */}
        {project && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <ChartBarIcon className="h-5 w-5 text-blue-500" />
              <h3 className="text-lg font-medium text-gray-900">Structure Analysis</h3>
            </div>
            
            <p className="text-gray-600 mb-4">
              Analyze your project's story structure and get suggestions for improvement.
            </p>
            
            <button
              onClick={() => executeAIOperation('analyze-structure', {})}
              disabled={activeOperation === 'analyze-structure'}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {activeOperation === 'analyze-structure' ? (
                <>
                  <LoadingSpinner size="sm" />
                  Analyzing...
                </>
              ) : (
                <>
                  <ChartBarIcon className="h-4 w-4" />
                  Analyze Structure
                </>
              )}
            </button>

            {/* Structure Results */}
            {results['analyze-structure'] && (
              <div className="mt-6 p-4 bg-blue-50 rounded-md">
                <h4 className="font-medium text-blue-900 mb-2">Structure Analysis</h4>
                {results['analyze-structure'].error ? (
                  <p className="text-red-600 text-sm">{results['analyze-structure'].error}</p>
                ) : (
                  <div className="space-y-2 text-sm">
                    <p><strong>Overall Structure:</strong> {results['analyze-structure'].overall_assessment}</p>
                    <p><strong>Strengths:</strong> {results['analyze-structure'].strengths?.join(', ')}</p>
                    <p><strong>Areas to Improve:</strong> {results['analyze-structure'].improvements?.join(', ')}</p>
                    <p className="text-blue-700">{results['analyze-structure'].recommendations}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Scene Suggestions */}
        {project && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <DocumentTextIcon className="h-5 w-5 text-green-500" />
              <h3 className="text-lg font-medium text-gray-900">Scene Suggestions</h3>
            </div>
            
            <p className="text-gray-600 mb-4">
              Get AI-generated scene suggestions based on your current project.
            </p>
            
            <button
              onClick={() => executeAIOperation('suggest-scenes', {})}
              disabled={activeOperation === 'suggest-scenes'}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {activeOperation === 'suggest-scenes' ? (
                <>
                  <LoadingSpinner size="sm" />
                  Generating...
                </>
              ) : (
                <>
                  <DocumentTextIcon className="h-4 w-4" />
                  Suggest Scenes
                </>
              )}
            </button>

            {/* Scene Suggestions Results */}
            {results['suggest-scenes'] && (
              <div className="mt-6 p-4 bg-green-50 rounded-md">
                <h4 className="font-medium text-green-900 mb-2">Scene Suggestions</h4>
                {results['suggest-scenes'].error ? (
                  <p className="text-red-600 text-sm">{results['suggest-scenes'].error}</p>
                ) : (
                  <div className="space-y-3">
                    {results['suggest-scenes'].suggested_scenes?.map((scene: any, index: number) => (
                      <div key={index} className="bg-white p-3 rounded border">
                        <h5 className="font-medium text-green-900">{scene.title}</h5>
                        <p className="text-sm text-gray-600 mt-1">{scene.description}</p>
                        <div className="flex gap-2 mt-2">
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                            {scene.scene_type}
                          </span>
                          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                            {scene.estimated_words} words
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Story Generation */}
        {project && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <CpuChipIcon className="h-5 w-5 text-indigo-500" />
              <h3 className="text-lg font-medium text-gray-900">Story Generation</h3>
            </div>
            
            <p className="text-gray-600 mb-4">
              Generate a complete story draft based on your project structure.
            </p>
            
            <button
              onClick={() => executeAIOperation('generate-story', {})}
              disabled={activeOperation === 'generate-story'}
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {activeOperation === 'generate-story' ? (
                <>
                  <LoadingSpinner size="sm" />
                  Generating...
                </>
              ) : (
                <>
                  <CpuChipIcon className="h-4 w-4" />
                  Generate Story
                </>
              )}
            </button>

            {/* Story Generation Results */}
            {results['generate-story'] && (
              <div className="mt-6 p-4 bg-indigo-50 rounded-md">
                <h4 className="font-medium text-indigo-900 mb-2">Generated Story</h4>
                {results['generate-story'].error ? (
                  <p className="text-red-600 text-sm">{results['generate-story'].error}</p>
                ) : (
                  <div className="space-y-2 text-sm">
                    <p><strong>Word Count:</strong> {results['generate-story'].word_count}</p>
                    <p><strong>Scenes Generated:</strong> {results['generate-story'].scenes_count}</p>
                    <div className="bg-white p-3 rounded border max-h-40 overflow-y-auto">
                      <p className="text-gray-700">{results['generate-story'].preview}</p>
                    </div>
                    <button className="mt-2 bg-indigo-600 text-white py-1 px-3 rounded text-sm hover:bg-indigo-700">
                      View Full Story
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recent AI Tasks */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <ClockIcon className="h-5 w-5 text-gray-500" />
          <h3 className="text-lg font-medium text-gray-900">Recent AI Tasks</h3>
        </div>
        
        {aiTasks.length > 0 ? (
          <div className="space-y-3">
            {aiTasks.map((task) => (
              <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <span className="font-medium text-gray-900">
                    {task.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                  <div className="text-sm text-gray-500">
                    {new Date(task.created_at).toLocaleString()}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={task.status} />
                  {task.status === 'completed' && (
                    <button className="text-blue-600 hover:text-blue-700 text-sm">
                      View Result
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No AI tasks yet</p>
        )}
      </div>
    </div>
  );
};

// Status Badge Component
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const statusClasses = {
    pending: 'bg-yellow-100 text-yellow-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800'
  };

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusClasses[status as keyof typeof statusClasses]}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

export default AIWorkshop;