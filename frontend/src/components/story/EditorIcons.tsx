// src/components/story/EditorIcons.tsx
import React from 'react';

interface IconProps {
  className?: string;
}

// Simple implementations of icons - in a real project, you'd use a library like heroicons
export const BoldIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 12H14C16.2091 12 18 10.2091 18 8C18 5.79086 16.2091 4 14 4H6V12ZM6 12H15C17.2091 12 19 13.7909 19 16C19 18.2091 17.2091 20 15 20H6V12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const ItalicIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M19 4H10M14 20H5M15 4L9 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const ListBulletIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M8 6H21M8 12H21M8 18H21M3 6H3.01M3 12H3.01M3 18H3.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const ListOrderedIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 6H21M10 12H21M10 18H21M4 6H5M4 18H5M4 12H5.5M5.5 12C5.5 12 6 12.1716 6 12.5C6 12.8284 5.5 13 5.5 13M5.5 13H5M5.5 13C5.5 13 6 13.1716 6 13.5C6 13.8284 5.5 14 5.5 14H4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const QuoteIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 21C9 21 9 15 9 15V9C9 9 9 3 3 3M15 21C21 21 21 15 21 15V9C21 9 21 3 15 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const LinkIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 13C10.8631 13.3039 11.8037 13.8637 12.5 14.5C13.1963 15.1363 13.6961 16.0869 14 17M9.5 10C8.66019 9.72755 7.66406 9.03325 7 8.5C5.5 7.5 4.5 6 4.5 4.5C4.5 3 5.5 2 7 2C8.5 2 11 4.5 11 4.5M13.5 21C13.5 21 16 18.5 17.5 18.5C19 18.5 20 19.5 20 21C20 22.5 19 23.5 17.5 24.5C16.8333 25 15.8333 25.7 15 26" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const ParagraphIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 6H20M12 12H20M4 18H20M4 6L8 10L4 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const Heading1Icon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 12H20M4 18V6M12 18V6M16 10V18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const Heading2Icon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 12H14M4 18V6M9 18V6M14 12C14 12 17 12 17 15C17 18 14 18 14 18H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const Heading3Icon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 12H12M4 18V6M8 18V6M13 8H19C19 8 19 10 17 11C19 12 19 14 19 14H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const DividerHorizontalIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 12H21M5 8H19M8 4H16M8 16H16M5 20H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const UndoIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 10H16C18.7614 10 21 12.2386 21 15C21 17.7614 18.7614 20 16 20H12M3 10L7 6M3 10L7 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const RedoIcon: React.FC<IconProps> = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M21 10H8C5.23858 10 3 12.2386 3 15C3 17.7614 5.23858 20 8 20H12M21 10L17 6M21 10L17 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);