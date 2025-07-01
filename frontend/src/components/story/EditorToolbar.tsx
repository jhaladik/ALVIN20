// src/components/story/EditorToolbar.tsx
import React from 'react';
import { Editor } from '@tiptap/react';
import {
  BoldIcon,
  ItalicIcon,
  ListBulletIcon,
  ListOrderedIcon,
  QuoteIcon,
  LinkIcon,
  ParagraphIcon,
  Heading1Icon,
  Heading2Icon,
  Heading3Icon,
  DividerHorizontalIcon,
  UndoIcon,
  RedoIcon,
} from './EditorIcons'; // You'd create these icons or import from a library

interface EditorToolbarProps {
  editor: Editor | null;
}

const EditorToolbar: React.FC<EditorToolbarProps> = ({ editor }) => {
  if (!editor) {
    return null;
  }
  
  return (
    <div className="flex flex-wrap items-center gap-1">
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('bold') ? 'bg-gray-100' : ''}`}
        title="Bold"
      >
        <BoldIcon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('italic') ? 'bg-gray-100' : ''}`}
        title="Italic"
      >
        <ItalicIcon className="h-4 w-4" />
      </button>
      
      <span className="border-l border-gray-200 mx-1 h-5"></span>
      
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('heading', { level: 1 }) ? 'bg-gray-100' : ''}`}
        title="Heading 1"
      >
        <Heading1Icon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('heading', { level: 2 }) ? 'bg-gray-100' : ''}`}
        title="Heading 2"
      >
        <Heading2Icon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('heading', { level: 3 }) ? 'bg-gray-100' : ''}`}
        title="Heading 3"
      >
        <Heading3Icon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => editor.chain().focus().setParagraph().run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('paragraph') ? 'bg-gray-100' : ''}`}
        title="Paragraph"
      >
        <ParagraphIcon className="h-4 w-4" />
      </button>
      
      <span className="border-l border-gray-200 mx-1 h-5"></span>
      
      <button
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('bulletList') ? 'bg-gray-100' : ''}`}
        title="Bullet List"
      >
        <ListBulletIcon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('orderedList') ? 'bg-gray-100' : ''}`}
        title="Ordered List"
      >
        <ListOrderedIcon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        className={`p-1 rounded hover:bg-gray-100 ${editor.isActive('blockquote') ? 'bg-gray-100' : ''}`}
        title="Quote"
      >
        <QuoteIcon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => editor.chain().focus().setHorizontalRule().run()}
        className="p-1 rounded hover:bg-gray-100"
        title="Horizontal Rule"
      >
        <DividerHorizontalIcon className="h-4 w-4" />
      </button>
      
      <span className="border-l border-gray-200 mx-1 h-5"></span>
      
      <button
        onClick={() => editor.chain().focus().undo().run()}
        disabled={!editor.can().undo()}
        className="p-1 rounded hover:bg-gray-100 disabled:opacity-30"
        title="Undo"
      >
        <UndoIcon className="h-4 w-4" />
      </button>
      
      <button
        onClick={() => editor.chain().focus().redo().run()}
        disabled={!editor.can().redo()}
        className="p-1 rounded hover:bg-gray-100 disabled:opacity-30"
        title="Redo"
      >
        <RedoIcon className="h-4 w-4" />
      </button>
    </div>
  );
};

export default EditorToolbar;