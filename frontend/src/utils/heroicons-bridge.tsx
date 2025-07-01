// src/utils/heroicons-bridge.tsx
/**
 * This file bridges old Heroicons names to new ones in v2.0.18+
 * 
 * Usage:
 * Instead of:
 * import { ViewBoardsIcon } from '@heroicons/react/24/outline';
 * 
 * Use:
 * import { ViewBoardsIcon } from '../utils/heroicons-bridge';
 */

import {
  // New icon imports from Heroicons v2
  Squares2X2Icon,
  CheckBadgeIcon,
  DocumentDuplicateIcon,
  ArrowDownTrayIcon,
  ArrowsUpDownIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  ExclamationCircleIcon,
  Bars2Icon,
  ChatBubbleBottomCenterTextIcon,
  XMarkIcon,
  BoltIcon,
  ListBulletIcon,
  // Keep all other icons you're using directly
  UserIcon,
  MapPinIcon,
  CubeIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  ArrowLeftIcon,
  BookOpenIcon,
  DocumentTextIcon,
  SparklesIcon,
  ShareIcon,
  SunIcon,
  MoonIcon,
  ChevronUpIcon,
  FlagIcon,
  ChatBubbleLeftIcon,
  HeartIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';

// Map old icon names to new ones
export { Squares2X2Icon as ViewBoardsIcon };
export { CheckBadgeIcon as BadgeCheckIcon };
export { DocumentDuplicateIcon as DuplicateIcon };
export { ArrowDownTrayIcon as DownloadIcon };
export { ArrowsUpDownIcon as ArrowsExpandIcon };
export { MagnifyingGlassIcon as SearchIcon };
export { ArrowPathIcon as RefreshIcon };
export { ExclamationCircleIcon as ExclamationIcon };
export { Bars2Icon as MenuAlt2Icon };
export { ChatBubbleBottomCenterTextIcon as ChatAlt2Icon };
export { XMarkIcon as XIcon };
export { BoltIcon as LightningBoltIcon };
export { ListBulletIcon as ViewListIcon };

// Re-export all other icons to allow importing everything from this file
export {
  UserIcon,
  MapPinIcon,
  CubeIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  ArrowLeftIcon,
  BookOpenIcon,
  DocumentTextIcon,
  SparklesIcon,
  ExclamationCircleIcon, // Also exported directly 
  CheckBadgeIcon, // Also exported directly
  ShareIcon,
  SunIcon,
  MoonIcon,
  ChevronUpIcon,
  FlagIcon,
  ChatBubbleLeftIcon,
  HeartIcon,
  UserGroupIcon,
};