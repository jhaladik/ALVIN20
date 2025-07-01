// File: src/components/scenes/KanbanBoard.tsx
import { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd';
import { Scene } from '../../types';
import SceneCard from './SceneCard';
import Button from '../ui/Button';
import { PlusIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';

// Define scene types for columns
const sceneTypes = [
  { id: 'opening', label: 'Opening' },
  { id: 'inciting', label: 'Inciting Incident' },
  { id: 'progressive', label: 'Progressive Complications' },
  { id: 'climax', label: 'Climax' },
  { id: 'resolution', label: 'Resolution' }
];

type KanbanBoardProps = {
  projectId: string;
  scenes: Scene[];
  onSceneOrderChange: (sceneOrder: { id: string, order: number, sceneType?: string }[]) => Promise<void>;
};

const KanbanBoard = ({ projectId, scenes, onSceneOrderChange }: KanbanBoardProps) => {
  const navigate = useNavigate();
  
  // Organize scenes by type
  const [columns, setColumns] = useState<Record<string, Scene[]>>({
    opening: [],
    inciting: [],
    progressive: [],
    climax: [],
    resolution: []
  });
  
  // Update columns when scenes change
  useEffect(() => {
    // Group scenes by type
    const newColumns: Record<string, Scene[]> = {
      opening: [],
      inciting: [],
      progressive: [],
      climax: [],
      resolution: []
    };
    
    // Add scenes to their respective columns
    scenes.forEach(scene => {
      const type = scene.sceneType || 'progressive'; // Default to progressive if no type set
      if (newColumns[type]) {
        newColumns[type].push(scene);
      } else {
        newColumns.progressive.push(scene);
      }
    });
    
    // Sort scenes within each column by order
    Object.keys(newColumns).forEach(type => {
      newColumns[type].sort((a, b) => a.order - b.order);
    });
    
    setColumns(newColumns);
  }, [scenes]);
  
  // Handle drag and drop
  const handleDragEnd = async (result: DropResult) => {
    const { source, destination } = result;
    
    // Dropped outside a valid droppable area
    if (!destination) return;
    
    // Dropped in the same place
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) {
      return;
    }
    
    // Moving within the same column
    if (source.droppableId === destination.droppableId) {
      const column = [...columns[source.droppableId]];
      const [removed] = column.splice(source.index, 1);
      column.splice(destination.index, 0, removed);
      
      setColumns({
        ...columns,
        [source.droppableId]: column
      });
      
      // Update scene orders
      const updatedScenes = column.map((scene, index) => ({
        id: scene.id,
        order: index + 1,
        sceneType: source.droppableId as Scene['sceneType']
      }));
      
      await onSceneOrderChange(updatedScenes);
      return;
    }
    
    // Moving from one column to another
    const sourceColumn = [...columns[source.droppableId]];
    const destColumn = [...columns[destination.droppableId]];
    const [removed] = sourceColumn.splice(source.index, 1);
    
    // Update the scene's type
    const updatedScene = { ...removed, sceneType: destination.droppableId as Scene['sceneType'] };
    
    destColumn.splice(destination.index, 0, updatedScene);
    
    setColumns({
      ...columns,
      [source.droppableId]: sourceColumn,
      [destination.droppableId]: destColumn
    });
    
    // Collect all the scenes that need to be updated
    const sourceUpdates = sourceColumn.map((scene, index) => ({
      id: scene.id,
      order: index + 1,
      sceneType: source.droppableId as Scene['sceneType']
    }));
    
    const destUpdates = destColumn.map((scene, index) => ({
      id: scene.id,
      order: index + 1,
      sceneType: destination.droppableId as Scene['sceneType']
    }));
    
    await onSceneOrderChange([...sourceUpdates, ...destUpdates]);
  };
  
  // Create a new scene
  const handleCreateScene = (sceneType: Scene['sceneType']) => {
    navigate(`/projects/${projectId}/scenes/new?type=${sceneType}`);
  };
  
  return (
    <div className="overflow-x-auto pb-4">
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="flex space-x-4 min-w-max">
          {sceneTypes.map(({ id, label }) => (
            <div key={id} className="w-80 flex-shrink-0">
              {/* Column header */}
              <div className="flex items-center justify-between mb-3 px-2">
                <h3 className="font-semibold text-gray-700">
                  {label} <span className="text-gray-500 text-sm">({columns[id].length})</span>
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCreateScene(id as Scene['sceneType'])}
                >
                  <PlusIcon className="h-4 w-4" />
                </Button>
              </div>
              
              {/* Droppable column */}
              <Droppable droppableId={id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`min-h-[500px] p-3 rounded-lg ${
                      snapshot.isDraggingOver ? 'bg-indigo-50' : 'bg-gray-50'
                    }`}
                  >
                    {columns[id].map((scene, index) => (
                      <Draggable key={scene.id} draggableId={scene.id} index={index}>
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`mb-3 ${
                              snapshot.isDragging ? 'opacity-70' : ''
                            }`}
                          >
                            <SceneCard
                              scene={scene}
                              onClick={() => navigate(`/projects/${projectId}/scenes/${scene.id}`)}
                            />
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                    
                    {/* Add scene button at bottom of empty column */}
                    {columns[id].length === 0 && (
                      <button
                        onClick={() => handleCreateScene(id as Scene['sceneType'])}
                        className="w-full py-3 border-2 border-dashed border-gray-300 rounded-md text-sm text-gray-500 flex items-center justify-center hover:bg-gray-100 transition-colors"
                      >
                        <PlusIcon className="h-5 w-5 mr-1" />
                        Add Scene
                      </button>
                    )}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>
    </div>
  );
};

export default KanbanBoard;
