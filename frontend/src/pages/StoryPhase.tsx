// src/pages/StoryPhase.tsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import { 
  DocumentTextIcon, 
  SparklesIcon, 
  PencilIcon, 
  DownloadIcon, 
  ShareIcon,
  ChevronDownIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  BookOpenIcon,
  RefreshIcon,
  ViewListIcon,
  ArrowPathIcon,
  DocumentDuplicateIcon,
  MoonIcon,
  SunIcon,
} from '@heroicons/react/24/outline';

// Components
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Button from '../components/ui/Button';
import StoryStyleSelector from '../components/story/StoryStyleSelector';
import ChapterOrganizer from '../components/story/ChapterOrganizer';
import EditorToolbar from '../components/story/EditorToolbar';
import StoryStats from '../components/story/StoryStats';
import StoryMetadataPanel from '../components/story/StoryMetadataPanel';
import ExportDialog from '../components/story/ExportDialog';
import SectionRegenerateDialog from '../components/story/SectionRegenerateDialog';

// Hooks & Services
import { useApi } from '../hooks/useApi';
import { useToast } from '../hooks/useToast';
import { useSocket } from '../hooks/useSocket';
import { useUser } from '../hooks/useUser';

// Types
import { 
  Project, 
  Scene, 
  StoryObject, 
  NarrativeOptions, 
  StoryData,
  ChapterData,
  StoryStats as StoryStatsType
} from '../types';

const StoryPhase: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const api = useApi();
  const { showToast } = useToast();
  const { socket, isConnected } = useSocket();
  const { user } = useUser();
  
  // State
  const [project, setProject] = useState<Project | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [storyObjects, setStoryObjects] = useState<{
    characters: StoryObject[];
    locations: StoryObject[];
    props: StoryObject[];
  }>({
    characters: [],
    locations: [],
    props: []
  });
  
  const [story, setStory] = useState<StoryData | null>(null);
  const [storyStats, setStoryStats] = useState<StoryStatsType>({
    wordCount: 0,
    pageCount: 0,
    readingTime: 0,
    marketabilityScore: 0,
    overallQuality: 0
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generationStep, setGenerationStep] = useState('');
  
  const [narrativeOptions, setNarrativeOptions] = useState<NarrativeOptions>({
    narrativeVoice: 'third_person_limited',
    proseStyle: 'balanced',
    dialogStyle: 'direct',
    tonePreference: 'dramatic'
  });
  
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showRegenerateDialog, setShowRegenerateDialog] = useState(false);
  const [selectedChapterIndex, setSelectedChapterIndex] = useState<number | null>(null);
  
  // Editor setup
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: 'Your story will appear here after generation...'
      })
    ],
    content: '',
    editorProps: {
      attributes: {
        class: 'prose max-w-none focus:outline-none min-h-[500px] px-4 py-2'
      }
    },
    onUpdate: ({ editor }) => {
      if (story) {
        // Update story content and calculate stats
        const content = editor.getHTML();
        setStory(prev => prev ? { ...prev, content } : null);
        calculateStats(content);
      }
    }
  });
  
  // Load project data
  useEffect(() => {
    const loadProjectData = async () => {
      if (!projectId) return;
      
      try {
        setIsLoading(true);
        
        // Fetch project, scenes and story objects
        const [projectResponse, scenesResponse, objectsResponse] = await Promise.all([
          api.get(`/api/projects/${projectId}`),
          api.get(`/api/projects/${projectId}/scenes`),
          api.get(`/api/projects/${projectId}/objects`)
        ]);
        
        setProject(projectResponse.data);
        setScenes(scenesResponse.data.sort((a: Scene, b: Scene) => a.order_index - b.order_index));
        
        // Organize objects by type
        const characters = objectsResponse.data.filter((obj: StoryObject) => obj.objectType === 'character');
        const locations = objectsResponse.data.filter((obj: StoryObject) => obj.objectType === 'location');
        const props = objectsResponse.data.filter((obj: StoryObject) => obj.objectType === 'prop');
        
        setStoryObjects({
          characters,
          locations,
          props
        });
        
        // Check if story already exists
        try {
          const storyResponse = await api.get(`/api/projects/${projectId}/story`);
          if (storyResponse.data) {
            setStory(storyResponse.data);
            if (editor && storyResponse.data.content) {
              editor.commands.setContent(storyResponse.data.content);
            }
            calculateStats(storyResponse.data.content);
          }
        } catch (err) {
          // Story doesn't exist yet, which is fine
          console.log('No story exists yet for this project');
        }
        
      } catch (err) {
        console.error('Failed to load project data', err);
        showToast('Failed to load project data. Please try again.', 'error');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadProjectData();
  }, [projectId, api, editor, showToast]);
  
  // Socket.io real-time updates
  useEffect(() => {
    if (!socket || !isConnected || !projectId) return;
    
    // Join project room
    socket.emit('join_project', { projectId });
    
    // Listen for story updates
    socket.on('story_updated', (updatedStory: StoryData) => {
      setStory(updatedStory);
      if (editor && updatedStory.content) {
        // Only update if content changed
        if (editor.getHTML() !== updatedStory.content) {
          editor.commands.setContent(updatedStory.content);
        }
      }
      calculateStats(updatedStory.content);
    });
    
    return () => {
      // Leave project room on unmount
      socket.emit('leave_project', { projectId });
      socket.off('story_updated');
    };
  }, [socket, isConnected, projectId, editor]);
  
  // Calculate story statistics
  const calculateStats = useCallback((content: string) => {
    if (!content) {
      setStoryStats({
        wordCount: 0,
        pageCount: 0,
        readingTime: 0,
        marketabilityScore: 0,
        overallQuality: 0
      });
      return;
    }
    
    // Strip HTML tags for word count
    const plainText = content.replace(/<[^>]*>/g, '');
    const words = plainText.trim().split(/\s+/);
    const wordCount = words.length;
    
    // Calculate page count (roughly 250 words per page)
    const pageCount = Math.ceil(wordCount / 250);
    
    // Calculate reading time (average 200 words per minute)
    const readingTime = Math.ceil(wordCount / 200);
    
    // For demo purposes, generate placeholder scores
    // In a real implementation, these would come from AI analysis
    const marketabilityScore = Math.min(5, Math.max(1, 3 + Math.random() * 1.5));
    const overallQuality = Math.min(5, Math.max(1, 3.5 + Math.random()));
    
    setStoryStats({
      wordCount,
      pageCount,
      readingTime,
      marketabilityScore: parseFloat(marketabilityScore.toFixed(1)),
      overallQuality: parseFloat(overallQuality.toFixed(1))
    });
  }, []);
  
  // Generate full story from scenes
  const handleGenerateStory = async () => {
    if (!projectId || scenes.length === 0) {
      showToast('You need scenes to generate a story.', 'warning');
      return;
    }
    
    try {
      // Check if user has enough tokens
      const estimateResponse = await api.post('/api/ai/token-estimate', {
        operation_type: 'generate_story',
        input_text: scenes.map(s => s.description).join(' ')
      });
      
      if (!estimateResponse.data.can_afford) {
        showToast(`Not enough tokens. You need ${estimateResponse.data.estimate.estimated_total_cost} tokens.`, 'error');
        return;
      }
      
      setIsGenerating(true);
      setGenerationStep('Analyzing scene structure...');
      setGenerationProgress(10);
      
      // Progress simulation (in a real implementation, this would come from backend events)
      const progressSteps = [
        { step: 'Analyzing character relationships...', progress: 25 },
        { step: 'Organizing chapter structure...', progress: 40 },
        { step: 'Generating narrative prose...', progress: 60 },
        { step: 'Applying literary style...', progress: 75 },
        { step: 'Refining dialogue and descriptions...', progress: 90 },
        { step: 'Finalizing your story...', progress: 95 }
      ];
      
      let stepIndex = 0;
      const progressInterval = setInterval(() => {
        if (stepIndex < progressSteps.length) {
          setGenerationStep(progressSteps[stepIndex].step);
          setGenerationProgress(progressSteps[stepIndex].progress);
          stepIndex++;
        } else {
          clearInterval(progressInterval);
        }
      }, 1500);
      
      // Generate story with selected narrative options
      const response = await api.post(`/api/projects/${projectId}/generate-story`, {
        narrativeOptions
      });
      
      clearInterval(progressInterval);
      
      if (response.data.success) {
        const generatedStory = response.data.story;
        setStory(generatedStory);
        if (editor) {
          editor.commands.setContent(generatedStory.content);
        }
        calculateStats(generatedStory.content);
        
        // Update user tokens (assuming response includes updated token count)
        if (response.data.tokens) {
          // Update token display
        }
        
        showToast('Story successfully generated!', 'success');
      } else {
        showToast('Failed to generate story.', 'error');
      }
    } catch (err) {
      console.error('Error generating story:', err);
      showToast('Error generating story. Please try again.', 'error');
    } finally {
      setIsGenerating(false);
      setGenerationProgress(0);
    }
  };
  
  // Regenerate a specific section
  const handleRegenerateSection = async (chapterIndex: number, options: Partial<NarrativeOptions>) => {
    if (!projectId || !story) return;
    
    try {
      setIsGenerating(true);
      setGenerationStep(`Regenerating chapter ${chapterIndex + 1}...`);
      setGenerationProgress(50);
      
      const updatedOptions = { ...narrativeOptions, ...options };
      
      const response = await api.post(`/api/projects/${projectId}/regenerate-section`, {
        chapterIndex,
        narrativeOptions: updatedOptions
      });
      
      if (response.data.success) {
        const updatedStory = response.data.story;
        setStory(updatedStory);
        if (editor) {
          editor.commands.setContent(updatedStory.content);
        }
        calculateStats(updatedStory.content);
        showToast('Section successfully regenerated!', 'success');
      } else {
        showToast('Failed to regenerate section.', 'error');
      }
    } catch (err) {
      console.error('Error regenerating section:', err);
      showToast('Error regenerating section. Please try again.', 'error');
    } finally {
      setIsGenerating(false);
      setGenerationProgress(0);
      setShowRegenerateDialog(false);
    }
  };
  
  // Save story content
  const handleSaveStory = async () => {
    if (!projectId || !story || !editor) return;
    
    try {
      const content = editor.getHTML();
      const response = await api.put(`/api/projects/${projectId}/story`, {
        ...story,
        content
      });
      
      if (response.data.success) {
        showToast('Story saved successfully!', 'success');
      } else {
        showToast('Failed to save story.', 'error');
      }
    } catch (err) {
      console.error('Error saving story:', err);
      showToast('Error saving story. Please try again.', 'error');
    }
  };
  
  // Export story
  const handleExportStory = async (format: 'pdf' | 'docx' | 'epub' | 'txt') => {
    if (!projectId || !story) return;
    
    try {
      const response = await api.get(`/api/projects/${projectId}/export-story?format=${format}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project?.title || 'story'}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      showToast(`Story exported as ${format.toUpperCase()} successfully!`, 'success');
    } catch (err) {
      console.error('Error exporting story:', err);
      showToast('Error exporting story. Please try again.', 'error');
    } finally {
      setShowExportDialog(false);
    }
  };
  
  // Share story
  const handleShareStory = () => {
    // Implementation would depend on your sharing mechanism
    showToast('Sharing functionality coming soon!', 'info');
  };
  
  // Update narrative options
  const handleUpdateNarrativeOptions = (options: Partial<NarrativeOptions>) => {
    setNarrativeOptions(prev => ({ ...prev, ...options }));
  };
  
  // Check if there's enough content to generate a story
  const canGenerateStory = useMemo(() => {
    return scenes.length >= 2 && !isGenerating;
  }, [scenes, isGenerating]);
  
  // Determine if we're in a ready state to display the editor
  const isStoryReady = story && story.content && !isGenerating;
  
  // Main render
  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BookOpenIcon className="h-6 w-6 text-indigo-600" />
            Story Phase
          </h1>
          <p className="text-gray-600">
            Transform your scenes into a cohesive narrative
          </p>
        </div>
        
        <div className="flex space-x-3">
          <Button 
            variant="secondary"
            onClick={() => navigate(`/projects/${projectId}`)}
            className="flex items-center gap-2"
          >
            <ArrowPathIcon className="h-5 w-5" />
            Back to Project
          </Button>
          
          <Button
            variant="primary"
            onClick={handleGenerateStory}
            disabled={!canGenerateStory}
            className="flex items-center gap-2"
          >
            <SparklesIcon className="h-5 w-5" />
            Generate Story
          </Button>
        </div>
      </div>
      
      {/* Generation Progress (shown when generating) */}
      {isGenerating && (
        <div className="bg-white rounded-xl shadow-lg p-6 text-center">
          <SparklesIcon className="h-12 w-12 text-indigo-500 mx-auto mb-4 animate-pulse" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Generating Your Story</h2>
          <p className="text-gray-600 mb-6">{generationStep}</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2 max-w-lg mx-auto">
            <div 
              className="bg-indigo-600 h-2.5 rounded-full transition-all duration-500" 
              style={{ width: `${generationProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500">
            This may take a minute or two depending on your story's complexity
          </p>
        </div>
      )}
      
      {/* Loading State */}
      {isLoading ? (
        <div className="bg-white rounded-xl shadow-lg p-6 flex justify-center items-center min-h-[300px]">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <>
          {/* Story Stats */}
          <StoryStats stats={storyStats} />
          
          {/* Main Story Editor */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Editor Toolbar */}
            <div className="border-b border-gray-200 p-2 flex flex-wrap justify-between items-center gap-2">
              <div className="flex flex-wrap items-center gap-2">
                {/* Show toolbar only when story is ready */}
                {isStoryReady && (
                  <EditorToolbar editor={editor} />
                )}
                
                {/* Style selector - always show but might be disabled */}
                <div className="border-l border-gray-200 pl-2 ml-2">
                  <StoryStyleSelector 
                    options={narrativeOptions}
                    onChange={handleUpdateNarrativeOptions}
                    disabled={isGenerating}
                  />
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                {/* Save Button */}
                {isStoryReady && (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={handleSaveStory}
                    className="flex items-center gap-1"
                  >
                    <DocumentTextIcon className="h-4 w-4" />
                    Save
                  </Button>
                )}
                
                {/* Export Button */}
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowExportDialog(true)}
                  disabled={!isStoryReady}
                  className="flex items-center gap-1"
                >
                  <DownloadIcon className="h-4 w-4" />
                  Export
                </Button>
                
                {/* Share Button */}
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleShareStory}
                  disabled={!isStoryReady}
                  className="flex items-center gap-1"
                >
                  <ShareIcon className="h-4 w-4" />
                  Share
                </Button>
              </div>
            </div>
            
            {/* Editor Content Area */}
            <div className="flex flex-col md:flex-row">
              {/* Left Sidebar - Chapter Organizer */}
              {isStoryReady && story.chapters && (
                <div className="w-full md:w-64 border-r border-gray-200 p-4">
                  <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-1">
                    <ViewListIcon className="h-4 w-4" />
                    Chapters
                  </h3>
                  
                  <ChapterOrganizer 
                    chapters={story.chapters}
                    onChapterSelect={index => setSelectedChapterIndex(index)}
                    onRegenerateChapter={index => {
                      setSelectedChapterIndex(index);
                      setShowRegenerateDialog(true);
                    }}
                  />
                </div>
              )}
              
              {/* Main Editor */}
              <div className="flex-1 p-4">
                {!story ? (
                  <div className="text-center py-12">
                    <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Story Generated Yet</h3>
                    <p className="text-gray-600 max-w-md mx-auto mb-6">
                      Your story will appear here after generation. Click the "Generate Story" button to transform your scenes into a cohesive narrative.
                    </p>
                    
                    {!canGenerateStory && scenes.length < 2 && (
                      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 max-w-md mx-auto text-left">
                        <div className="flex items-start">
                          <ExclamationCircleIcon className="h-5 w-5 text-yellow-500 mr-2 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-yellow-700">
                            You need at least 2 scenes to generate a story. Go to the Expand phase to create more scenes.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <EditorContent editor={editor} className="min-h-[500px]" />
                )}
              </div>
              
              {/* Right Sidebar - Metadata and Context */}
              {isStoryReady && (
                <div className="w-full md:w-64 border-l border-gray-200 p-4">
                  <StoryMetadataPanel 
                    metadata={story.metadata}
                    onUpdate={(metadata) => setStory(prev => prev ? { ...prev, metadata } : null)}
                  />
                </div>
              )}
            </div>
          </div>
        </>
      )}
      
      {/* Export Dialog */}
      {showExportDialog && (
        <ExportDialog
          onExport={handleExportStory}
          onClose={() => setShowExportDialog(false)}
        />
      )}
      
      {/* Regenerate Section Dialog */}
      {showRegenerateDialog && selectedChapterIndex !== null && (
        <SectionRegenerateDialog
          currentOptions={narrativeOptions}
          onRegenerate={(options) => handleRegenerateSection(selectedChapterIndex, options)}
          onClose={() => setShowRegenerateDialog(false)}
        />
      )}
    </div>
  );
};

export default StoryPhase;