// src/components/story/ChapterOrganizer.tsx
import React from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { ChapterData } from '../../types';
import { RefreshIcon, PencilIcon } from '@heroicons/react/24/outline';

interface ChapterOrganizerProps {
  chapters: ChapterData[];
  onChapterSelect: (index: number) => void;
  onRegenerateChapter: (index: number) => void;
}

const ChapterOrganizer: React.FC<ChapterOrganizerProps> = ({
  chapters,
  onChapterSelect,
  onRegenerateChapter
}) => {
  const handleDragEnd = (result: any) => {
    // In a real implementation, this would reorder the chapters
    // Not implementing the full drag & drop functionality here for brevity
    if (!result.destination) return;
    // Would call a parent function to update chapter order
  };
  
  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <Droppable droppableId="chapters">
        {(provided) => (
          <div
            {...provided.droppableProps}
            ref={provided.innerRef}
            className="space-y-2"
          >
            {chapters.map((chapter, index) => (
              <Draggable key={chapter.id} draggableId={chapter.id} index={index}>
                {(provided) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                    className="bg-gray-50 rounded p-2 cursor-pointer border border-gray-200 hover:border-indigo-300 transition-colors"
                    onClick={() => onChapterSelect(index)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1 mr-2">
                        <div className="text-xs text-gray-500">Chapter {index + 1}</div>
                        <div className="text-sm font-medium truncate">{chapter.title}</div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onRegenerateChapter(index);
                        }}
                        className="text-gray-500 hover:text-indigo-600 p-1"
                        title="Regenerate chapter"
                      >
                        <RefreshIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </DragDropContext>
  );
};

export default ChapterOrganizer;