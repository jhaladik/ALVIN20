// src/types/ai.ts
// TypeScript interfaces for AI-related data structures

export interface AICritic {
    id: string;
    name: string;
    specialty: string;
    description: string;
    color: string;
    focusAreas: string[];
    tokenCost: number;
  }
  
  export interface AIAnalysis {
    id: string;
    criticType: string;
    targetId: string; // sceneId or projectId
    targetType: 'scene' | 'project';
    content: string;
    rating?: number;
    recommendations?: string[];
    createdAt: string;
    updatedAt: string;
    tokenCost: number;
  }
  
  export interface AIAnalysisRequest {
    sceneId?: string;
    projectId?: string;
    criticType: string;
  }
  
  export interface AIAnalysisResponse {
    success: boolean;
    analysis?: AIAnalysis;
    error?: string;
    tokenCost?: number;
    remainingTokens?: number;
  }
  
  // Predefined critics with their details
  export const AI_CRITICS: AICritic[] = [
    {
      id: 'structure',
      name: 'Professor Syntax',
      specialty: 'Story Structure',
      description: 'Analyzes story structure and pacing with an academic approach',
      color: 'bg-indigo-100 text-indigo-800',
      focusAreas: ['Three-act structure', 'Dramatic tension', 'Scene transitions', 'Plot progression'],
      tokenCost: 12
    },
    {
      id: 'character',
      name: 'Character Whisperer',
      specialty: 'Character Development',
      description: 'Examines character psychology, arcs, and relationships',
      color: 'bg-blue-100 text-blue-800',
      focusAreas: ['Character arcs', 'Motivation consistency', 'Dialogue authenticity', 'Relationships'],
      tokenCost: 12
    },
    {
      id: 'dialog',
      name: 'Dialog Master',
      specialty: 'Dialogue Quality',
      description: 'Evaluates dialogue authenticity, flow, and character voice',
      color: 'bg-purple-100 text-purple-800',
      focusAreas: ['Natural speech patterns', 'Character voice distinction', 'Subtext', 'Dialogue mechanics'],
      tokenCost: 8
    },
    {
      id: 'pacing',
      name: 'Tempo Conductor',
      specialty: 'Pacing & Rhythm',
      description: 'Assesses narrative pacing, tension building, and flow',
      color: 'bg-amber-100 text-amber-800',
      focusAreas: ['Scene rhythm', 'Information flow', 'Tension building', 'Reader engagement'],
      tokenCost: 12
    },
    {
      id: 'genre',
      name: 'Genre Guru',
      specialty: 'Genre Conventions',
      description: 'Analyzes adherence to genre expectations and tropes',
      color: 'bg-rose-100 text-rose-800',
      focusAreas: ['Genre tropes', 'Reader expectations', 'Market fit', 'Genre-specific techniques'],
      tokenCost: 10
    },
    {
      id: 'plot_holes',
      name: 'Logic Detective',
      specialty: 'Plot Consistency',
      description: 'Identifies logical inconsistencies and plot holes',
      color: 'bg-green-100 text-green-800',
      focusAreas: ['Plot consistency', 'Logical gaps', 'Continuity errors', 'Cause-effect chains'],
      tokenCost: 15
    },
    {
      id: 'conflict',
      name: 'Conflict Architect',
      specialty: 'Conflict Development',
      description: 'Evaluates conflict escalation, stakes, and resolution',
      color: 'bg-teal-100 text-teal-800',
      focusAreas: ['Conflict types', 'Escalation patterns', 'Resolution satisfaction', 'Stakes progression'],
      tokenCost: 8
    },
    {
      id: 'world_building',
      name: 'World Weaver',
      specialty: 'Setting & World',
      description: 'Examines world-building, setting consistency, and atmosphere',
      color: 'bg-orange-100 text-orange-800',
      focusAreas: ['Setting consistency', 'Cultural logic', 'Environmental details', 'World rules'],
      tokenCost: 10
    }
  ];
  