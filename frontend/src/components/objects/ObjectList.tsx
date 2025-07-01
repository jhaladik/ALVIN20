// File: src/components/objects/ObjectList.tsx
import { useState } from 'react';
import { StoryObject } from '../../types';
import { SearchIcon } from '@heroicons/react/outline';
import { UserIcon, MapPinIcon, CubeIcon } from '@heroicons/react/24/outline';

type ObjectListProps = {
  objects: StoryObject[];
  selectedId: string | null;
  onSelect: (id: string) => void;
};

const ObjectList = ({ objects, selectedId, onSelect }: ObjectListProps) => {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filter objects based on search query
  const filteredObjects = searchQuery 
    ? objects.filter(obj => 
        obj.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        obj.description?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : objects;
    
  // Get appropriate icon based on object type
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
  
  return (
    <div className="card h-full">
      {/* Search input */}
      <div className="relative mb-4">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <SearchIcon className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="input-standard pl-10"
          placeholder="Search objects..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      
      {/* Object list */}
      <div className="space-y-2 max-h-[calc(100vh-300px)] overflow-y-auto pr-2">
        {filteredObjects.length > 0 ? (
          filteredObjects.map((obj) => (
            <div
              key={obj.id}
              className={`flex items-center p-3 rounded-md cursor-pointer transition-all ${
                selectedId === obj.id
                  ? 'bg-indigo-50 border-l-4 border-indigo-500'
                  : 'hover:bg-gray-50 border-l-4 border-transparent'
              }`}
              onClick={() => onSelect(obj.id)}
            >
              <div className="mr-3">
                {getObjectIcon(obj.objectType)}
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {obj.name}
                </p>
                {obj.description && (
                  <p className="text-xs text-gray-500 truncate">
                    {obj.description}
                  </p>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <p className="text-sm text-gray-500">No objects found</p>
            {searchQuery && (
              <button
                className="mt-2 text-xs text-indigo-600 hover:text-indigo-500"
                onClick={() => setSearchQuery('')}
              >
                Clear search
              </button>
            )}
          </div>
        )}
      </div>
      
      {/* Show count at bottom */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Showing {filteredObjects.length} of {objects.length} objects
        </p>
      </div>
    </div>
  );
};

export default ObjectList;
