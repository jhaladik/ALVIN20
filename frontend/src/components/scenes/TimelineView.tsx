// File: src/components/scenes/TimelineView.tsx
import { useState } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { Scene } from '../../types';
import { useNavigate } from 'react-router-dom';
import {
  UserIcon,
  MapPinIcon,
  CubeIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  PencilIcon,
  TrashIcon,
  DocumentDuplicateIcon, // Replacement for DuplicateIcon
  PlusIcon
} from '@heroicons/react/24/outline';
import Button from '../ui/Button';

// Map scene type to badge color
const typeColors: Record<string, string> = {
  opening: 'bg-blue-100 text-blue-800',
  inciting: 'bg-purple-100 text-purple-800',
  progressive: 'bg-green-100 text-green-800',
  climax: 'bg-red-100 text-red-800',
  resolution: 'bg-gray-100 text-gray-800'
};

type TimelineViewProps = {
  projectId: string;
  scenes: Scene[];
  onSceneOrderChange: (sceneOrder: { id: string, order: number, sceneType?: string }[]) => Promise<void>;
};

const TimelineView = ({ projectId, scenes, onSceneOrderChange }: TimelineViewProps) => {
  const navigate = useNavigate();
  const [expandedScenes, setExpandedScenes] = useState<Record<string, boolean>>({});
  
  // Toggle scene expansion
  const toggleExpand = (sceneId: string) => {
    setExpandedScenes(prev => ({
      ...prev,
      [sceneId]: !prev[sceneId]
    }));
  };
  
  // Sort scenes by order
  const sortedScenes = [...scenes].sort((a, b) => a.order - b.order);
  
  // Handle drag and drop
  const handleDragEnd = async (result: DropResult) => {
    const { source, destination } = result;
    
    // Dropped outside a valid droppable area
    if (!destination) return;
    
    // Dropped in the same place
    if (source.index === destination.index) return;
    
    // Reorder the scenes
    const newScenes = [...sortedScenes];
    const [removed] = newScenes.splice(source.index, 1);
    newScenes.splice(destination.index, 0, removed);
    
    // Update scene orders
    const updatedScenes = newScenes.map((scene, index) => ({
      id: scene.id,
      order: index + 1
    }));
    
    await onSceneOrderChange(updatedScenes);
  };
  
  // Handle creating a new scene
  const handleCreateScene = () => {
    navigate(`/projects/${projectId}/scenes/new`);
  };
  
  // Handle duplicating a scene
  const handleDuplicateScene = (sceneId: string) => {
    navigate(`/projects/${projectId}/scenes/new?duplicate=${sceneId}`);
  };
  
  // Handle deleting a scene
  const handleDeleteScene = async (sceneId: string) => {
    if (window.confirm('Are you sure you want to delete this scene?')) {
      try {
        await onSceneOrderChange([{ id: sceneId, order: -1 }]); // Use -1 as a signal for deletion
      } catch (error) {
        console.error('Failed to delete scene', error);
      }
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="timeline">
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className="divide-y divide-gray-200"
            >
              {sortedScenes.map((scene, index) => (
                <Draggable key={scene.id} draggableId={scene.id} index={index}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      className={`${
                        snapshot.isDragging ? 'bg-indigo-50' : 'hover:bg-gray-50'
                      }`}
                    >
                      <div
                        {...provided.dragHandleProps}
                        className="p-4"
                      >
                        <div className="flex items-center">
                          {/* Scene info */}
                          <div className="flex-1">
                            <div className="flex items-center">
                              <button
                                type="button"
                                onClick={() => toggleExpand(scene.id)}
                                className="text-gray-400 hover:text-gray-600 mr-2"
                              >
                                {expandedScenes[scene.id] ? (
                                  <ChevronDownIcon className="h-5 w-5" />
                                ) : (
                                  <ChevronRightIcon className="h-5 w-5" />
                                )}
                              </button>
                              
                              <div>
                                <div className="flex items-center">
                                  <span className="font-medium text-gray-900">
                                    {scene.title}
                                  </span>
                                  <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100">
                                    #{scene.order}
                                  </span>
                                  {scene.sceneType && (
                                    <span 
                                      className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${
                                        typeColors[scene.sceneType] || 'bg-gray-100 text-gray-800'
                                      }`}
                                    >
                                      {scene.sceneType.charAt(0).toUpperCase() + scene.sceneType.slice(1)}
                                    </span>
                                  )}
                                </div>
                                
                                {expandedScenes[scene.id] && (
                                  <div className="mt-2">
                                    <p className="text-sm text-gray-500">
                                      {scene.description || 'No description provided.'}
                                    </p>
                                    
                                    <div className="mt-2 flex flex-wrap gap-2">
                                      {scene.characters && scene.characters.length > 0 && (
                                        <div className="inline-flex items-center px-2 py-1 rounded-md bg-indigo-50 text-indigo-700 text-xs">
                                          <UserIcon className="h-3.5 w-3.5 mr-1" />
                                          {scene.characters.length} characters
                                        </div>
                                      )}
                                      
                                      {scene.locations && scene.locations.length > 0 && (
                                        <div className="inline-flex items-center px-2 py-1 rounded-md bg-green-50 text-green-700 text-xs">
                                          <MapPinIcon className="h-3.5 w-3.5 mr-1" />
                                          {scene.locations.length} locations
                                        </div>
                                      )}
                                      
                                      {scene.props && scene.props.length > 0 && (
                                        <div className="inline-flex items-center px-2 py-1 rounded-md bg-amber-50 text-amber-700 text-xs">
                                          <CubeIcon className="h-3.5 w-3.5 mr-1" />
                                          {scene.props.length} props
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          {/* Actions */}
                          <div className="flex-shrink-0 ml-4 flex items-center space-x-2">
                            <button
                              type="button"
                              onClick={() => navigate(`/projects/${projectId}/scenes/${scene.id}`)}
                              className="text-gray-400 hover:text-indigo-600"
                              title="Edit scene"
                            >
                              <PencilIcon className="h-5 w-5" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDuplicateScene(scene.id)}
                              className="text-gray-400 hover:text-indigo-600"
                              title="Duplicate scene"
                            >
                              <DocumentDuplicateIcon className="h-5 w-5" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDeleteScene(scene.id)}
                              className="text-gray-400 hover:text-red-600"
                              title="Delete scene"
                            >
                              <TrashIcon className="h-5 w-5" />
                            </button>
                          </div>
                        </div>
                        
                        {/* Emotional intensity bar */}
                        <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5 hidden sm:block">
                          <div 
                            className="bg-indigo-600 h-1.5 rounded-full" 
                            style={{ width: `${scene.emotionalIntensity * 10}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
              
              {/* Add scene button */}
              <div className="p-4 flex justify-center">
                <Button
                  variant="secondary"
                  onClick={handleCreateScene}
                >
                  <PlusIcon className="h-5 w-5 mr-1" />
                  Add Scene
                </Button>
              </div>
            </div>
          )}
        </Droppable>
      </DragDropContext>
    </div>
  );
};

export default TimelineView;