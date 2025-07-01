// src/components/ui/Avatar.tsx
import React from 'react';

type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
type PresenceIndicator = 'online' | 'offline' | 'away' | 'busy' | 'typing';

interface AvatarProps {
  username: string;
  src?: string;
  size?: AvatarSize;
  className?: string;
  indicator?: PresenceIndicator;
}

const Avatar: React.FC<AvatarProps> = ({
  username,
  src,
  size = 'md',
  className = '',
  indicator,
}) => {
  // Get initials from username
  const getInitials = () => {
    if (!username) return '';
    
    const parts = username.split(/[ -]/);
    if (parts.length > 1) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    
    return username.substring(0, 2).toUpperCase();
  };
  
  // Get avatar size class
  const getSizeClass = () => {
    switch (size) {
      case 'xs':
        return 'h-6 w-6 text-xs';
      case 'sm':
        return 'h-8 w-8 text-sm';
      case 'md':
        return 'h-10 w-10 text-base';
      case 'lg':
        return 'h-12 w-12 text-lg';
      case 'xl':
        return 'h-16 w-16 text-xl';
      default:
        return 'h-10 w-10 text-base';
    }
  };
  
  // Get indicator size and position
  const getIndicatorClass = () => {
    const indicatorSizeClass = size === 'xs' || size === 'sm' 
      ? 'h-2.5 w-2.5 border-1' 
      : 'h-3.5 w-3.5 border-2';
    
    return `absolute bottom-0 right-0 ${indicatorSizeClass} border-white rounded-full`;
  };
  
  // Get indicator color
  const getIndicatorColor = () => {
    switch (indicator) {
      case 'online':
        return 'bg-green-500';
      case 'offline':
        return 'bg-gray-400';
      case 'away':
        return 'bg-yellow-500';
      case 'busy':
        return 'bg-red-500';
      case 'typing':
        return 'bg-indigo-500';
      default:
        return 'bg-green-500';
    }
  };
  
  // Get animation class for typing
  const getAnimationClass = () => {
    return indicator === 'typing' ? 'animate-pulse' : '';
  };

  return (
    <div className={`relative inline-flex ${className}`}>
      {src ? (
        <img
          src={src}
          alt={username}
          className={`${getSizeClass()} rounded-full object-cover`}
        />
      ) : (
        <div
          className={`${getSizeClass()} rounded-full bg-indigo-100 text-indigo-800 flex items-center justify-center font-medium`}
        >
          {getInitials()}
        </div>
      )}
      
      {indicator && (
        <span
          className={`${getIndicatorClass()} ${getIndicatorColor()} ${getAnimationClass()}`}
        ></span>
      )}
    </div>
  );
};

export default Avatar;
