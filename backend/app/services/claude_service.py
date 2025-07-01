# app/services/claude_service.py - ALVIN Claude AI Service
import json
import logging
from typing import Dict, List, Optional, Any
from flask import current_app
import anthropic

logger = logging.getLogger(__name__)

class ClaudeService:
    """Service for interacting with Claude AI API"""
    
    def __init__(self):
        self.api_key = current_app.config.get('ANTHROPIC_API_KEY')
        self.model = current_app.config.get('DEFAULT_CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        self.simulation_mode = current_app.config.get('AI_SIMULATION_MODE', False)
        
        if not self.simulation_mode and not self.api_key:
            logger.warning("Claude API key not found. Running in simulation mode.")
            self.simulation_mode = True
        
        if not self.simulation_mode:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def _make_request(self, prompt: str, max_tokens: int = 4000, system_prompt: str = None) -> Dict[str, Any]:
        """Make a request to Claude API or return simulated response"""
        
        if self.simulation_mode:
            return self._simulate_response(prompt, max_tokens)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                system=system_prompt
            )
            
            return {
                'content': response.content[0].text,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }
        
        except Exception as e:
            logger.error(f"Claude API request failed: {str(e)}")
            return self._simulate_response(prompt, max_tokens, error=True)
    
    def _simulate_response(self, prompt: str, max_tokens: int, error: bool = False) -> Dict[str, Any]:
        """Simulate Claude response for testing/development"""
        
        if error:
            return {
                'content': 'Simulated response due to API error',
                'usage': {'input_tokens': 100, 'output_tokens': 50}
            }
        
        # Simple simulation based on prompt content
        if 'analyze-idea' in prompt.lower():
            content = {
                "story_assessment": {
                    "genre": "mystery",
                    "tone": "suspenseful",
                    "target_audience": "adults",
                    "estimated_scope": "novella",
                    "marketability": 4
                },
                "strengths": ["Intriguing premise", "Strong emotional hook", "Clear protagonist motivation"],
                "areas_for_development": ["Character depth", "Setting details", "Plot structure"],
                "character_suggestions": [
                    {"name": "Detective Sarah Chen", "role": "protagonist", "description": "Experienced detective with personal connection to the case"},
                    {"name": "Dr. Michael Torres", "role": "supporting", "description": "Forensic psychologist who provides insights"}
                ],
                "scene_suggestions": [
                    {"title": "The Discovery", "type": "opening", "description": "The mysterious letter is found"},
                    {"title": "First Clue", "type": "development", "description": "Decoding the first part of the letter"},
                    {"title": "The Revelation", "type": "climax", "description": "The truth behind the letter is revealed"}
                ]
            }
        
        elif 'create-project' in prompt.lower():
            content = {
                "title": "The Grandmother's Secret",
                "description": "A thrilling mystery about family secrets and hidden truths",
                "genre": "mystery",
                "tone": "suspenseful",
                "target_audience": "adults",
                "estimated_scope": "novella",
                "marketability": 4,
                "target_word_count": 50000,
                "scenes": [
                    {"title": "The Attic Discovery", "type": "opening", "description": "Finding the mysterious letter"},
                    {"title": "First Investigation", "type": "development", "description": "Beginning to decode the letter"},
                    {"title": "Family Secrets", "type": "climax", "description": "Uncovering the truth"}
                ],
                "story_objects": [
                    {"name": "Detective Emma", "type": "character", "role": "protagonist", "description": "Young detective"},
                    {"name": "Grandmother's Attic", "type": "location", "description": "Where the mystery begins"},
                    {"name": "Coded Letter", "type": "object", "description": "The central mystery object"}
                ]
            }
        
        elif 'analyze-structure' in prompt.lower():
            content = {
                "structure_analysis": {
                    "overall_pacing": "Good progression with room for improvement",
                    "scene_balance": "Well-distributed scene types",
                    "emotional_arc": "Strong emotional progression",
                    "plot_coherence": "Logical plot development"
                },
                "recommendations": [
                    "Consider adding a transitional scene between scenes 2 and 3",
                    "Increase emotional intensity in the climax scene",
                    "Add more character development in the middle sections"
                ],
                "scene_analysis": [
                    {"scene_id": 1, "effectiveness": 0.8, "suggestions": ["Strengthen opening hook"]},
                    {"scene_id": 2, "effectiveness": 0.7, "suggestions": ["Add more conflict"]}
                ]
            }
        
        elif 'suggest-scenes' in prompt.lower():
            content = {
                "suggestions": [
                    {
                        "title": "The Confrontation",
                        "type": "climax",
                        "description": "The protagonist faces the antagonist in a final showdown",
                        "emotional_intensity": 0.9,
                        "placement_suggestion": "Before the current ending"
                    },
                    {
                        "title": "Moment of Doubt",
                        "type": "development",
                        "description": "The protagonist questions their mission and methods",
                        "emotional_intensity": 0.6,
                        "placement_suggestion": "Middle of the story"
                    }
                ]
            }
        
        elif 'analyze-scene' in prompt.lower():
            content = {
                "scene_analysis": {
                    "strengths": ["Strong dialogue", "Good pacing", "Clear character motivation"],
                    "weaknesses": ["Lacks sensory details", "Could use more tension"],
                    "suggestions": [
                        "Add more descriptive language to set the scene",
                        "Increase the stakes for the protagonist",
                        "Consider adding a plot twist or revelation"
                    ],
                    "effectiveness_score": 0.75,
                    "emotional_impact": 0.6
                }
            }
        
        elif 'generate-story' in prompt.lower():
            content = {
                "story": {
                    "title": "Generated Story",
                    "content": "<h1>Chapter 1: The Beginning</h1><p>The story unfolds with careful attention to character development and plot progression. Each scene builds upon the previous one, creating a compelling narrative that engages the reader from start to finish.</p><h1>Chapter 2: The Development</h1><p>As the plot thickens, our characters face new challenges that test their resolve and push the story toward its inevitable conclusion.</p>",
                    "word_count": 1200,
                    "chapters": 3
                }
            }
        
        else:
            content = "Simulated Claude response for development/testing purposes."
        
        return {
            'content': json.dumps(content) if isinstance(content, dict) else content,
            'usage': {
                'input_tokens': len(prompt) // 4,  # Rough estimate
                'output_tokens': 200
            }
        }
    
    def analyze_story_idea(self, idea_text: str, story_intent: str = None, 
                          target_audience: str = None, preferred_genre: str = None) -> Dict[str, Any]:
        """Analyze a story idea and provide feedback and suggestions"""
        
        system_prompt = """You are an expert story development assistant. Analyze the provided story idea and return a JSON response with the following structure:

{
    "story_assessment": {
        "genre": "primary genre",
        "tone": "overall tone",
        "target_audience": "suggested target audience",
        "estimated_scope": "short story/novella/novel",
        "marketability": 1-5
    },
    "strengths": ["list of story strengths"],
    "areas_for_development": ["areas that need work"],
    "character_suggestions": [
        {"name": "character name", "role": "protagonist/antagonist/supporting", "description": "brief description"}
    ],
    "scene_suggestions": [
        {"title": "scene title", "type": "opening/inciting/development/climax/resolution", "description": "scene description"}
    ]
}

Provide constructive, specific feedback that helps develop the idea into a full story."""

        prompt = f"""Story Idea: {idea_text}

Story Intent: {story_intent or 'Not specified'}
Target Audience: {target_audience or 'Not specified'}
Preferred Genre: {preferred_genre or 'Not specified'}

Please analyze this story idea and provide detailed feedback and suggestions."""

        response = self._make_request(prompt, max_tokens=3000, system_prompt=system_prompt)
        
        try:
            analysis = json.loads(response['content'])
            return {
                'analysis': analysis,
                'usage': response['usage']
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude response as JSON")
            return {
                'analysis': {'error': 'Failed to parse AI response'},
                'usage': response['usage']
            }
    
    def create_project_from_idea(self, idea_text: str, title_override: str = None) -> Dict[str, Any]:
        """Create a complete project structure from a story idea"""
        
        system_prompt = """You are an expert story development assistant. Create a complete project structure from the provided story idea. Return a JSON response with this exact structure:

{
    "title": "project title",
    "description": "project description",
    "genre": "genre",
    "tone": "tone",
    "target_audience": "target audience",
    "estimated_scope": "scope",
    "marketability": 1-5,
    "target_word_count": number,
    "attributes": {
        "themes": ["theme1", "theme2"],
        "keywords": ["keyword1", "keyword2"]
    },
    "scenes": [
        {"title": "scene title", "type": "opening/inciting/development/climax/resolution", "description": "scene description", "emotional_intensity": 0.0-1.0}
    ],
    "story_objects": [
        {"name": "object name", "type": "character/location/object/concept", "role": "role if character", "description": "description"}
    ]
}

Create a well-structured foundation for the story project."""

        prompt = f"""Story Idea: {idea_text}

{f'Preferred Title: {title_override}' if title_override else ''}

Please create a complete project structure from this idea, including scenes and story objects."""

        response = self._make_request(prompt, max_tokens=4000, system_prompt=system_prompt)
        
        try:
            project_data = json.loads(response['content'])
            if title_override:
                project_data['title'] = title_override
            
            return {
                **project_data,
                'usage': response['usage']
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude project creation response as JSON")
            return {
                'title': title_override or 'Untitled Story',
                'description': 'Generated from AI analysis',
                'usage': response['usage']
            }
    
    def analyze_story_structure(self, project, scenes: List) -> Dict[str, Any]:
        """Analyze the overall structure of a story project"""
        
        system_prompt = """You are an expert story structure analyst. Analyze the provided project and scenes, then return a JSON response with this structure:

{
    "structure_analysis": {
        "overall_pacing": "assessment",
        "scene_balance": "assessment",
        "emotional_arc": "assessment",
        "plot_coherence": "assessment"
    },
    "recommendations": ["list of specific recommendations"],
    "scene_analysis": [
        {"scene_id": number, "effectiveness": 0.0-1.0, "suggestions": ["suggestions"]}
    ]
}

Provide actionable feedback for improving the story structure."""

        scenes_text = "\n".join([
            f"Scene {i+1} ({scene.scene_type}): {scene.title} - {scene.description}"
            for i, scene in enumerate(scenes)
        ])

        prompt = f"""Project: {project.title}
Genre: {project.genre}
Description: {project.description}

Scenes:
{scenes_text}

Please analyze the story structure and provide recommendations."""

        response = self._make_request(prompt, max_tokens=3000, system_prompt=system_prompt)
        
        try:
            analysis = json.loads(response['content'])
            return {
                'analysis': analysis,
                'usage': response['usage']
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude structure analysis response as JSON")
            return {
                'analysis': {'error': 'Failed to parse AI response'},
                'usage': response['usage']
            }
    
    def suggest_scenes(self, project, existing_scenes: List) -> Dict[str, Any]:
        """Generate scene suggestions for a project"""
        
        system_prompt = """You are an expert story development assistant. Based on the project details and existing scenes, suggest new scenes that would improve the story. Return a JSON response:

{
    "suggestions": [
        {
            "title": "scene title",
            "type": "opening/inciting/development/climax/resolution/transition",
            "description": "detailed scene description",
            "emotional_intensity": 0.0-1.0,
            "placement_suggestion": "where to place this scene"
        }
    ]
}

Focus on scenes that fill gaps in the story structure or enhance the narrative."""

        existing_scenes_text = "\n".join([
            f"Scene {i+1} ({scene.scene_type}): {scene.title} - {scene.description}"
            for i, scene in enumerate(existing_scenes)
        ])

        prompt = f"""Project: {project.title}
Genre: {project.genre}
Description: {project.description}

Existing Scenes:
{existing_scenes_text}

Please suggest additional scenes that would improve this story."""

        response = self._make_request(prompt, max_tokens=3000, system_prompt=system_prompt)
        
        try:
            suggestions = json.loads(response['content'])
            return {
                'suggestions': suggestions.get('suggestions', []),
                'usage': response['usage']
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude scene suggestions response as JSON")
            return {
                'suggestions': [],
                'usage': response['usage']
            }
    
    def analyze_scene(self, scene, critic_type: str, focus_areas: List[str]) -> Dict[str, Any]:
        """Analyze a specific scene with a particular critical focus"""
        
        critic_prompts = {
            'structure': 'Focus on scene structure, pacing, and narrative flow.',
            'character': 'Focus on character development, dialogue, and relationships.',
            'dialogue': 'Focus specifically on dialogue quality, authenticity, and impact.',
            'pacing': 'Focus on narrative pacing, tension, and rhythm.',
            'emotion': 'Focus on emotional impact, character emotions, and reader engagement.',
            'plot': 'Focus on plot advancement, conflict, and story momentum.'
        }

        system_prompt = f"""You are an expert literary critic specializing in {critic_type} analysis. Analyze the provided scene and return a JSON response:

{{
    "scene_analysis": {{
        "strengths": ["list of strengths"],
        "weaknesses": ["list of weaknesses"],
        "suggestions": ["specific improvement suggestions"],
        "effectiveness_score": 0.0-1.0,
        "emotional_impact": 0.0-1.0
    }}
}}

{critic_prompts.get(critic_type, 'Provide comprehensive analysis.')}
{f'Pay special attention to: {", ".join(focus_areas)}' if focus_areas else ''}"""

        prompt = f"""Scene Title: {scene.title}
Scene Type: {scene.scene_type}
Description: {scene.description}
Content: {scene.content or 'No content provided'}

Please analyze this scene with focus on {critic_type}."""

        response = self._make_request(prompt, max_tokens=2000, system_prompt=system_prompt)
        
        try:
            analysis = json.loads(response['content'])
            return {
                'analysis': analysis,
                'usage': response['usage']
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude scene analysis response as JSON")
            return {
                'analysis': {'error': 'Failed to parse AI response'},
                'usage': response['usage']
            }
    
    def generate_full_story(self, project, scenes: List, narrative_options: Dict, 
                           target_length: str, style_preferences: Dict) -> Dict[str, Any]:
        """Generate a complete story from project scenes"""
        
        length_tokens = {
            'short': 2000,
            'medium': 4000,
            'long': 8000
        }
        
        max_tokens = length_tokens.get(target_length, 4000)

        system_prompt = """You are an expert fiction writer. Generate a complete story based on the provided project details and scenes. Return a JSON response:

{
    "story": {
        "title": "story title",
        "content": "full story content in HTML format with proper chapter/section structure",
        "word_count": number,
        "chapters": number
    }
}

Write engaging, well-crafted prose that brings the scenes to life as a cohesive narrative."""

        scenes_outline = "\n".join([
            f"Scene {i+1}: {scene.title} ({scene.scene_type})\n{scene.description}"
            for i, scene in enumerate(scenes)
        ])

        prompt = f"""Project: {project.title}
Genre: {project.genre}
Target Length: {target_length}
Narrative Options: {json.dumps(narrative_options)}
Style Preferences: {json.dumps(style_preferences)}

Scene Outline:
{scenes_outline}

Please generate a complete story based on these scenes."""

        response = self._make_request(prompt, max_tokens=max_tokens, system_prompt=system_prompt)
        
        try:
            story_data = json.loads(response['content'])
            return {
                'story': story_data.get('story', {}),
                'usage': response['usage']
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse Claude story generation response as JSON")
            return {
                'story': {
                    'title': project.title,
                    'content': 'Story generation failed. Please try again.',
                    'word_count': 0,
                    'chapters': 0
                },
                'usage': response['usage']
            }