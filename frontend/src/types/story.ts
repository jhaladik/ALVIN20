// src/types/story.ts
export interface NarrativeOptions {
    narrativeVoice: 'first_person' | 'third_person_limited' | 'third_person_omniscient';
    proseStyle: 'minimal' | 'balanced' | 'descriptive';
    dialogStyle: 'direct' | 'indirect' | 'mixed';
    tonePreference: string;
  }
  
  export interface ChapterData {
    id: string;
    title: string;
    content: string;
    scenes: string[]; // Array of scene IDs that make up this chapter
    order: number;
  }
  
  export interface StoryMetadata {
    genre: string;
    theme: string;
    targetAudience: string;
    tone: string;
    uniqueElements: string[];
    keySymbols: string[];
    marketabilityScore?: number;
    qualityScore?: number;
  }
  
  export interface StoryData {
    id: string;
    projectId: string;
    title: string;
    premise: string;
    content: string;
    metadata: StoryMetadata;
    chapters?: ChapterData[];
    wordCount?: number;
    createdAt: string;
    updatedAt: string;
  }
  
  export interface StoryStats {
    wordCount: number;
    pageCount: number;
    readingTime: number;
    marketabilityScore: number;
    overallQuality: number;
  }