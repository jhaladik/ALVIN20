// src/hooks/useAIAnalysis.ts
import { useState, useEffect, useCallback } from 'react';
import { Socket } from 'socket.io-client';
import { AIAnalysis } from '../types/ai';
import aiService from '../services/aiService';

interface UseAIAnalysisProps {
  sceneId?: string;
  projectId?: string;
  socket: Socket | null;
  isConnected: boolean;
}

export function useAIAnalysis({
  sceneId,
  projectId,
  socket,
  isConnected,
}: UseAIAnalysisProps) {
  const [analyses, setAnalyses] = useState<AIAnalysis[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeCriticType, setActiveCriticType] = useState<string>('structure');
  const [error, setError] = useState<string | null>(null);

  // Load initial analyses
  useEffect(() => {
    const loadAnalyses = async () => {
      try {
        if (sceneId) {
          const sceneAnalyses = await aiService.getSceneAnalyses(sceneId);
          setAnalyses(sceneAnalyses);
        } else if (projectId) {
          const projectAnalyses = await aiService.getProjectAnalyses(projectId);
          setAnalyses(projectAnalyses);
        }
      } catch (err) {
        console.error('Failed to load analyses', err);
        setError('Failed to load previous analyses');
      }
    };

    loadAnalyses();
  }, [sceneId, projectId]);

  // Setup socket listeners
  useEffect(() => {
    if (!socket || !isConnected) return;

    // Listen for new AI analysis
    socket.on('ai_analysis_completed', (analysis: AIAnalysis) => {
      const targetMatches = 
        (sceneId && analysis.targetId === sceneId) || 
        (projectId && analysis.targetId === projectId);
      
      if (targetMatches) {
        setAnalyses(prev => {
          // Replace if same type exists, otherwise add
          const exists = prev.some(a => a.criticType === analysis.criticType);
          if (exists) {
            return prev.map(a => 
              a.criticType === analysis.criticType ? analysis : a
            );
          } else {
            return [...prev, analysis];
          }
        });
        
        // If this is the active critic, clear analyzing state
        if (analysis.criticType === activeCriticType) {
          setIsAnalyzing(false);
        }
      }
    });

    // Error handling
    socket.on('ai_analysis_error', (data: { criticType: string, error: string }) => {
      if (data.criticType === activeCriticType) {
        setIsAnalyzing(false);
        setError(`Analysis failed: ${data.error}`);
      }
    });

    return () => {
      socket.off('ai_analysis_completed');
      socket.off('ai_analysis_error');
    };
  }, [socket, isConnected, sceneId, projectId, activeCriticType]);

  // Request analysis function
  const requestAnalysis = useCallback(async (criticType: string) => {
    setError(null);
    setIsAnalyzing(true);
    setActiveCriticType(criticType);

    try {
      if (sceneId) {
        await aiService.analyzeScene(sceneId, criticType);
      } else if (projectId) {
        await aiService.analyzeProject(projectId, criticType);
      } else {
        throw new Error('No scene or project ID provided');
      }
      
      // The socket will handle the response when analysis is completed
    } catch (err: any) {
      console.error('Failed to request AI analysis', err);
      setIsAnalyzing(false);
      setError(err.message || 'Failed to request AI analysis');
    }
  }, [sceneId, projectId]);

  // Get filtered analyses for the active critic
  const activeAnalyses = analyses.filter(
    analysis => analysis.criticType === activeCriticType
  ).sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  return {
    analyses,
    activeAnalyses,
    isAnalyzing,
    activeCriticType,
    setActiveCriticType,
    error,
    requestAnalysis,
  };
}

export default useAIAnalysis;
