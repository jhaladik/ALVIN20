// File: src/components/objects/ObjectCreateModal.tsx
import { useState } from 'react';
import { StoryObject, StoryObjectType } from '../../types';
import Button from '../ui/Button';
import { XIcon } from '@heroicons/react/outline';
import { UserIcon, MapPinIcon, CubeIcon } from '@heroicons/react/24/outline';

type ObjectCreateModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (objectData: Partial<StoryObject>) => Promise<StoryObject>;
  defaultType?: StoryObjectType;
};

const ObjectCreateModal = ({ 
  isOpen, 
  onClose, 
  onCreate, 
  defaultType = 'character' 
}: ObjectCreateModalProps) => {
  const [formData, setFormData] = useState<Partial<StoryObject>>({
    name: '',
    description: '',
    objectType: defaultType,
  });
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState('');
  
  // Reset form when modal opens or default type changes
  useState(() => {
    if (isOpen) {
      setFormData({
        name: '',
        description: '',
        objectType: defaultType,
      });
      setError('');
    }
  });
  
  if (!isOpen) return null;
  
  const handleInputChange = (key: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.name) {
      setError('Name is required');
      return;
    }
    
    try {
      setIsCreating(true);
      setError('');
      const newObject = await onCreate(formData);
      onClose();
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to create object. Please try again.');
      }
    } finally {
      setIsCreating(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2 className="text-xl font-bold text-gray-900">
            Create New Story Object
          </h2>
          <button
            type="button"
            className="text-gray-400 hover:text-gray-500"
            onClick={onClose}
          >
            <XIcon className="h-6 w-6" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="px-6 py-4">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
              <div className="flex">
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          {/* Object type selector */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Object Type
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                className={`
                  flex flex-col items-center justify-center p-3 rounded-md
                  ${formData.objectType === 'character' 
                    ? 'bg-indigo-50 border-2 border-indigo-500' 
                    : 'bg-white border border-gray-300 hover:bg-gray-50'}
                `}
                onClick={() => handleInputChange('objectType', 'character')}
              >
                <UserIcon className="h-6 w-6 text-indigo-500 mb-1" />
                <span className="text-sm font-medium">Character</span>
              </button>
              
              <button
                type="button"
                className={`
                  flex flex-col items-center justify-center p-3 rounded-md
                  ${formData.objectType === 'location' 
                    ? 'bg-green-50 border-2 border-green-500' 
                    : 'bg-white border border-gray-300 hover:bg-gray-50'}
                `}
                onClick={() => handleInputChange('objectType', 'location')}
              >
                <MapPinIcon className="h-6 w-6 text-green-500 mb-1" />
                <span className="text-sm font-medium">Location</span>
              </button>
              
              <button
                type="button"
                className={`
                  flex flex-col items-center justify-center p-3 rounded-md
                  ${formData.objectType === 'prop' 
                    ? 'bg-amber-50 border-2 border-amber-500' 
                    : 'bg-white border border-gray-300 hover:bg-gray-50'}
                `}
                onClick={() => handleInputChange('objectType', 'prop')}
              >
                <CubeIcon className="h-6 w-6 text-amber-500 mb-1" />
                <span className="text-sm font-medium">Prop</span>
              </button>
            </div>
          </div>
          
          {/* Name field */}
          <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Name *
            </label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              className="input-standard"
              placeholder={`Enter ${formData.objectType} name`}
              required
            />
          </div>
          
          {/* Description field */}
          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="input-standard min-h-[100px]"
              placeholder={`Brief description of this ${formData.objectType}`}
            />
          </div>
          
          {/* Image URL field */}
          <div className="mb-6">
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
          </div>
          
          {/* Action buttons */}
          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
            >
              Cancel
            </Button>
            
            <Button
              type="submit"
              isLoading={isCreating}
            >
              Create {formData.objectType.charAt(0).toUpperCase() + formData.objectType.slice(1)}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ObjectCreateModal;
