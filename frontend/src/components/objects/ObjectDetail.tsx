// File: src/components/objects/ObjectDetail.tsx
import { useState, useEffect } from 'react';
import { StoryObject } from '../../types';
import Button from '../ui/Button';
import { TrashIcon, SaveIcon } from '@heroicons/react/outline';
import { UserIcon, MapPinIcon, CubeIcon } from '@heroicons/react/24/outline';

type ObjectDetailProps = {
  object: StoryObject | null;
  onUpdate: (updates: Partial<StoryObject>) => Promise<StoryObject>;
  onDelete: () => Promise<void>;
};

// Define specific fields for each object type
const characterFields = [
  { id: 'age', label: 'Age', type: 'number' },
  { id: 'role', label: 'Role in Story', type: 'text' },
  { id: 'motivation', label: 'Motivation', type: 'textarea' },
  { id: 'background', label: 'Background', type: 'textarea' },
  { id: 'personalityTraits', label: 'Personality Traits', type: 'text' }
];

const locationFields = [
  { id: 'address', label: 'Address/Position', type: 'text' },
  { id: 'ambiance', label: 'Ambiance/Mood', type: 'text' },
  { id: 'description', label: 'Description', type: 'textarea' },
  { id: 'significance', label: 'Significance in Story', type: 'textarea' }
];

const propFields = [
  { id: 'appearance', label: 'Appearance', type: 'text' },
  { id: 'significance', label: 'Significance', type: 'textarea' },
  { id: 'history', label: 'History', type: 'textarea' }
];

const ObjectDetail = ({ object, onUpdate, onDelete }: ObjectDetailProps) => {
  const [formData, setFormData] = useState<Partial<StoryObject>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  // Reset form when object changes
  useEffect(() => {
    if (object) {
      setFormData({...object});
      setHasUnsavedChanges(false);
    }
  }, [object]);
  
  // Early return if no object selected
  if (!object) {
    return (
      <div className="card h-full flex items-center justify-center">
        <p className="text-gray-500">Select an object to view details</p>
      </div>
    );
  }
  
  // Get appropriate icon based on object type
  const getObjectIcon = () => {
    switch(object.objectType) {
      case 'character':
        return <UserIcon className="h-6 w-6 text-indigo-500" />;
      case 'location':
        return <MapPinIcon className="h-6 w-6 text-green-500" />;
      case 'prop':
        return <CubeIcon className="h-6 w-6 text-amber-500" />;
      default:
        return null;
    }
  };
  
  // Get appropriate fields based on object type
  const getTypeSpecificFields = () => {
    switch(object.objectType) {
      case 'character':
        return characterFields;
      case 'location':
        return locationFields;
      case 'prop':
        return propFields;
      default:
        return [];
    }
  };
  
  const handleInputChange = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }));
    setHasUnsavedChanges(true);
  };
  
  const handleSave = async () => {
    try {
      setIsSaving(true);
      await onUpdate(formData);
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Failed to save object', error);
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete this ${object.objectType}?`)) {
      try {
        setIsDeleting(true);
        await onDelete();
      } catch (error) {
        console.error('Failed to delete object', error);
      } finally {
        setIsDeleting(false);
      }
    }
  };
  
  return (
    <div className="card h-full overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          {getObjectIcon()}
          <h2 className="text-xl font-bold text-gray-900 ml-2">
            {object.objectType.charAt(0).toUpperCase() + object.objectType.slice(1)} Details
          </h2>
        </div>
        
        <div className="flex space-x-2">
          <Button 
            variant="primary"
            onClick={handleSave}
            disabled={!hasUnsavedChanges}
            isLoading={isSaving}
          >
            <SaveIcon className="h-5 w-5 mr-1" />
            Save
          </Button>
          
          <Button
            variant="danger"
            onClick={handleDelete}
            isLoading={isDeleting}
          >
            <TrashIcon className="h-5 w-5 mr-1" />
            Delete
          </Button>
        </div>
      </div>
      
      <div className="space-y-6">
        {/* Common fields */}
        <div className="grid grid-cols-1 gap-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <input
              id="name"
              type="text"
              value={formData.name || ''}
              onChange={(e) => handleInputChange('name', e.target.value)}
              className="input-standard"
              placeholder={`Enter ${object.objectType} name`}
            />
          </div>
          
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Short Description
            </label>
            <input
              id="description"
              type="text"
              value={formData.description || ''}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="input-standard"
              placeholder="Brief description"
            />
          </div>
          
          <div>
            <label htmlFor="imageUrl" className="block text-sm font-medium text-gray-700 mb-1">
              Image URL (optional)
            </label>
            <input
              id="imageUrl"
              type="text"
              value={formData.imageUrl || ''}
              onChange={(e) => handleInputChange('imageUrl', e.target.value)}
              className="input-standard"
              placeholder="https://example.com/image.jpg"
            />
            {formData.imageUrl && (
              <div className="mt-2">
                <img 
                  src={formData.imageUrl} 
                  alt={formData.name} 
                  className="h-32 w-32 object-cover rounded-md border border-gray-300"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://via.placeholder.com/150?text=Image+Error';
                  }}
                />
              </div>
            )}
          </div>
        </div>
        
        {/* Type-specific fields */}
        <div className="mt-6 border-t border-gray-200 pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {object.objectType.charAt(0).toUpperCase() + object.objectType.slice(1)} Specific Details
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {getTypeSpecificFields().map((field) => (
              <div key={field.id}>
                <label 
                  htmlFor={field.id}
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  {field.label}
                </label>
                
                {field.type === 'textarea' ? (
                  <textarea
                    id={field.id}
                    value={(formData as any)[field.id] || ''}
                    onChange={(e) => handleInputChange(field.id, e.target.value)}
                    className="input-standard min-h-[100px]"
                    placeholder={`Enter ${field.label.toLowerCase()}`}
                  />
                ) : (
                  <input
                    id={field.id}
                    type={field.type}
                    value={(formData as any)[field.id] || (field.type === 'number' ? 0 : '')}
                    onChange={(e) => handleInputChange(
                      field.id, 
                      field.type === 'number' ? parseInt(e.target.value) : e.target.value
                    )}
                    className="input-standard"
                    placeholder={`Enter ${field.label.toLowerCase()}`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
        
        {/* Metadata */}
        <div className="mt-6 border-t border-gray-200 pt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500">Created</p>
              <p className="text-sm">{new Date(object.createdAt).toLocaleDateString()}</p>
            </div>
            
            {object.updatedAt && (
              <div>
                <p className="text-xs text-gray-500">Last Updated</p>
                <p className="text-sm">{new Date(object.updatedAt).toLocaleDateString()}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ObjectDetail;
