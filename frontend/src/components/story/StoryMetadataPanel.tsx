// src/components/story/StoryMetadataPanel.tsx
import React, { useState } from 'react';
import { PencilIcon, CheckIcon, XIcon } from '@heroicons/react/24/outline';

interface StoryMetadataProps {
  metadata: {
    genre: string;
    theme: string;
    targetAudience: string;
    tone: string;
    uniqueElements: string[];
    keySymbols: string[];
  };
  onUpdate: (metadata: any) => void;
}

const StoryMetadataPanel: React.FC<StoryMetadataProps> = ({ metadata, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedMetadata, setEditedMetadata] = useState(metadata);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEditedMetadata(prev => ({ ...prev, [name]: value }));
  };
  
  const handleArrayInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>, field: 'uniqueElements' | 'keySymbols') => {
    const values = e.target.value.split(',').map(item => item.trim()).filter(Boolean);
    setEditedMetadata(prev => ({ ...prev, [field]: values }));
  };
  
  const handleSave = () => {
    onUpdate(editedMetadata);
    setIsEditing(false);
  };
  
  const handleCancel = () => {
    setEditedMetadata(metadata);
    setIsEditing(false);
  };
  
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-medium text-gray-900">Story Metadata</h3>
        {isEditing ? (
          <div className="flex space-x-1">
            <button
              onClick={handleSave}
              className="p-1 text-green-600 hover:text-green-800"
              title="Save"
            >
              <CheckIcon className="h-4 w-4" />
            </button>
            <button
              onClick={handleCancel}
              className="p-1 text-red-600 hover:text-red-800"
              title="Cancel"
            >
              <XIcon className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="p-1 text-gray-500 hover:text-indigo-600"
            title="Edit metadata"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
        )}
      </div>
      
      <div className="space-y-3">
        {/* Genre */}
        <div>
          <div className="text-xs font-medium text-gray-500 mb-1">Genre</div>
          {isEditing ? (
            <input
              type="text"
              name="genre"
              value={editedMetadata.genre}
              onChange={handleInputChange}
              className="w-full p-1 text-sm border border-gray-300 rounded"
            />
          ) : (
            <div className="text-sm">{metadata.genre || 'Not specified'}</div>
          )}
        </div>
        
        {/* Theme */}
        <div>
          <div className="text-xs font-medium text-gray-500 mb-1">Theme</div>
          {isEditing ? (
            <input
              type="text"
              name="theme"
              value={editedMetadata.theme}
              onChange={handleInputChange}
              className="w-full p-1 text-sm border border-gray-300 rounded"
            />
          ) : (
            <div className="text-sm">{metadata.theme || 'Not specified'}</div>
          )}
        </div>
        
        {/* Target Audience */}
        <div>
          <div className="text-xs font-medium text-gray-500 mb-1">Target Audience</div>
          {isEditing ? (
            <input
              type="text"
              name="targetAudience"
              value={editedMetadata.targetAudience}
              onChange={handleInputChange}
              className="w-full p-1 text-sm border border-gray-300 rounded"
            />
          ) : (
            <div className="text-sm">{metadata.targetAudience || 'Not specified'}</div>
          )}
        </div>
        
        {/* Tone */}
        <div>
          <div className="text-xs font-medium text-gray-500 mb-1">Tone</div>
          {isEditing ? (
            <input
              type="text"
              name="tone"
              value={editedMetadata.tone}
              onChange={handleInputChange}
              className="w-full p-1 text-sm border border-gray-300 rounded"
            />
          ) : (
            <div className="text-sm">{metadata.tone || 'Not specified'}</div>
          )}
        </div>
        
        {/* Unique Elements */}
        <div>
          <div className="text-xs font-medium text-gray-500 mb-1">Unique Elements</div>
          {isEditing ? (
            <textarea
              name="uniqueElements"
              value={editedMetadata.uniqueElements.join(', ')}
              onChange={(e) => handleArrayInputChange(e, 'uniqueElements')}
              className="w-full p-1 text-sm border border-gray-300 rounded"
              rows={2}
              placeholder="Comma-separated list"
            />
          ) : (
            <div className="text-sm">
              {metadata.uniqueElements && metadata.uniqueElements.length > 0
                ? metadata.uniqueElements.join(', ')
                : 'None'}
            </div>
          )}
        </div>
        
        {/* Key Symbols */}
        <div>
          <div className="text-xs font-medium text-gray-500 mb-1">Key Symbols</div>
          {isEditing ? (
            <textarea
              name="keySymbols"
              value={editedMetadata.keySymbols.join(', ')}
              onChange={(e) => handleArrayInputChange(e, 'keySymbols')}
              className="w-full p-1 text-sm border border-gray-300 rounded"
              rows={2}
              placeholder="Comma-separated list"
            />
          ) : (
            <div className="text-sm">
              {metadata.keySymbols && metadata.keySymbols.length > 0
                ? metadata.keySymbols.join(', ')
                : 'None'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StoryMetadataPanel;