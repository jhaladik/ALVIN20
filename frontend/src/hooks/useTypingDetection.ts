// src/hooks/useTypingDetection.ts
import { useState, useEffect, useRef } from 'react';
import { useSocketContext } from '../context/SocketContext';

interface UseTypingDetectionProps {
  roomType: 'project' | 'scene';
  roomId: string;
  isEnabled?: boolean;
}

/**
 * Hook to detect typing activity and notify other users through Socket.IO
 */
export function useTypingDetection({
  roomType,
  roomId,
  isEnabled = true,
}: UseTypingDetectionProps) {
  const { sendTypingStatus } = useSocketContext();
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef<number | null>(null);
  
  // Clear typing timeout
  const clearTypingTimeout = () => {
    if (typingTimeoutRef.current) {
      window.clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = null;
    }
  };
  
  // Send typing status update
  const updateTypingStatus = (typing: boolean) => {
    if (!isEnabled) return;
    
    setIsTyping(typing);
    sendTypingStatus(roomType, roomId, typing);
    
    // Clear any existing timeout
    clearTypingTimeout();
    
    // If typing, set a timeout to automatically clear the typing status
    if (typing) {
      typingTimeoutRef.current = window.setTimeout(() => {
        setIsTyping(false);
        sendTypingStatus(roomType, roomId, false);
      }, 3000); // Clear typing status after 3 seconds of inactivity
    }
  };
  
  // Handle input changes to detect typing
  const handleInputChange = () => {
    if (!isTyping) {
      updateTypingStatus(true);
    } else {
      // Reset the timeout on each keystroke
      clearTypingTimeout();
      typingTimeoutRef.current = window.setTimeout(() => {
        setIsTyping(false);
        sendTypingStatus(roomType, roomId, false);
      }, 3000);
    }
  };
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      clearTypingTimeout();
      if (isTyping) {
        sendTypingStatus(roomType, roomId, false);
      }
    };
  }, [roomType, roomId, isTyping, sendTypingStatus]);
  
  return {
    isTyping,
    handleInputChange,
  };
}

export default useTypingDetection;
