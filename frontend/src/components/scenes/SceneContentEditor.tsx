// File: src/components/scenes/SceneContentEditor.tsx
import { useEffect, useRef } from 'react'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import CharacterCount from '@tiptap/extension-character-count'
import Placeholder from '@tiptap/extension-placeholder'

// Note: In a real implementation, you would need to install these dependencies:
// npm install @tiptap/react @tiptap/starter-kit @tiptap/extension-character-count @tiptap/extension-placeholder

type SceneContentEditorProps = {
  content: string
  onChange: (content: string) => void
}

const SceneContentEditor = ({ content, onChange }: SceneContentEditorProps) => {
  const editorRef = useRef<HTMLDivElement>(null)
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      CharacterCount.configure({
        limit: 50000,
      }),
      Placeholder.configure({
        placeholder: 'Start writing your scene here...',
      }),
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    autofocus: 'end',
  })
  
  // Update content when prop changes
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content)
    }
  }, [content, editor])
  
  // Handle tab key for indentation
  useEffect(() => {
    if (!editorRef.current) return
    
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab' && editor) {
        event.preventDefault()
        editor.commands.insertContent('&nbsp;&nbsp;&nbsp;&nbsp;')
      }
    }
    
    editorRef.current.addEventListener('keydown', handleKeyDown)
    
    return () => {
      editorRef.current?.removeEventListener('keydown', handleKeyDown)
    }
  }, [editor])
  
  return (
    <div className="card min-h-[500px] flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-700">Scene Content</h3>
        {editor && (
          <span className="text-xs text-gray-500">
            {editor.storage.characterCount.characters()}/50,000 characters
          </span>
        )}
      </div>
      
      <div 
        className="flex-1 border border-gray-300 rounded-md overflow-y-auto"
        ref={editorRef}
      >
        <EditorContent 
          editor={editor} 
          className="h-full px-4 py-3 prose max-w-none"
        />
      </div>
    </div>
  )
}

export default SceneContentEditor