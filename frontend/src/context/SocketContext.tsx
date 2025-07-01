// src/context/SocketContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from '../hooks/useAuth';

interface SocketContextProps {
  socket: Socket | null;
  isConnected: boolean;
  activeUsers: ActiveUser[];
  joinRoom: (roomType: string, roomId: string) => void;
  leaveRoom: (roomType: string, roomId: string) => void;
  sendTypingStatus: (roomType: string, roomId: string, isTyping: boolean) => void;
  typingUsers: TypingUser[];
}

export interface ActiveUser {
  id: string;
  username: string;
  avatar?: string;
  roomId: string;
  joinedAt: string;
  lastActivity: string;
}

export interface TypingUser {
  id: string;
  username: string;
  roomId: string;
  timestamp: string;
}

export const SocketContext = createContext<SocketContextProps>({
  socket: null,
  isConnected: false,
  activeUsers: [],
  joinRoom: () => {},
  leaveRoom: () => {},
  sendTypingStatus: () => {},
  typingUsers: [],
});

export const useSocketContext = () => useContext(SocketContext);

export const SocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [activeUsers, setActiveUsers] = useState<ActiveUser[]>([]);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);

  // Initialize socket connection when user is authenticated
  useEffect(() => {
    if (!isAuthenticated || !user) {
      if (socket) {
        socket.disconnect();
        setSocket(null);
        setIsConnected(false);
      }
      return;
    }

    // Initialize socket connection
    const socketInstance = io(import.meta.env.VITE_API_URL || 'http://localhost:5000', {
      withCredentials: true,
      transports: ['websocket'],
      auth: {
        token: user.id,
      },
    });

    setSocket(socketInstance);

    // Socket event listeners
    socketInstance.on('connect', () => {
      console.log('Socket connected');
      setIsConnected(true);
    });

    socketInstance.on('disconnect', () => {
      console.log('Socket disconnected');
      setIsConnected(false);
    });

    socketInstance.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      setIsConnected(false);
    });

    // Handle presence updates
    socketInstance.on('presence_update', (users: ActiveUser[]) => {
      setActiveUsers(users);
    });

    // Handle typing status updates
    socketInstance.on('typing_status', (typingData: TypingUser) => {
      setTypingUsers((prevTyping) => {
        // Remove any existing typing status for this user
        const filtered = prevTyping.filter(user => user.id !== typingData.id);
        
        // If user is typing, add them to the list
        if (typingData.timestamp) {
          return [...filtered, typingData];
        }
        
        // Otherwise, just return the filtered list (user stopped typing)
        return filtered;
      });
    });

    // Cleanup on unmount
    return () => {
      socketInstance.disconnect();
      setSocket(null);
      setIsConnected(false);
    };
  }, [isAuthenticated, user]);

  // Remove users from typing list after a timeout
  useEffect(() => {
    if (typingUsers.length === 0) return;

    const interval = setInterval(() => {
      const now = Date.now();
      setTypingUsers(prevTyping => 
        prevTyping.filter(user => {
          // Remove typing status older than 3 seconds
          const timestamp = new Date(user.timestamp).getTime();
          return now - timestamp < 3000;
        })
      );
    }, 1000);

    return () => clearInterval(interval);
  }, [typingUsers]);

  // Join a room (project, scene, etc.)
  const joinRoom = (roomType: string, roomId: string) => {
    if (!socket || !isConnected) return;
    
    socket.emit('join_room', { roomType, roomId });
  };

  // Leave a room
  const leaveRoom = (roomType: string, roomId: string) => {
    if (!socket || !isConnected) return;
    
    socket.emit('leave_room', { roomType, roomId });
  };

  // Send typing status
  const sendTypingStatus = (roomType: string, roomId: string, isTyping: boolean) => {
    if (!socket || !isConnected) return;
    
    socket.emit('typing', {
      roomType,
      roomId,
      isTyping,
      timestamp: isTyping ? new Date().toISOString() : '',
    });
  };

  const value = {
    socket,
    isConnected,
    activeUsers,
    joinRoom,
    leaveRoom,
    sendTypingStatus,
    typingUsers,
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};