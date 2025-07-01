# app/services/export_service.py - ALVIN Export Service
import io
import os
import tempfile
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Union, BinaryIO
from flask import current_app
import logging

# Import export libraries
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from docx import Document
    from docx.shared import Inches
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    PYTHON_DOCX_AVAILABLE = True
except ImportError:
    PYTHON_DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)

class ExportService:
    """Service for exporting stories to various formats"""
    
    def __init__(self):
        self.supported_formats = ['txt', 'html']
        
        if REPORTLAB_AVAILABLE:
            self.supported_formats.append('pdf')
        
        if PYTHON_DOCX_AVAILABLE:
            self.supported_formats.append('docx')
    
    def export_story(self, project, scenes: List, format: str = 'txt') -> BinaryIO:
        """
        Export a complete story to the specified format
        
        Args:
            project: Project model instance
            scenes: List of scene model instances
            format: Export format ('txt', 'html', 'pdf', 'docx')
        
        Returns:
            BinaryIO: File-like object containing the exported story
        """
        if format not in self.supported_formats:
            raise ValueError(f"Format '{format}' not supported. Available: {self.supported_formats}")
        
        # Sort scenes by order
        sorted_scenes = sorted(scenes, key=lambda x: x.order_index or 0)
        
        # Generate content based on format
        if format == 'txt':
            return self._export_txt(project, sorted_scenes)
        elif format == 'html':
            return self._export_html(project, sorted_scenes)
        elif format == 'pdf':
            return self._export_pdf(project, sorted_scenes)
        elif format == 'docx':
            return self._export_docx(project, sorted_scenes)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_txt(self, project, scenes: List) -> BinaryIO:
        """Export to plain text format"""
        output = io.StringIO()
        
        # Title and metadata
        output.write(f"{project.title}\n")
        output.write("=" * len(project.title) + "\n\n")
        
        if project.description:
            output.write(f"{project.description}\n\n")
        
        output.write(f"Genre: {project.genre or 'Not specified'}\n")
        output.write(f"Word Count: {project.current_word_count or 0}\n")
        output.write(f"Created: {project.created_at.strftime('%Y-%m-%d') if project.created_at else 'Unknown'}\n")
        output.write(f"Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        output.write("-" * 50 + "\n\n")
        
        # Scenes
        for i, scene in enumerate(scenes, 1):
            output.write(f"Chapter {i}: {scene.title}\n")
            output.write("-" * (len(f"Chapter {i}: {scene.title}")) + "\n\n")
            
            if scene.description:
                output.write(f"[{scene.description}]\n\n")
            
            if scene.content:
                # Strip HTML tags for plain text
                import re
                clean_content = re.sub(r'<[^>]+>', '', scene.content)
                clean_content = clean_content.replace('&nbsp;', ' ')
                clean_content = clean_content.replace('&amp;', '&')
                clean_content = clean_content.replace('&lt;', '<')
                clean_content = clean_content.replace('&gt;', '>')
                
                output.write(clean_content)
                output.write("\n\n")
            
            if i < len(scenes):
                output.write("\n" + "=" * 20 + "\n\n")
        
        # Convert to bytes
        content = output.getvalue()
        output.close()
        
        return io.BytesIO(content.encode('utf-8'))
    
    def _export_html(self, project, scenes: List) -> BinaryIO:
        """Export to HTML format"""
        output = io.StringIO()
        
        # HTML structure
        output.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Georgia, serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 2.5em;
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        .metadata {{
            color: #7f8c8d;
            font-style: italic;
            margin: 10px 0;
        }}
        .description {{
            font-size: 1.1em;
            margin: 20px 0;
            color: #555;
        }}
        .chapter {{
            margin: 40px 0;
            page-break-before: always;
        }}
        .chapter-title {{
            font-size: 1.8em;
            color: #2c3e50;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .chapter-description {{
            font-style: italic;
            color: #7f8c8d;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
        }}
        .chapter-content {{
            text-align: justify;
            text-indent: 1.5em;
        }}
        .chapter-content p {{
            margin: 1em 0;
        }}
        @media print {{
            body {{ margin: 0; }}
            .chapter {{ page-break-before: always; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{title}</h1>
        <div class="metadata">
            <p>Genre: {genre}</p>
            <p>Word Count: {word_count}</p>
            <p>Created: {created}</p>
            <p>Exported: {exported}</p>
        </div>
        {description_html}
    </div>
""".format(
            title=project.title,
            genre=project.genre or 'Not specified',
            word_count=project.current_word_count or 0,
            created=project.created_at.strftime('%Y-%m-%d') if project.created_at else 'Unknown',
            exported=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
            description_html=f'<div class="description">{project.description}</div>' if project.description else ''
        ))
        
        # Chapters/Scenes
        for i, scene in enumerate(scenes, 1):
            output.write(f"""
    <div class="chapter">
        <h2 class="chapter-title">Chapter {i}: {scene.title}</h2>
        {f'<div class="chapter-description">{scene.description}</div>' if scene.description else ''}
        <div class="chapter-content">
            {scene.content or '<p><em>No content available.</em></p>'}
        </div>
    </div>
""")
        
        output.write("""
</body>
</html>""")
        
        # Convert to bytes
        content = output.getvalue()
        output.close()
        
        return io.BytesIO(content.encode('utf-8'))
    
    def _export_pdf(self, project, scenes: List) -> BinaryIO:
        """Export to PDF format using ReportLab"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab not available. Install with: pip install reportlab")
        
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get default styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor='#2c3e50'
        )
        
        chapter_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            spaceBefore=30,
            textColor='#2c3e50'
        )
        
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor='#7f8c8d',
            spaceAfter=20
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            firstLineIndent=20
        )
        
        # Build story content
        story = []
        
        # Title page
        story.append(Paragraph(project.title, title_style))
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata_text = f"""
        Genre: {project.genre or 'Not specified'}<br/>
        Word Count: {project.current_word_count or 0}<br/>
        Created: {project.created_at.strftime('%Y-%m-%d') if project.created_at else 'Unknown'}<br/>
        Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
        """
        story.append(Paragraph(metadata_text, metadata_style))
        
        if project.description:
            story.append(Spacer(1, 12))
            story.append(Paragraph(project.description, body_style))
        
        story.append(PageBreak())
        
        # Chapters/Scenes
        for i, scene in enumerate(scenes, 1):
            # Chapter title
            story.append(Paragraph(f"Chapter {i}: {scene.title}", chapter_style))
            
            # Chapter description
            if scene.description:
                desc_style = ParagraphStyle(
                    'Description',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=TA_LEFT,
                    textColor='#7f8c8d',
                    spaceAfter=15,
                    leftIndent=20,
                    fontName='Helvetica-Oblique'
                )
                story.append(Paragraph(f"[{scene.description}]", desc_style))
            
            # Chapter content
            if scene.content:
                # Clean HTML content for PDF
                import re
                clean_content = re.sub(r'<[^>]+>', '', scene.content)
                clean_content = clean_content.replace('&nbsp;', ' ')
                clean_content = clean_content.replace('&amp;', '&')
                clean_content = clean_content.replace('&lt;', '<')
                clean_content = clean_content.replace('&gt;', '>')
                
                # Split into paragraphs
                paragraphs = clean_content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), body_style))
            
            # Page break between chapters (except last)
            if i < len(scenes):
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _export_docx(self, project, scenes: List) -> BinaryIO:
        """Export to Microsoft Word format"""
        if not PYTHON_DOCX_AVAILABLE:
            raise ImportError("python-docx not available. Install with: pip install python-docx")
        
        # Create document
        doc = Document()
        
        # Add title
        title = doc.add_heading(project.title, 0)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Add metadata
        metadata = doc.add_paragraph()
        metadata.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = metadata.add_run(f"""
Genre: {project.genre or 'Not specified'}
Word Count: {project.current_word_count or 0}
Created: {project.created_at.strftime('%Y-%m-%d') if project.created_at else 'Unknown'}
Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
        """.strip())
        run.italic = True
        
        # Add description if exists
        if project.description:
            doc.add_paragraph()
            desc_para = doc.add_paragraph(project.description)
            desc_para.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        
        # Add page break
        doc.add_page_break()
        
        # Add chapters/scenes
        for i, scene in enumerate(scenes, 1):
            # Chapter title
            chapter_title = doc.add_heading(f"Chapter {i}: {scene.title}", level=1)
            
            # Chapter description
            if scene.description:
                desc_para = doc.add_paragraph()
                run = desc_para.add_run(f"[{scene.description}]")
                run.italic = True
                run.font.color.rgb = None  # Gray color would require additional imports
            
            # Chapter content
            if scene.content:
                # Clean HTML content
                import re
                clean_content = re.sub(r'<[^>]+>', '', scene.content)
                clean_content = clean_content.replace('&nbsp;', ' ')
                clean_content = clean_content.replace('&amp;', '&')
                clean_content = clean_content.replace('&lt;', '<')
                clean_content = clean_content.replace('&gt;', '>')
                
                # Split into paragraphs
                paragraphs = clean_content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        content_para = doc.add_paragraph(para.strip())
                        content_para.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
            
            # Page break between chapters (except last)
            if i < len(scenes):
                doc.add_page_break()
        
        # Save to buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer
    
    def export_project_data(self, project, scenes: List, story_objects: List) -> BinaryIO:
        """
        Export complete project data as JSON for backup/import
        
        Args:
            project: Project model instance
            scenes: List of scene model instances  
            story_objects: List of story object model instances
        
        Returns:
            BinaryIO: JSON file containing all project data
        """
        import json
        
        # Build export data structure
        export_data = {
            'export_info': {
                'version': '1.0',
                'exported_at': datetime.utcnow().isoformat(),
                'exported_by': 'ALVIN v1.0'
            },
            'project': {
                'title': project.title,
                'description': project.description,
                'genre': project.genre,
                'current_phase': project.current_phase,
                'target_word_count': project.target_word_count,
                'current_word_count': project.current_word_count,
                'status': project.status,
                'tone': project.tone,
                'target_audience': project.target_audience,
                'estimated_scope': project.estimated_scope,
                'marketability': project.marketability,
                'original_idea': project.original_idea,
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'updated_at': project.updated_at.isoformat() if project.updated_at else None
            },
            'scenes': [
                {
                    'title': scene.title,
                    'description': scene.description,
                    'content': scene.content,
                    'scene_type': scene.scene_type,
                    'emotional_intensity': scene.emotional_intensity,
                    'order_index': scene.order_index,
                    'status': scene.status,
                    'word_count': scene.word_count,
                    'created_at': scene.created_at.isoformat() if scene.created_at else None,
                    'updated_at': scene.updated_at.isoformat() if scene.updated_at else None
                }
                for scene in sorted(scenes, key=lambda x: x.order_index or 0)
            ],
            'story_objects': [
                {
                    'name': obj.name,
                    'object_type': obj.object_type,
                    'description': obj.description,
                    'importance': obj.importance,
                    'character_role': obj.character_role,
                    'symbolic_meaning': obj.symbolic_meaning,
                    'attributes': obj.attributes,
                    'status': obj.status,
                    'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    'updated_at': obj.updated_at.isoformat() if obj.updated_at else None
                }
                for obj in story_objects
            ]
        }
        
        # Convert to JSON bytes
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        return io.BytesIO(json_str.encode('utf-8'))
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return self.supported_formats.copy()
    
    def get_export_filename(self, project, format: str) -> str:
        """Generate appropriate filename for export"""
        # Clean title for filename
        import re
        clean_title = re.sub(r'[^\w\s-]', '', project.title)
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M')
        
        return f"{clean_title}_{timestamp}.{format}"