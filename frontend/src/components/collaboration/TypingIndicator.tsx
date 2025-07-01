// src/components/collaboration/TypingIndicator.tsx
import React from 'react';
import { PencilIcon } from '@heroicons/react/24/outline';
import { useSocketContext } from '../../context/SocketContext';
import { useAuth } from '../../context/AuthContext';

interface TypingIndicatorProps {
  roomType: 'project' | 'scene';
  roomId: string;
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ roomType, roomId }) => {
  const { typingUsers } = useSocketContext();
  const { user } = useAuth();
  
  // Filter typing users for this room, excluding the current user
  const typingUsersInRoom = typingUsers.filter(
    typingUser => typingUser.roomId === roomId && typingUser.id !== user?.id
  );
  
  if (typingUsersInRoom.length === 0) {
    return null;
  }

  // Format the message based on how many users are typing
  const getMessage = () => {
    if (typingUsersInRoom.length === 1) {
      return `${typingUsersInRoom[0].username} is typing...`;
    } else if (typingUsersInRoom.length === 2) {
      return `${typingUsersInRoom[0].username} and ${typingUsersInRoom[1].username} are typing...`;
    } else if (typingUsersInRoom.length === 3) {
      return `${typingUsersInRoom[0].username}, ${typingUsersInRoom[1].username}, and ${typingUsersInRoom[2].username} are typing...`;
    } else {
      return `${typingUsersInRoom.length} people are typing...`;
    }
  };

  return (
    <div className="flex items-center text-xs text-gray-500 animate-pulse">
      <PencilIcon className="h-3 w-3 mr-1" />
      <span>{getMessage()}</span>
    </div>
  );
};

export default TypingIndicator;
