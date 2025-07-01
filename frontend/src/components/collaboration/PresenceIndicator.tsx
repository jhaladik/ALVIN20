// src/components/collaboration/PresenceIndicator.tsx
import React, { useState } from 'react';
import { 
  UsersIcon, 
  PencilIcon, 
  EyeIcon,
  ChatBubbleLeftEllipsisIcon
} from '@heroicons/react/24/outline';
import { useSocketContext } from '../../context/SocketContext';
import Avatar from '../ui/Avatar';
import { format } from 'date-fns';

interface PresenceIndicatorProps {
  roomType: 'project' | 'scene';
  roomId: string;
}

const PresenceIndicator: React.FC<PresenceIndicatorProps> = ({ roomType, roomId }) => {
  const { activeUsers, typingUsers } = useSocketContext();
  const [showDetails, setShowDetails] = useState(false);
  
  // Filter users for this room
  const usersInRoom = activeUsers.filter(user => user.roomId === roomId);
  const typingUsersInRoom = typingUsers.filter(user => user.roomId === roomId);
  
  if (usersInRoom.length === 0) {
    return null;
  }

  // Format relative time
  const formatActivityTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) {
      return 'just now';
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else {
      return format(date, 'h:mm a');
    }
  };

  return (
    <div className="relative">
      {/* Condensed indicator */}
      <button
        className="inline-flex items-center px-2.5 py-1.5 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
        onClick={() => setShowDetails(!showDetails)}
      >
        <UsersIcon className="h-4 w-4 text-gray-600 mr-1" />
        <span className="text-sm text-gray-700">{usersInRoom.length}</span>
        
        {typingUsersInRoom.length > 0 && (
          <span className="ml-1.5 flex items-center text-gray-600">
            <PencilIcon className="h-3 w-3 mr-0.5 animate-pulse" />
          </span>
        )}
      </button>
      
      {/* Detailed popup */}
      {showDetails && (
        <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
          <div className="p-3 border-b border-gray-200">
            <h3 className="text-sm font-medium text-gray-900">
              {usersInRoom.length} {usersInRoom.length === 1 ? 'person' : 'people'} viewing
            </h3>
          </div>
          
          <div className="max-h-60 overflow-y-auto">
            {usersInRoom.map((user) => {
              const isTyping = typingUsersInRoom.some(u => u.id === user.id);
              
              return (
                <div key={user.id} className="p-3 flex items-center justify-between hover:bg-gray-50">
                  <div className="flex items-center">
                    <Avatar 
                      username={user.username}
                      src={user.avatar}
                      size="sm"
                      className="mr-2"
                      indicator={isTyping ? 'typing' : 'online'}
                    />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {user.username}
                      </p>
                      <p className="text-xs text-gray-500">
                        Active {formatActivityTime(user.lastActivity)}
                      </p>
                    </div>
                  </div>
                  
                  {isTyping ? (
                    <PencilIcon className="h-4 w-4 text-indigo-500 animate-pulse" />
                  ) : (
                    <EyeIcon className="h-4 w-4 text-gray-400" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default PresenceIndicator;
