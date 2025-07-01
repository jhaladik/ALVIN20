// src/components/pages/AIFeaturesPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Tab } from '@headlessui/react';
import { 
  SparklesIcon, 
  BeakerIcon, 
  LightBulbIcon, 
  ChartBarIcon 
} from '@heroicons/react/24/outline';

import { useSocketContext } from '../../context/SocketContext';
import { useAIAnalysis } from '../../hooks/useAIAnalysis';
import aiService from '../../services/aiService';
import api from '../../services/api';

import AICriticsPanel from '../ai/AICriticsPanel';
import Button from '../ui/Button';
import LoadingSpinner from '../ui/LoadingSpinner';

interface Project {
  id: string;
  title: string;
  description: string;
  genre: string;
  sceneCount: number;
}

interface StoryStructure {
  overallAnalysis: string;
  emotionalArc: { x: number; y: number }[];
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

const AIFeaturesPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { socket, isConnected } = useSocketContext();
  
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Structure analysis state
  const [structureAnalysis, setStructureAnalysis] = useState<StoryStructure | null>(null);
  const [isAnalyzingStructure, setIsAnalyzingStructure] = useState(false);
  
  // Scene suggestions state
  const [sceneSuggestions, setSceneSuggestions] = useState<any[]>([]);
  const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false);
  
  // Use the AI analysis hook for the critics panel
  const {
    analyses,
    isAnalyzing,
    activeCriticType,
    setActiveCriticType,
    error: analysisError,
    requestAnalysis,
  } = useAIAnalysis({
    projectId,
    socket,
    isConnected,
  });

  // Load project data
  useEffect(() => {
    const loadProjectData = async () => {
      if (!projectId) return;
      
      try {
        setIsLoading(true);
        const response = await api.get(`/api/projects/${projectId}`);
        setProject(response.data.project);
        
        // Check if structure analysis exists
        if (response.data.structureAnalysis) {
          setStructureAnalysis(response.data.structureAnalysis);
        }
        
      } catch (err) {
        console.error('Failed to load project', err);
        setError('Failed to load project details');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadProjectData();
  }, [projectId]);

  // Analyze story structure
  const handleAnalyzeStructure = async () => {
    if (!projectId) return;
    
    try {
      setIsAnalyzingStructure(true);
      setError(null);
      
      const response = await aiService.analyzeStoryStructure(projectId);
      setStructureAnalysis(response.structure);
      
    } catch (err: any) {
      console.error('Failed to analyze structure', err);
      setError(err.message || 'Failed to analyze story structure');
    } finally {
      setIsAnalyzingStructure(false);
    }
  };

  // Generate scene suggestions
  const handleGenerateSuggestions = async () => {
    if (!projectId) return;
    
    try {
      setIsGeneratingSuggestions(true);
      setError(null);
      
      const response = await aiService.suggestScenes(projectId, 3);
      setSceneSuggestions(response.suggestions);
      
    } catch (err: any) {
      console.error('Failed to generate suggestions', err);
      setError(err.message || 'Failed to generate scene suggestions');
    } finally {
      setIsGeneratingSuggestions(false);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Error state
  if (error && !project) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md">
          {error}
        </div>
        <Button
          variant="secondary"
          className="mt-4"
          onClick={() => navigate('/projects')}
        >
          Back to Projects
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{project?.title}</h1>
            <p className="text-gray-600">{project?.genre} · {project?.sceneCount} scenes</p>
          </div>
          
          <Button variant="secondary" onClick={() => navigate(`/projects/${projectId}`)}>
            Back to Project
          </Button>
        </div>
        
        <div className="mt-4 bg-indigo-50 border border-indigo-100 rounded-lg p-4">
          <div className="flex items-start">
            <SparklesIcon className="h-6 w-6 text-indigo-500 mr-3 flex-shrink-0" />
            <div>
              <h2 className="text-lg font-medium text-indigo-800">AI Insights & Tools</h2>
              <p className="text-indigo-700 mt-1">
                Leverage Claude AI to analyze and improve your story from multiple perspectives.
                Select from specialized critics, get structural analysis, or generate new scene ideas.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}
      
      {/* Tab navigation */}
      <Tab.Group>
        <Tab.List className="flex space-x-1 rounded-xl bg-gray-100 p-1 mb-6">
          <Tab
            className={({ selected }) =>
              `w-full rounded-lg py-2.5 text-sm font-medium leading-5 
               ${
                 selected
                   ? 'bg-white shadow text-indigo-700'
                   : 'text-gray-700 hover:bg-white/[0.12] hover:text-gray-900'
               }`
            }
          >
            <div className="flex items-center justify-center">
              <BeakerIcon className="h-5 w-5 mr-2" />
              AI Critics
            </div>
          </Tab>
          <Tab
            className={({ selected }) =>
              `w-full rounded-lg py-2.5 text-sm font-medium leading-5 
               ${
                 selected
                   ? 'bg-white shadow text-indigo-700'
                   : 'text-gray-700 hover:bg-white/[0.12] hover:text-gray-900'
               }`
            }
          >
            <div className="flex items-center justify-center">
              <ChartBarIcon className="h-5 w-5 mr-2" />
              Story Structure
            </div>
          </Tab>
          <Tab
            className={({ selected }) =>
              `w-full rounded-lg py-2.5 text-sm font-medium leading-5 
               ${
                 selected
                   ? 'bg-white shadow text-indigo-700'
                   : 'text-gray-700 hover:bg-white/[0.12] hover:text-gray-900'
               }`
            }
          >
            <div className="flex items-center justify-center">
              <LightBulbIcon className="h-5 w-5 mr-2" />
              Scene Suggestions
            </div>
          </Tab>
        </Tab.List>
        
        <Tab.Panels>
          {/* AI Critics Panel */}
          <Tab.Panel>
            <AICriticsPanel
              projectId={projectId}
              analyses={analyses}
              isAnalyzing={isAnalyzing}
              activeCriticType={activeCriticType}
              error={analysisError}
              onRequestAnalysis={requestAnalysis}
              onActiveCriticChange={setActiveCriticType}
            />
          </Tab.Panel>
          
          {/* Story Structure Panel */}
          <Tab.Panel>
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Story Structure Analysis</h3>
              
              {isAnalyzingStructure ? (
                <div className="flex flex-col items-center justify-center min-h-[400px]">
                  <SparklesIcon className="h-12 w-12 text-indigo-500 mb-4 animate-pulse" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Analyzing Story Structure</h3>
                  <p className="text-gray-600 text-center max-w-md mb-6">
                    Our AI is examining the overall structure, pacing, and dramatic arc of your story.
                    This may take a minute or two.
                  </p>
                  <LoadingSpinner size="lg" />
                </div>
              ) : structureAnalysis ? (
                <div className="space-y-6">
                  {/* Overall analysis */}
                  <div>
                    <h4 className="text-md font-medium text-gray-900 mb-2">Overall Analysis</h4>
                    <div className="prose max-w-none">
                      <p>{structureAnalysis.overallAnalysis}</p>
                    </div>
                  </div>
                  
                  {/* Emotional arc chart would go here */}
                  <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
                    <h4 className="text-md font-medium text-gray-900 mb-2">Emotional Arc</h4>
                    <p className="text-sm text-gray-600 mb-4">
                      This chart shows the emotional intensity throughout your story's progression.
                    </p>
                    <div className="h-64 bg-white border border-gray-200 rounded-md p-4">
                      {/* Placeholder for emotional arc chart */}
                      <div className="flex items-center justify-center h-full text-gray-400">
                        Emotional arc visualization would appear here.
                      </div>
                    </div>
                  </div>
                  
                  {/* Strengths and weaknesses */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-green-50 p-4 rounded-md border border-green-200">
                      <h4 className="text-md font-medium text-green-800 mb-2">Strengths</h4>
                      <ul className="list-disc list-inside space-y-2 text-green-700">
                        {structureAnalysis.strengths.map((strength, index) => (
                          <li key={index}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-amber-50 p-4 rounded-md border border-amber-200">
                      <h4 className="text-md font-medium text-amber-800 mb-2">Areas for Improvement</h4>
                      <ul className="list-disc list-inside space-y-2 text-amber-700">
                        {structureAnalysis.weaknesses.map((weakness, index) => (
                          <li key={index}>{weakness}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  {/* Recommendations */}
                  <div className="bg-indigo-50 p-4 rounded-md border border-indigo-200">
                    <h4 className="text-md font-medium text-indigo-800 mb-2">Recommendations</h4>
                    <ul className="list-disc list-inside space-y-2 text-indigo-700">
                      {structureAnalysis.recommendations.map((recommendation, index) => (
                        <li key={index}>{recommendation}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="flex justify-end">
                    <Button
                      variant="secondary"
                      onClick={handleAnalyzeStructure}
                      disabled={isAnalyzingStructure}
                    >
                      <SparklesIcon className="h-4 w-4 mr-1" />
                      Refresh Analysis
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center min-h-[400px]">
                  <ChartBarIcon className="h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Structure Analysis Yet</h3>
                  <p className="text-gray-600 text-center max-w-md mb-6">
                    Get a comprehensive analysis of your story's structure, including pacing, dramatic arc,
                    emotional intensity, and key structural elements.
                  </p>
                  <Button
                    variant="primary"
                    onClick={handleAnalyzeStructure}
                    disabled={isAnalyzingStructure}
                  >
                    <SparklesIcon className="h-5 w-5 mr-2" />
                    Analyze Story Structure
                  </Button>
                  <p className="text-xs text-gray-500 mt-4">
                    This will use 25 tokens from your account.
                  </p>
                </div>
              )}
            </div>
          </Tab.Panel>
          
          {/* Scene Suggestions Panel */}
          <Tab.Panel>
            <div className="card">
              <h3 className="text-lg font-medium text-gray-900 mb-4">AI Scene Suggestions</h3>
              
              {isGeneratingSuggestions ? (
                <div className="flex flex-col items-center justify-center min-h-[400px]">
                  <SparklesIcon className="h-12 w-12 text-indigo-500 mb-4 animate-pulse" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Generating Scene Ideas</h3>
                  <p className="text-gray-600 text-center max-w-md mb-6">
                    Our AI is creating fresh scene ideas based on your existing story structure.
                    This may take a minute or two.
                  </p>
                  <LoadingSpinner size="lg" />
                </div>
              ) : sceneSuggestions.length > 0 ? (
                <div className="space-y-6">
                  {sceneSuggestions.map((suggestion, index) => (
                    <div 
                      key={index}
                      className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
                    >
                      <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                        <h4 className="font-medium text-gray-900">Suggestion {index + 1}: {suggestion.title}</h4>
                      </div>
                      <div className="p-4">
                        <div className="prose max-w-none">
                          <p>{suggestion.description}</p>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                          <div>
                            <h5 className="text-sm font-medium text-gray-900 mb-1">Characters</h5>
                            <div className="flex flex-wrap gap-2">
                              {suggestion.characters.map((char: string, i: number) => (
                                <span 
                                  key={i}
                                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                                >
                                  {char}
                                </span>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h5 className="text-sm font-medium text-gray-900 mb-1">Location</h5>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              {suggestion.location}
                            </span>
                          </div>
                          
                          <div>
                            <h5 className="text-sm font-medium text-gray-900 mb-1">Emotional Intensity</h5>
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div 
                                className="bg-blue-600 h-2.5 rounded-full" 
                                style={{ width: `${suggestion.emotionalIntensity * 10}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-gray-500 mt-1">
                              {suggestion.emotionalIntensity}/10
                            </span>
                          </div>
                        </div>
                        
                        <div className="mt-4 pt-4 border-t border-gray-200 flex justify-end">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => navigate(`/projects/${projectId}/scenes/new?suggestion=${index}`)}
                          >
                            Use This Suggestion
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  <div className="flex justify-end">
                    <Button
                      variant="secondary"
                      onClick={handleGenerateSuggestions}
                      disabled={isGeneratingSuggestions}
                    >
                      <SparklesIcon className="h-4 w-4 mr-1" />
                      Generate New Suggestions
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center min-h-[400px]">
                  <LightBulbIcon className="h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Scene Suggestions Yet</h3>
                  <p className="text-gray-600 text-center max-w-md mb-6">
                    Get AI-generated scene ideas based on your current story structure, characters,
                    and narrative progression.
                  </p>
                  <Button
                    variant="primary"
                    onClick={handleGenerateSuggestions}
                    disabled={isGeneratingSuggestions}
                  >
                    <SparklesIcon className="h-5 w-5 mr-2" />
                    Generate Scene Suggestions
                  </Button>
                  <p className="text-xs text-gray-500 mt-4">
                    This will use 15 tokens from your account.
                  </p>
                </div>
              )}
            </div>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};

export default AIFeaturesPage;
