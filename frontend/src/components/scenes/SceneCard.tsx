// File: src/components/scenes/SceneCard.tsx
import { Scene } from '../../types';
import {
  UserIcon,
  MapPinIcon,
  CubeIcon,
  Bars2Icon, // Replacement for MenuAlt2Icon
  ChatBubbleBottomCenterTextIcon, // Replacement for ChatAlt2Icon
  CheckBadgeIcon, // Replacement for BadgeCheckIcon
  ExclamationCircleIcon // Replacement for ExclamationIcon
} from '@heroicons/react/24/outline';

type SceneCardProps = {
  scene: Scene;
  onClick: () => void;
};

const SceneCard = ({ scene, onClick }: SceneCardProps) => {
  // Convert emotional intensity to visual indicator
  const getEmotionalIntensity = () => {
    const colors = [
      'bg-blue-100 text-blue-800',    // 1-2 - Calm
      'bg-green-100 text-green-800',  // 3-4 - Light
      'bg-yellow-100 text-yellow-800', // 5-6 - Medium
      'bg-orange-100 text-orange-800', // 7-8 - Intense
      'bg-red-100 text-red-800'        // 9-10 - Extreme
    ];
    
    // Scale the intensity (1-10) to an index (0-4)
    const index = Math.min(Math.floor((scene.emotionalIntensity - 1) / 2), 4);
    return colors[index];
  };
  
  // Get first 150 characters of content for preview
  const getContentPreview = () => {
    if (!scene.content) return '';
    
    // Strip HTML tags for plain text preview
    const plainText = scene.content.replace(/<[^>]*>?/gm, '');
    return plainText.length > 150 
      ? `${plainText.substring(0, 150)}...` 
      : plainText;
  };
  
  // Count objects in scene
  const objectCount = (scene.characters?.length || 0) + 
                      (scene.locations?.length || 0) + 
                      (scene.props?.length || 0);
  
  return (
    <div 
      className="bg-white rounded-md shadow-sm border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all cursor-pointer overflow-hidden"
      onClick={onClick}
    >
      {/* Scene header */}
      <div className="px-4 py-3 border-b border-gray-100">
        <div className="flex justify-between items-start">
          <h3 className="text-sm font-medium text-gray-900 line-clamp-1">{scene.title}</h3>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            #{scene.order}
          </span>
        </div>
      </div>
      
      {/* Scene content preview */}
      <div className="px-4 py-2">
        <p className="text-xs text-gray-500 line-clamp-3">
          {getContentPreview() || 'No content yet...'}
        </p>
      </div>
      
      {/* Scene metadata */}
      <div className="px-4 py-2 bg-gray-50 flex justify-between items-center text-xs text-gray-500">
        <div className="flex items-center space-x-3">
          {/* Emotional intensity */}
          <span className={`px-2 py-0.5 rounded-full ${getEmotionalIntensity()}`}>
            {scene.emotionalIntensity}/10
          </span>
          
          {/* Object count */}
          <div className="flex items-center">
            <Bars2Icon className="h-3.5 w-3.5 mr-1" />
            <span>{objectCount} objects</span>
          </div>
        </div>
        
        {/* AI Analysis indicator */}
        {scene.hasAnalysis ? (
          <CheckBadgeIcon className="h-4 w-4 text-green-500" title="Has AI analysis" />
        ) : (
          <ExclamationCircleIcon className="h-4 w-4 text-gray-400" title="No AI analysis" />
        )}
      </div>
      
      {/* Object icons */}
      {objectCount > 0 && (
        <div className="px-4 py-2 border-t border-gray-100 flex items-center space-x-4">
          {scene.characters && scene.characters.length > 0 && (
            <div className="flex items-center text-xs text-gray-500">
              <UserIcon className="h-3.5 w-3.5 mr-1 text-indigo-400" />
              <span>{scene.characters.length}</span>
            </div>
          )}
          
          {scene.locations && scene.locations.length > 0 && (
            <div className="flex items-center text-xs text-gray-500">
              <MapPinIcon className="h-3.5 w-3.5 mr-1 text-green-400" />
              <span>{scene.locations.length}</span>
            </div>
          )}
          
          {scene.props && scene.props.length > 0 && (
            <div className="flex items-center text-xs text-gray-500">
              <CubeIcon className="h-3.5 w-3.5 mr-1 text-amber-400" />
              <span>{scene.props.length}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SceneCard;