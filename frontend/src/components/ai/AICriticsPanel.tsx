// src/components/ai/AICriticsPanel.tsx
import React from 'react';
import { SparklesIcon } from '@heroicons/react/24/outline';
import { InformationCircleIcon } from '@heroicons/react/24/solid';
import { AIAnalysis, AI_CRITICS } from '../../types/ai';
import Button from '../ui/Button';
import LoadingSpinner from '../ui/LoadingSpinner';
import AIAnalysisCard from './AIAnalysisCard';

interface AICriticsPanelProps {
  sceneId?: string;
  projectId?: string;
  analyses: AIAnalysis[];
  isAnalyzing: boolean;
  activeCriticType: string;
  error: string | null;
  onRequestAnalysis: (criticType: string) => void;
  onActiveCriticChange: (criticType: string) => void;
}

const AICriticsPanel: React.FC<AICriticsPanelProps> = ({
  sceneId,
  projectId,
  analyses,
  isAnalyzing,
  activeCriticType,
  error,
  onRequestAnalysis,
  onActiveCriticChange,
}) => {
  // Get filtered analyses for the active critic
  const filteredAnalyses = analyses.filter(
    (analysis) => analysis.criticType === activeCriticType
  ).sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  // Get date formatted for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  // Get the active critic's color
  const getActiveCriticColor = () => {
    const critic = AI_CRITICS.find((c) => c.id === activeCriticType);
    return critic?.color || 'bg-gray-100 text-gray-800';
  };

  // Get the active critic
  const activeCritic = AI_CRITICS.find((c) => c.id === activeCriticType);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Critics sidebar */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">AI Critics</h3>

        <div className="space-y-2">
          {AI_CRITICS.map((critic) => (
            <button
              key={critic.id}
              onClick={() => onActiveCriticChange(critic.id)}
              disabled={isAnalyzing}
              className={`w-full flex items-center justify-between p-3 rounded-md text-sm font-medium transition-colors ${
                activeCriticType === critic.id
                  ? 'bg-indigo-50 border border-indigo-200'
                  : 'hover:bg-gray-50 border border-transparent'
              }`}
            >
              <div className="flex items-center">
                <span className={`inline-flex items-center justify-center h-6 w-6 rounded-full ${critic.color} mr-2 text-xs`}>
                  AI
                </span>
                <div className="flex flex-col items-start">
                  <span>{critic.name}</span>
                  <span className="text-xs text-gray-500">{critic.specialty}</span>
                </div>
              </div>
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${
                  analyses.some((a) => a.criticType === critic.id)
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {analyses.some((a) => a.criticType === critic.id) ? 'Available' : 'New'}
              </span>
            </button>
          ))}
        </div>

        <div className="mt-6 space-y-2 text-xs text-gray-500">
          <p>Each AI critic provides specialized feedback from a different perspective.</p>
          <p>Running an AI analysis will use tokens from your account.</p>
          {activeCritic && (
            <div className="p-3 bg-indigo-50 rounded-md mt-4">
              <div className="flex items-start">
                <InformationCircleIcon className="h-5 w-5 text-indigo-500 mr-2 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-indigo-800">{activeCritic.name}</p>
                  <p className="mt-1">{activeCritic.description}</p>
                  <p className="mt-2 font-medium text-indigo-800">Focus areas:</p>
                  <ul className="list-disc list-inside mt-1 ml-1 space-y-1">
                    {activeCritic.focusAreas.map((area, index) => (
                      <li key={index}>{area}</li>
                    ))}
                  </ul>
                  <p className="mt-2">
                    Cost: <span className="font-medium">{activeCritic.tokenCost} tokens</span>
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Analysis content */}
      <div className="md:col-span-2">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md mb-4">
            {error}
          </div>
        )}

        {isAnalyzing ? (
          <div className="card flex flex-col items-center justify-center min-h-[400px]">
            <SparklesIcon className="h-12 w-12 text-indigo-500 mb-4 animate-pulse" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">AI Analysis in Progress</h3>
            <p className="text-gray-600 text-center max-w-md mb-6">
              Our AI critic is carefully analyzing your{' '}
              {sceneId ? 'scene' : 'project'} from the perspective of 
              "{AI_CRITICS.find((c) => c.id === activeCriticType)?.name}".
              This may take up to a minute.
            </p>
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredAnalyses.length > 0 ? (
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <span
                  className={`inline-flex items-center justify-center h-6 w-6 rounded-full ${getActiveCriticColor()} mr-2 text-xs`}
                >
                  AI
                </span>
                {AI_CRITICS.find((c) => c.id === activeCriticType)?.name} Analysis
              </h3>

              <Button
                variant="secondary"
                size="sm"
                onClick={() => onRequestAnalysis(activeCriticType)}
                disabled={isAnalyzing}
              >
                <SparklesIcon className="h-4 w-4 mr-1" />
                Refresh Analysis
              </Button>
            </div>

            <div className="space-y-6">
              {filteredAnalyses.map((analysis) => (
                <AIAnalysisCard 
                  key={analysis.id} 
                  analysis={analysis} 
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="card flex flex-col items-center justify-center min-h-[400px]">
            <SparklesIcon className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Yet</h3>
            <p className="text-gray-600 text-center max-w-md mb-6">
              Get insights from our AI critic on your {sceneId ? 'scene' : 'project'}'s{' '}
              {AI_CRITICS.find((c) => c.id === activeCriticType)?.specialty.toLowerCase()}.
            </p>
            <Button
              variant="primary"
              onClick={() => onRequestAnalysis(activeCriticType)}
              disabled={isAnalyzing}
            >
              <SparklesIcon className="h-5 w-5 mr-2" />
              Run AI Analysis
            </Button>
            <p className="text-xs text-gray-500 mt-4">
              This will use {AI_CRITICS.find((c) => c.id === activeCriticType)?.tokenCost} tokens from your account.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AICriticsPanel;
