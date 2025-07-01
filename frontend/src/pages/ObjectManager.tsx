// File: src/pages/ObjectManager.tsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Button from '../components/ui/Button';
import ObjectList from '../components/objects/ObjectList';
import ObjectDetail from '../components/objects/ObjectDetail';
import RelationshipGraph from '../components/objects/RelationshipGraph';
import ObjectCreateModal from '../components/objects/ObjectCreateModal';
import { useSocket } from '../hooks/useSocket';
import { StoryObject, StoryObjectType, Relationship } from '../types';
import {
  UserIcon,
  MapPinIcon,
  CubeIcon,
  ArrowLeftIcon,
  PlusIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';

type ObjectTab = 'characters' | 'locations' | 'props' | 'relationships';

const ObjectManager = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { socket, isConnected } = useSocket();
  
  const [activeTab, setActiveTab] = useState<ObjectTab>('characters');
  const [objects, setObjects] = useState<{
    characters: StoryObject[];
    locations: StoryObject[];
    props: StoryObject[];
  }>({
    characters: [],
    locations: [],
    props: [],
  });
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [selectedObjectId, setSelectedObjectId] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Get the currently selected object based on ID and active tab
  const getSelectedObject = () => {
    if (!selectedObjectId) return null;
    return objects[activeTab === 'relationships' ? 'characters' : activeTab].find(
      obj => obj.id === selectedObjectId
    ) || null;
  };
  
  // Load all objects for the current project
  useEffect(() => {
    const loadObjectData = async () => {
      if (!projectId) return;
      
      try {
        setIsLoading(true);
        
        // Load all objects and relationships in parallel
        const [
          charactersResponse, 
          locationsResponse, 
          propsResponse,
          relationshipsResponse
        ] = await Promise.all([
          api.get(`/api/projects/${projectId}/objects?type=character`),
          api.get(`/api/projects/${projectId}/objects?type=location`),
          api.get(`/api/projects/${projectId}/objects?type=prop`),
          api.get(`/api/projects/${projectId}/relationships`)
        ]);
        
        setObjects({
          characters: charactersResponse.data,
          locations: locationsResponse.data,
          props: propsResponse.data
        });
        
        setRelationships(relationshipsResponse.data);
        setError('');
      } catch (err) {
        console.error('Failed to load object data', err);
        setError('Failed to load story objects. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadObjectData();
  }, [projectId]);
  
  // Setup real-time socket for collaborative editing
  useEffect(() => {
    if (!socket || !isConnected || !projectId) return;
    
    // Join project room
    socket.emit('join_project', { projectId });
    
    // Listen for object updates
    socket.on('object_updated', (updatedObject: StoryObject) => {
      setObjects(prev => {
        const objectType = updatedObject.objectType as 'characters' | 'locations' | 'props';
        return {
          ...prev,
          [objectType]: prev[objectType].map(obj =>
            obj.id === updatedObject.id ? updatedObject : obj
          )
        };
      });
    });
    
    // Listen for new objects
    socket.on('object_created', (newObject: StoryObject) => {
      setObjects(prev => {
        const objectType = newObject.objectType as 'characters' | 'locations' | 'props';
        return {
          ...prev,
          [objectType]: [...prev[objectType], newObject]
        };
      });
    });
    
    // Listen for deleted objects
    socket.on('object_deleted', (deletedObject: { id: string, objectType: string }) => {
      setObjects(prev => {
        const objectType = deletedObject.objectType as 'characters' | 'locations' | 'props';
        return {
          ...prev,
          [objectType]: prev[objectType].filter(obj => obj.id !== deletedObject.id)
        };
      });
      
      // Deselect if the deleted object was selected
      if (selectedObjectId === deletedObject.id) {
        setSelectedObjectId(null);
      }
    });
    
    // Listen for relationship updates
    socket.on('relationship_updated', (updatedRelationships: Relationship[]) => {
      setRelationships(updatedRelationships);
    });
    
    return () => {
      // Leave project room on unmount
      socket.emit('leave_project', { projectId });
      socket.off('object_updated');
      socket.off('object_created');
      socket.off('object_deleted');
      socket.off('relationship_updated');
    };
  }, [socket, isConnected, projectId, selectedObjectId]);
  
  // Handle creating a new object
  const handleCreateObject = async (objectData: Partial<StoryObject>) => {
    if (!projectId) return;
    
    try {
      const response = await api.post(`/api/projects/${projectId}/objects`, objectData);
      const newObject = response.data;
      
      setObjects(prev => {
        const objectType = newObject.objectType as 'characters' | 'locations' | 'props';
        return {
          ...prev,
          [objectType]: [...prev[objectType], newObject]
        };
      });
      
      setSelectedObjectId(newObject.id);
      setActiveTab(newObject.objectType === 'character' ? 'characters' : 
                   newObject.objectType === 'location' ? 'locations' : 'props');
      
      return newObject;
    } catch (err) {
      console.error('Failed to create object', err);
      throw new Error('Failed to create object. Please try again.');
    }
  };
  
  // Handle updating an existing object
  const handleUpdateObject = async (id: string, updates: Partial<StoryObject>) => {
    if (!projectId) return;
    
    try {
      const response = await api.put(`/api/projects/${projectId}/objects/${id}`, updates);
      const updatedObject = response.data;
      
      setObjects(prev => {
        const objectType = updatedObject.objectType as 'characters' | 'locations' | 'props';
        return {
          ...prev,
          [objectType]: prev[objectType].map(obj =>
            obj.id === id ? updatedObject : obj
          )
        };
      });
      
      return updatedObject;
    } catch (err) {
      console.error('Failed to update object', err);
      throw new Error('Failed to update object. Please try again.');
    }
  };
  
  // Handle deleting an object
  const handleDeleteObject = async (id: string, objectType: StoryObjectType) => {
    if (!projectId) return;
    
    try {
      await api.delete(`/api/projects/${projectId}/objects/${id}`);
      
      setObjects(prev => {
        const type = objectType === 'character' ? 'characters' : 
                   objectType === 'location' ? 'locations' : 'props';
        return {
          ...prev,
          [type]: prev[type].filter(obj => obj.id !== id)
        };
      });
      
      // Deselect if the deleted object was selected
      if (selectedObjectId === id) {
        setSelectedObjectId(null);
      }
    } catch (err) {
      console.error('Failed to delete object', err);
      throw new Error('Failed to delete object. Please try again.');
    }
  };
  
  // Handle updating relationships
  const handleUpdateRelationships = async (
    sourceId: string, 
    targetId: string, 
    relationshipType: string,
    description: string
  ) => {
    if (!projectId) return;
    
    try {
      const response = await api.post(`/api/projects/${projectId}/relationships`, {
        sourceId,
        targetId,
        relationshipType,
        description
      });
      
      setRelationships(response.data);
    } catch (err) {
      console.error('Failed to update relationship', err);
      throw new Error('Failed to update relationship. Please try again.');
    }
  };
  
  // Loading state
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate(`/projects/${projectId}`)}
          >
            <ArrowLeftIcon className="h-5 w-5 mr-1" />
            Back to Project
          </Button>
          <h1 className="text-2xl font-bold text-gray-900 ml-4">Story Objects</h1>
        </div>
        
        <Button
          onClick={() => setIsCreateModalOpen(true)}
        >
          <PlusIcon className="h-5 w-5 mr-1" />
          Create Object
        </Button>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px space-x-8">
          <button
            className={`${
              activeTab === 'characters'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
            onClick={() => {
              setActiveTab('characters');
              setSelectedObjectId(null);
            }}
          >
            <UserIcon className="h-5 w-5 mr-2" />
            Characters ({objects.characters.length})
          </button>
          
          <button
            className={`${
              activeTab === 'locations'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
            onClick={() => {
              setActiveTab('locations');
              setSelectedObjectId(null);
            }}
          >
            <MapPinIcon className="h-5 w-5 mr-2" />
            Locations ({objects.locations.length})
          </button>
          
          <button
            className={`${
              activeTab === 'props'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
            onClick={() => {
              setActiveTab('props');
              setSelectedObjectId(null);
            }}
          >
            <CubeIcon className="h-5 w-5 mr-2" />
            Props ({objects.props.length})
          </button>
          
          <button
            className={`${
              activeTab === 'relationships'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
            onClick={() => {
              setActiveTab('relationships');
              setSelectedObjectId(null);
            }}
          >
            <ChartBarIcon className="h-5 w-5 mr-2" />
            Relationships ({relationships.length})
          </button>
        </nav>
      </div>
      
      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Object list sidebar */}
        <div className="lg:col-span-1">
          {activeTab !== 'relationships' ? (
            <ObjectList 
              objects={objects[activeTab]}
              selectedId={selectedObjectId}
              onSelect={id => setSelectedObjectId(id)}
            />
          ) : (
            <div className="card h-full">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Character Relationships
              </h3>
              <p className="text-sm text-gray-500">
                Select a character to view and manage their relationships with other story objects.
              </p>
              <div className="mt-4">
                <ObjectList 
                  objects={objects.characters}
                  selectedId={selectedObjectId}
                  onSelect={id => setSelectedObjectId(id)}
                />
              </div>
            </div>
          )}
        </div>
        
        {/* Object details or relationship graph */}
        <div className="lg:col-span-2">
          {activeTab === 'relationships' ? (
            selectedObjectId ? (
              <RelationshipGraph
                character={objects.characters.find(char => char.id === selectedObjectId) || null}
                allObjects={objects}
                relationships={relationships.filter(
                  rel => rel.sourceId === selectedObjectId || rel.targetId === selectedObjectId
                )}
                onUpdateRelationship={handleUpdateRelationships}
              />
            ) : (
              <div className="card flex items-center justify-center h-full">
                <p className="text-gray-500">
                  Select a character to view their relationships
                </p>
              </div>
            )
          ) : (
            selectedObjectId ? (
              <ObjectDetail
                object={getSelectedObject()}
                onUpdate={(updates) => handleUpdateObject(selectedObjectId, updates)}
                onDelete={() => {
                  const obj = getSelectedObject();
                  if (obj) {
                    handleDeleteObject(obj.id, obj.objectType);
                  }
                }}
              />
            ) : (
              <div className="card flex items-center justify-center h-full">
                <p className="text-gray-500">
                  Select a {activeTab.slice(0, -1)} to view details or create a new one
                </p>
              </div>
            )
          )}
        </div>
      </div>
      
      {/* Create object modal */}
      <ObjectCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreate={handleCreateObject}
        defaultType={
          activeTab === 'characters' 
            ? 'character' 
            : activeTab === 'locations' 
              ? 'location' 
              : 'prop'
        }
      />
    </div>
  );
};

export default ObjectManager;
