// File: src/components/objects/RelationshipGraph.tsx
import { useState, useEffect } from 'react';
import { StoryObject, Relationship } from '../../types';
import Button from '../ui/Button';
import { 
  UserIcon, 
  MapPinIcon, 
  CubeIcon, 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  HeartIcon,
  XIcon,
  UserGroupIcon,
  LightningBoltIcon,
  ExclamationIcon
} from '@heroicons/react/24/outline';

type RelationshipGraphProps = {
  character: StoryObject | null;
  allObjects: {
    characters: StoryObject[];
    locations: StoryObject[];
    props: StoryObject[];
  };
  relationships: Relationship[];
  onUpdateRelationship: (
    sourceId: string, 
    targetId: string, 
    relationshipType: string,
    description: string
  ) => Promise<void>;
};

// Predefined relationship types
const relationshipTypes = [
  { id: 'family', label: 'Family', icon: <UserGroupIcon className="h-5 w-5" /> },
  { id: 'friend', label: 'Friend', icon: <HeartIcon className="h-5 w-5" /> },
  { id: 'enemy', label: 'Enemy', icon: <XIcon className="h-5 w-5" /> },
  { id: 'ally', label: 'Ally', icon: <UserIcon className="h-5 w-5" /> },
  { id: 'romantic', label: 'Romantic', icon: <HeartIcon className="h-5 w-5 text-red-500" /> },
  { id: 'conflict', label: 'Conflict', icon: <LightningBoltIcon className="h-5 w-5" /> },
  { id: 'professional', label: 'Professional', icon: <UserIcon className="h-5 w-5" /> },
  { id: 'ownership', label: 'Owns', icon: <CubeIcon className="h-5 w-5" /> },
  { id: 'residence', label: 'Lives At', icon: <MapPinIcon className="h-5 w-5" /> },
  { id: 'unknown', label: 'Other', icon: <ExclamationIcon className="h-5 w-5" /> }
];

// Component to manage relationship creation and editing
const RelationshipForm = ({
  sourceId,
  existingRelationship = null,
  onSave,
  onCancel,
  availableObjects,
}: {
  sourceId: string;
  existingRelationship?: Relationship | null;
  onSave: (targetId: string, type: string, description: string) => void;
  onCancel: () => void;
  availableObjects: {
    characters: StoryObject[];
    locations: StoryObject[];
    props: StoryObject[];
  };
}) => {
  const [targetId, setTargetId] = useState(existingRelationship?.targetId || '');
  const [relationType, setRelationType] = useState(existingRelationship?.relationshipType || 'unknown');
  const [description, setDescription] = useState(existingRelationship?.description || '');
  const [objectTypeFilter, setObjectTypeFilter] = useState<'all' | 'characters' | 'locations' | 'props'>('all');
  
  // Get filtered objects based on the selected filter
  const getFilteredObjects = () => {
    if (objectTypeFilter === 'all') {
      return [
        ...availableObjects.characters.filter(obj => obj.id !== sourceId),
        ...availableObjects.locations,
        ...availableObjects.props,
      ];
    }
    
    if (objectTypeFilter === 'characters') {
      return availableObjects.characters.filter(obj => obj.id !== sourceId);
    }
    
    return availableObjects[objectTypeFilter];
  };
  
  // Get object icon based on type
  const getObjectIcon = (type: string) => {
    switch(type) {
      case 'character':
        return <UserIcon className="h-5 w-5 text-indigo-400" />;
      case 'location':
        return <MapPinIcon className="h-5 w-5 text-green-400" />;
      case 'prop':
        return <CubeIcon className="h-5 w-5 text-amber-400" />;
      default:
        return null;
    }
  };
  
  // Get object data by ID
  const getObjectById = (id: string) => {
    return [
      ...availableObjects.characters,
      ...availableObjects.locations,
      ...availableObjects.props,
    ].find(obj => obj.id === id);
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetId || !relationType) return;
    
    onSave(targetId, relationType, description);
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Filter Object Type
        </label>
        <div className="flex space-x-2">
          <button
            type="button"
            className={`px-3 py-1 rounded-md text-sm ${
              objectTypeFilter === 'all' 
                ? 'bg-gray-200 text-gray-800' 
                : 'bg-white border border-gray-300 text-gray-600'
            }`}
            onClick={() => setObjectTypeFilter('all')}
          >
            All
          </button>
          <button
            type="button"
            className={`px-3 py-1 rounded-md text-sm flex items-center ${
              objectTypeFilter === 'characters' 
                ? 'bg-indigo-100 text-indigo-800' 
                : 'bg-white border border-gray-300 text-gray-600'
            }`}
            onClick={() => setObjectTypeFilter('characters')}
          >
            <UserIcon className="h-4 w-4 mr-1" />
            Characters
          </button>
          <button
            type="button"
            className={`px-3 py-1 rounded-md text-sm flex items-center ${
              objectTypeFilter === 'locations' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-white border border-gray-300 text-gray-600'
            }`}
            onClick={() => setObjectTypeFilter('locations')}
          >
            <MapPinIcon className="h-4 w-4 mr-1" />
            Locations
          </button>
          <button
            type="button"
            className={`px-3 py-1 rounded-md text-sm flex items-center ${
              objectTypeFilter === 'props' 
                ? 'bg-amber-100 text-amber-800' 
                : 'bg-white border border-gray-300 text-gray-600'
            }`}
            onClick={() => setObjectTypeFilter('props')}
          >
            <CubeIcon className="h-4 w-4 mr-1" />
            Props
          </button>
        </div>
      </div>
      
      <div>
        <label htmlFor="targetId" className="block text-sm font-medium text-gray-700 mb-1">
          Related To
        </label>
        <select
          id="targetId"
          value={targetId}
          onChange={(e) => setTargetId(e.target.value)}
          className="input-standard"
          required
        >
          <option value="">Select a story object...</option>
          {getFilteredObjects().map((obj) => (
            <option key={obj.id} value={obj.id}>
              {obj.name} ({obj.objectType})
            </option>
          ))}
        </select>
      </div>
      
      <div>
        <label htmlFor="relationType" className="block text-sm font-medium text-gray-700 mb-1">
          Relationship Type
        </label>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          {relationshipTypes.map((type) => (
            <button
              key={type.id}
              type="button"
              className={`
                flex flex-col items-center justify-center p-2 rounded-md text-sm
                ${relationType === type.id 
                  ? 'bg-indigo-50 border-2 border-indigo-500' 
                  : 'bg-white border border-gray-300 hover:bg-gray-50'}
              `}
              onClick={() => setRelationType(type.id)}
            >
              {type.icon}
              <span className="mt-1">{type.label}</span>
            </button>
          ))}
        </div>
      </div>
      
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="input-standard min-h-[80px]"
          placeholder="Describe this relationship..."
        />
      </div>
      
      <div className="flex justify-end space-x-2">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={!targetId || !relationType}
        >
          {existingRelationship ? 'Update' : 'Create'} Relationship
        </Button>
      </div>
    </form>
  );
};

const RelationshipGraph = ({ 
  character, 
  allObjects, 
  relationships, 
  onUpdateRelationship 
}: RelationshipGraphProps) => {
  const [showForm, setShowForm] = useState(false);
  const [editingRelationship, setEditingRelationship] = useState<Relationship | null>(null);
  
  // Reset form when character changes
  useEffect(() => {
    setShowForm(false);
    setEditingRelationship(null);
  }, [character?.id]);
  
  if (!character) {
    return (
      <div className="card h-full flex items-center justify-center">
        <p className="text-gray-500">Select a character to view their relationships</p>
      </div>
    );
  }
  
  // Find an object by ID
  const findObjectById = (id: string): StoryObject | undefined => {
    return [
      ...allObjects.characters,
      ...allObjects.locations,
      ...allObjects.props
    ].find(obj => obj.id === id);
  };
  
  // Get relationship label based on type
  const getRelationshipLabel = (type: string) => {
    return relationshipTypes.find(t => t.id === type)?.label || 'Unknown';
  };
  
  // Get relationship icon based on type
  const getRelationshipIcon = (type: string) => {
    return relationshipTypes.find(t => t.id === type)?.icon || null;
  };
  
  // Save relationship
  const handleSaveRelationship = async (targetId: string, type: string, description: string) => {
    try {
      await onUpdateRelationship(character.id, targetId, type, description);
      setShowForm(false);
      setEditingRelationship(null);
    } catch (error) {
      console.error('Failed to save relationship', error);
    }
  };
  
  // Edit relationship
  const handleEditRelationship = (relationship: Relationship) => {
    setEditingRelationship(relationship);
    setShowForm(true);
  };
  
  // Delete relationship
  const handleDeleteRelationship = async (relationship: Relationship) => {
    if (window.confirm('Are you sure you want to delete this relationship?')) {
      try {
        // Pass empty type to delete the relationship
        await onUpdateRelationship(
          relationship.sourceId, 
          relationship.targetId, 
          '', 
          ''
        );
      } catch (error) {
        console.error('Failed to delete relationship', error);
      }
    }
  };
  
  return (
    <div className="card h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <UserIcon className="h-6 w-6 text-indigo-500" />
          <h2 className="text-xl font-bold text-gray-900 ml-2">
            {character.name}'s Relationships
          </h2>
        </div>
        
        {!showForm && (
          <Button
            onClick={() => {
              setEditingRelationship(null);
              setShowForm(true);
            }}
          >
            <PlusIcon className="h-5 w-5 mr-1" />
            Add Relationship
          </Button>
        )}
      </div>
      
      {showForm ? (
        <RelationshipForm
          sourceId={character.id}
          existingRelationship={editingRelationship}
          onSave={handleSaveRelationship}
          onCancel={() => {
            setShowForm(false);
            setEditingRelationship(null);
          }}
          availableObjects={allObjects}
        />
      ) : (
        <div>
          {relationships.length > 0 ? (
            <div className="space-y-4">
              {relationships.map((relationship) => {
                const relatedObjectId = relationship.sourceId === character.id 
                  ? relationship.targetId 
                  : relationship.sourceId;
                const relatedObject = findObjectById(relatedObjectId);
                
                if (!relatedObject) return null;
                
                return (
                  <div 
                    key={`${relationship.sourceId}-${relationship.targetId}`}
                    className="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex-shrink-0 mr-4">
                      {relatedObject.objectType === 'character' && (
                        <div className="h-12 w-12 rounded-full bg-indigo-100 flex items-center justify-center">
                          <UserIcon className="h-6 w-6 text-indigo-500" />
                        </div>
                      )}
                      {relatedObject.objectType === 'location' && (
                        <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                          <MapPinIcon className="h-6 w-6 text-green-500" />
                        </div>
                      )}
                      {relatedObject.objectType === 'prop' && (
                        <div className="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center">
                          <CubeIcon className="h-6 w-6 text-amber-500" />
                        </div>
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center">
                        <p className="text-sm font-medium text-gray-900">
                          {relatedObject.name}
                        </p>
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {relatedObject.objectType}
                        </span>
                      </div>
                      
                      <div className="mt-1 flex items-center">
                        {getRelationshipIcon(relationship.relationshipType)}
                        <span className="ml-1 text-sm text-gray-500">
                          {getRelationshipLabel(relationship.relationshipType)}
                        </span>
                      </div>
                      
                      {relationship.description && (
                        <p className="mt-1 text-sm text-gray-500">
                          {relationship.description}
                        </p>
                      )}
                    </div>
                    
                    <div className="flex-shrink-0 ml-4 flex space-x-2">
                      <button
                        className="text-gray-400 hover:text-gray-500"
                        onClick={() => handleEditRelationship(relationship)}
                      >
                        <PencilIcon className="h-5 w-5" />
                      </button>
                      <button
                        className="text-gray-400 hover:text-red-500"
                        onClick={() => handleDeleteRelationship(relationship)}
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-500">
                No relationships found for {character.name}.
              </p>
              <p className="text-sm text-gray-400 mt-2">
                Click "Add Relationship" to create connections with other story objects.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RelationshipGraph;
