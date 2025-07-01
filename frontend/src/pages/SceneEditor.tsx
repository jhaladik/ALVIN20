// File: src/pages/SceneEditor.tsx
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import { Scene, StoryObject, AIAnalysis } from '../types'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import Button from '../components/ui/Button'
import {
  ArrowLeftIcon,
  LightBulbIcon,
  DocumentTextIcon,
  PencilIcon,
  TrashIcon,
  ChatBubbleBottomCenterTextIcon,
  BookmarkIcon,
  UserIcon,
  MapPinIcon,
  SparklesIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline'
import SceneContentEditor from '../components/scenes/SceneContentEditor'
import SceneObjectSelector from '../components/scenes/SceneObjectSelector'
import ScenePropertiesPanel from '../components/scenes/ScenePropertiesPanel'
import AICriticPanel from '../components/ai/AICriticPanel'
import CommentSection from '../components/collaboration/CommentSection'
import { useSocket } from '../hooks/useSocket'

type EditorTab = 'write' | 'properties' | 'ai' | 'comments'

const SceneEditor = () => {
  const { projectId, sceneId } = useParams<{ projectId: string; sceneId: string }>()
  const navigate = useNavigate()
  const { socket, isConnected } = useSocket()
  
  const [scene, setScene] = useState<Scene | null>(null)
  const [projectObjects, setProjectObjects] = useState<{
    characters: StoryObject[]
    locations: StoryObject[]
    props: StoryObject[]
  }>({
    characters: [],
    locations: [],
    props: [],
  })
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<EditorTab>('write')
  const [isAiAnalyzing, setIsAiAnalyzing] = useState(false)
  const [activeCriticType, setActiveCriticType] = useState<string>('general')
  
  // Setup real-time socket for collaborative editing
  useEffect(() => {
    if (!socket || !isConnected || !sceneId) return
    
    // Join scene room
    socket.emit('join_scene', { sceneId })
    
    // Listen for scene updates
    socket.on('scene_updated', (updatedScene: Scene) => {
      if (updatedScene.id === sceneId) {
        setScene(updatedScene)
      }
    })
    
    // Listen for new AI analysis
    socket.on('ai_analysis_completed', (analysis: AIAnalysis) => {
      if (analysis.targetId === sceneId) {
        setAiAnalysis(prev => [...prev, analysis])
        setIsAiAnalyzing(false)
      }
    })
    
    return () => {
      // Leave scene room on unmount
      socket.emit('leave_scene', { sceneId })
      socket.off('scene_updated')
      socket.off('ai_analysis_completed')
    }
  }, [socket, isConnected, sceneId])
  
  // Load scene data
  useEffect(() => {
    const loadSceneData = async () => {
      if (!projectId || !sceneId) return
      
      try {
        setIsLoading(true)
        const isNewScene = sceneId === 'new'
        
        if (isNewScene) {
          // For new scene, just load project objects
          const objectsResponse = await api.get(`/api/projects/${projectId}/objects`)
          
          const defaultNewScene: Scene = {
            id: '',
            projectId: projectId,
            title: 'Untitled Scene',
            content: '',
            emotionalIntensity: 5,
            order: 1, // Will be set to highest order + 1 on save
            characters: [],
            locations: [],
            props: [],
            createdAt: new Date().toISOString(),
            lastModified: new Date().toISOString(),
          }
          
          setScene(defaultNewScene)
          
          // Organize objects by type
          const characters = objectsResponse.data.filter(
            (obj: StoryObject) => obj.type === 'character'
          )
          const locations = objectsResponse.data.filter(
            (obj: StoryObject) => obj.type === 'location'
          )
          const props = objectsResponse.data.filter(
            (obj: StoryObject) => obj.type === 'prop'
          )
          
          setProjectObjects({
            characters,
            locations,
            props,
          })
        } else {
          // For existing scene, load scene, objects, and AI analysis
          const [sceneResponse, objectsResponse, aiResponse] = await Promise.all([
            api.get(`/api/scenes/${sceneId}`),
            api.get(`/api/projects/${projectId}/objects`),
            api.get(`/api/ai/analysis?targetId=${sceneId}&targetType=scene`),
          ])
          
          setScene(sceneResponse.data)
          setAiAnalysis(aiResponse.data)
          
          // Organize objects by type
          const characters = objectsResponse.data.filter(
            (obj: StoryObject) => obj.type === 'character'
          )
          const locations = objectsResponse.data.filter(
            (obj: StoryObject) => obj.type === 'location'
          )
          const props = objectsResponse.data.filter(
            (obj: StoryObject) => obj.type === 'prop'
          )
          
          setProjectObjects({
            characters,
            locations,
            props,
          })
        }
      } catch (err) {
        console.error('Failed to load scene data', err)
        setError('Failed to load scene data. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
    
    loadSceneData()
  }, [projectId, sceneId])
  
  const handleSaveScene = async () => {
    if (!scene || !projectId) return
    
    try {
      setIsSaving(true)
      let response
      
      if (sceneId === 'new') {
        // For new scenes, get the highest order
        const scenesResponse = await api.get(`/api/scenes?projectId=${projectId}`)
        const scenes = scenesResponse.data
        const highestOrder = scenes.length > 0 
          ? Math.max(...scenes.map((s: Scene) => s.order)) 
          : 0
          
        // Create new scene
        response = await api.post('/api/scenes', {
          ...scene,
          projectId,
          order: highestOrder + 1,
        })
        
        // Navigate to the newly created scene
        navigate(`/projects/${projectId}/scenes/${response.data.id}`, { replace: true })
      } else {
        // Update existing scene
        response = await api.put(`/api/scenes/${scene.id}`, scene)
      }
      
      setScene(response.data)
      
      // Emit scene update event for real-time collaboration
      if (socket && isConnected) {
        socket.emit('scene_update', response.data)
      }
    } catch (err) {
      console.error('Failed to save scene', err)
      setError('Failed to save scene. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }
  
  const handleDeleteScene = async () => {
    if (!scene || !projectId || sceneId === 'new') return
    
    if (!confirm('Are you sure you want to delete this scene? This action cannot be undone.')) {
      return
    }
    
    try {
      await api.delete(`/api/scenes/${scene.id}`)
      navigate(`/projects/${projectId}`)
    } catch (err) {
      console.error('Failed to delete scene', err)
      setError('Failed to delete scene. Please try again.')
    }
  }
  
  const updateSceneContent = (content: string) => {
    if (!scene) return
    setScene({ ...scene, content, lastModified: new Date().toISOString() })
  }
  
  const updateSceneTitle = (title: string) => {
    if (!scene) return
    setScene({ ...scene, title, lastModified: new Date().toISOString() })
  }
  
  const updateSceneObjects = (
    type: 'characters' | 'locations' | 'props',
    objectIds: string[]
  ) => {
    if (!scene) return
    setScene({ ...scene, [type]: objectIds, lastModified: new Date().toISOString() })
  }
  
  const updateSceneProperties = (properties: Partial<Scene>) => {
    if (!scene) return
    setScene({ ...scene, ...properties, lastModified: new Date().toISOString() })
  }
  
  const requestAiAnalysis = async (criticType: string) => {
    if (!scene || !projectId || sceneId === 'new') return
    
    try {
      setIsAiAnalyzing(true)
      setActiveCriticType(criticType)
      
      // Save the scene first to ensure the latest content is analyzed
      await handleSaveScene()
      
      // Request AI analysis
      await api.post(`/api/ai/analyze-scene`, {
        sceneId: scene.id,
        criticType,
      })
      
      // The socket will handle the response when analysis is completed
    } catch (err) {
      console.error('Failed to request AI analysis', err)
      setError('Failed to request AI analysis. Please try again.')
      setIsAiAnalyzing(false)
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }
  
  if (!scene && !isLoading) {
    return (
      <div className="text-center py-12">
        <ExclamationCircleIcon className="h-12 w-12 text-red-500 mx-auto" />
        <h2 className="mt-4 text-lg font-medium text-gray-900">Scene not found</h2>
        <p className="mt-2 text-gray-600">This scene may have been deleted or you don't have access.</p>
        <Button 
          variant="primary" 
          className="mt-4" 
          onClick={() => navigate(`/projects/${projectId}`)}
        >
          Back to Project
        </Button>
      </div>
    )
  }
  
  return (
    <div className="h-full flex flex-col">
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
      
      {/* Scene header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Button
            variant="ghost"
            onClick={() => navigate(`/projects/${projectId}`)}
            className="mr-2"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </Button>
          
          <div>
            <div className="flex items-center">
              <input
                type="text"
                value={scene?.title || ''}
                onChange={(e) => updateSceneTitle(e.target.value)}
                className="text-2xl font-bold text-gray-900 border-none focus:ring-0 focus:outline-none p-0 bg-transparent"
                placeholder="Untitled Scene"
              />
            </div>
            
            <p className="text-sm text-gray-500">
              Scene #{scene?.order} • Last modified: {new Date(scene?.lastModified || '').toLocaleString()}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="primary"
            onClick={handleSaveScene}
            isLoading={isSaving}
          >
            Save
          </Button>
          
          {sceneId !== 'new' && (
            <Button
              variant="danger"
              onClick={handleDeleteScene}
            >
              <TrashIcon className="h-5 w-5" />
            </Button>
          )}
        </div>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-gray-200 mb-4">
        <nav className="-mb-px flex space-x-6">
          <button
            className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center ${
              activeTab === 'write'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('write')}
          >
            <DocumentTextIcon className="h-5 w-5 mr-2" />
            Write
          </button>
          <button
            className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center ${
              activeTab === 'properties'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('properties')}
          >
            <PencilIcon className="h-5 w-5 mr-2" />
            Properties
          </button>
          <button
            className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center ${
              activeTab === 'ai'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('ai')}
          >
            <SparklesIcon className="h-5 w-5 mr-2" />
            AI Critics
          </button>
          <button
            className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center ${
              activeTab === 'comments'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setActiveTab('comments')}
          >
            <ChatBubbleBottomCenterTextIcon className="h-5 w-5 mr-2" />
            Comments
          </button>
        </nav>
      </div>
      
      {/* Tab content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'write' && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="md:col-span-3">
              <SceneContentEditor 
                content={scene?.content || ''}
                onChange={updateSceneContent}
              />
            </div>
            
            <div className="space-y-6">
              <SceneObjectSelector
                title="Characters"
                icon={<UserIcon className="h-5 w-5" />}
                selectedIds={scene?.characters || []}
                objects={projectObjects.characters}
                onChange={(ids) => updateSceneObjects('characters', ids)}
              />
              
              <SceneObjectSelector
                title="Locations"
                icon={<MapPinIcon className="h-5 w-5" />}
                selectedIds={scene?.locations || []}
                objects={projectObjects.locations}
                onChange={(ids) => updateSceneObjects('locations', ids)}
              />
              
              <SceneObjectSelector
                title="Props"
                icon={<BookmarkIcon className="h-5 w-5" />}
                selectedIds={scene?.props || []}
                objects={projectObjects.props}
                onChange={(ids) => updateSceneObjects('props', ids)}
              />
              
              <div className="card">
                <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                  <LightBulbIcon className="h-5 w-5 text-yellow-500 mr-1" />
                  AI Suggestion
                </h3>
                <p className="text-sm text-gray-600">
                  Save your scene to get AI suggestions for improvement or click the AI Critics tab.
                </p>
                <Button
                  variant="secondary"
                  size="sm"
                  className="mt-3 w-full"
                  onClick={() => {
                    handleSaveScene().then(() => {
                      setActiveTab('ai')
                      requestAiAnalysis('general')
                    })
                  }}
                >
                  <SparklesIcon className="h-4 w-4 mr-2" />
                  Get Suggestions
                </Button>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'properties' && scene && (
          <ScenePropertiesPanel
            scene={scene}
            onUpdate={updateSceneProperties}
          />
        )}
        
        {activeTab === 'ai' && (
          <AICriticPanel
            sceneId={scene?.id || ''}
            aiAnalysis={aiAnalysis}
            isAnalyzing={isAiAnalyzing}
            activeCriticType={activeCriticType}
            onRequestAnalysis={requestAiAnalysis}
          />
        )}
        
        {activeTab === 'comments' && sceneId !== 'new' && (
          <CommentSection targetId={sceneId} targetType="scene" />
        )}
        
        {activeTab === 'comments' && sceneId === 'new' && (
          <div className="text-center py-12">
            <ChatBubbleBottomCenterTextIcon className="h-12 w-12 text-gray-400 mx-auto" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Save this scene first</h3>
            <p className="mt-1 text-sm text-gray-500">
              You need to save this scene before you can add comments.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default SceneEditor