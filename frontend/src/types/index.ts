// File: src/types/index.ts
// Define all types used across the application here
export type User = {
    id: string
    username: string
    email: string
    plan: string
    tokensRemaining: number
    createdAt: string
  }
  
  export type Project = {
    id: string
    title: string
    description: string
    phase: 'idea' | 'expand' | 'story'
    createdAt: string
    lastModified: string
    progress: number
    collaborators: string[]
  }
  
  export type Scene = {
    id: string
    projectId: string
    title: string
    content: string
    emotionalIntensity: number
    order: number
    characters: string[]
    locations: string[]
    props: string[]
    aiAnalysis?: AIAnalysis
    createdAt: string
    lastModified: string
  }
  
  export type StoryObject = {
    id: string
    projectId: string
    type: 'character' | 'location' | 'prop'
    name: string
    description: string
    attributes: Record<string, any>
    relationships: Relationship[]
  }
  
  export type Relationship = {
    targetId: string
    type: string
    description: string
  }
  
  export type AIAnalysis = {
    id: string
    targetId: string
    targetType: 'project' | 'scene' | 'object'
    criticType: string
    content: string
    createdAt: string
  }
  
  export type Comment = {
    id: string
    userId: string
    username: string
    targetId: string
    targetType: 'project' | 'scene' | 'object'
    content: string
    createdAt: string
  }
  
  export type Notification = {
    id: string
    userId: string
    type: string
    message: string
    read: boolean
    targetId?: string
    targetType?: 'project' | 'scene' | 'comment'
    createdAt: string
  }