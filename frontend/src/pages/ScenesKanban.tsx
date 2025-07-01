// File: src/pages/ScenesKanban.tsx
import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import { Scene } from '../types'
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import Button from '../components/ui/Button'
import {
  PlusIcon,
  ArrowPathIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'

// Note: In a real implementation, you would need to install this dependency:
// npm install react-beautiful-dnd

const ScenesKanban = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const [scenes, setScenes] = useState<Scene[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Load scenes
  useEffect(() => {
    const loadScenes = async () => {
      if (!projectId) return
      
      try {
        setIsLoading(true)
        const response = await api.get(`/api/scenes?projectId=${projectId}`)
        
        // Sort scenes by order
        const sortedScenes = response.data.sort((a: Scene, b: Scene) => a.order - b.order)
        setScenes(sortedScenes)
      } catch (err) {
        console.error('Failed to load scenes', err)
        setError('Failed to load scenes. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
    
    loadScenes()
  }, [projectId])
  
  // Update scene orders after drag and drop
  const handleDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result
    
    // If dropped outside a droppable area or same position
    if (!destination || (destination.index === source.index)) {
      return
    }
    
    // Create a copy of scenes
    const newScenes = Array.from(scenes)
    
    // Get the dragged scene
    const draggedScene = newScenes.find(scene => scene.id === draggableId)
    
    if (!draggedScene) return
    
    // Remove from the original position
    newScenes.splice(source.index, 1)
    
    // Insert at the new position
    newScenes.splice(destination.index, 0, draggedScene)
    
    // Update scene orders
    const updatedScenes = newScenes.map((scene, index) => ({
      ...scene,
      order: index + 1,
    }))
    
    // Update state optimistically
    setScenes(updatedScenes)
    
    // Update on the server
    try {
      await Promise.all(
        updatedScenes.map(scene => 
          api.put(`/api/scenes/${scene.id}`, {
            ...scene,
            order: scene.order
          })
        )
      )
    } catch (err) {
      console.error('Failed to update scene orders', err)
      setError('Failed to update scene orders. Please try again.')
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
      
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900">Scene Timeline</h2>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => window.location.reload()}
          >
            <ArrowPathIcon className="h-5 w-5 mr-1" />
            Refresh
          </Button>
          <Link to={`/projects/${projectId}/scenes/new`} className="btn-primary inline-flex items-center">
            <PlusIcon className="h-5 w-5 mr-1" />
            Add Scene
          </Link>
        </div>
      </div>
      
      {scenes.length > 0 ? (
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="scenes" direction="vertical">
            {(provided) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="space-y-4"
              >
                {scenes.map((scene, index) => (
                  <Draggable key={scene.id} draggableId={scene.id} index={index}>
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        className="card border border-gray-200 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start">
                          <div 
                            {...provided.dragHandleProps} 
                            className="h-8 w-8 bg-gray-100 rounded-full flex items-center justify-center mr-4 cursor-grab"
                          >
                            {scene.order}
                          </div>
                          
                          <div className="flex-1">
                            <Link to={`/projects/${projectId}/scenes/${scene.id}`} className="block">
                              <h3 className="text-lg font-medium text-gray-900 hover:text-indigo-600">
                                {scene.title}
                              </h3>
                              <div className="mt-2">
                                <div className="text-sm text-gray-600 line-clamp-2">
                                  {scene.content.replace(/<[^>]*>/g, '')}
                                </div>
                              </div>
                            </Link>
                            
                            <div className="mt-4 flex flex-wrap gap-2">
                              {scene.characters.length > 0 && (
                                <div className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
                                  {scene.characters.length} character{scene.characters.length !== 1 ? 's' : ''}
                                </div>
                              )}
                              
                              {scene.locations.length > 0 && (
                                <div className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded-full">
                                  {scene.locations.length} location{scene.locations.length !== 1 ? 's' : ''}
                                </div>
                              )}
                              
                              {scene.props.length > 0 && (
                                <div className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full">
                                  {scene.props.length} prop{scene.props.length !== 1 ? 's' : ''}
                                </div>
                              )}
                              
                              <div className="text-xs bg-yellow-50 text-yellow-700 px-2 py-1 rounded-full">
                                Intensity: {scene.emotionalIntensity}/10
                              </div>
                            </div>
                          </div>
                          
                          <Link 
                            to={`/projects/${projectId}/scenes/${scene.id}`}
                            className="inline-flex items-center ml-4 text-sm text-indigo-600 hover:text-indigo-500"
                          >
                            Edit
                          </Link>
                        </div>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      ) : (
        <div className="text-center py-16 border border-dashed border-gray-300 rounded-md">
          <SparklesIcon className="h-12 w-12 text-gray-400 mx-auto" />
          <h3 className="mt-4 text-sm font-medium text-gray-900">No scenes yet</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating your first scene.</p>
          <div className="mt-6">
            <Link 
              to={`/projects/${projectId}/scenes/new`}
              className="btn-primary inline-flex items-center"
            >
              <PlusIcon className="h-5 w-5 mr-1" />
              Create First Scene
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default ScenesKanban