# app/services/token_service.py - ALVIN Token Estimation Service
import re
import json
from typing import Dict, List, Optional, Tuple
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class TokenService:
    """Service for estimating and tracking token usage for AI operations"""
    
    def __init__(self):
        # Base token costs for different operations (estimated)
        self.operation_costs = {
            'analyze_idea': {
                'base_cost': 100,
                'per_100_chars': 15,
                'output_multiplier': 1.5
            },
            'create_project_from_idea': {
                'base_cost': 200,
                'per_100_chars': 20,
                'output_multiplier': 2.0
            },
            'analyze_structure': {
                'base_cost': 150,
                'per_100_chars': 10,
                'output_multiplier': 1.3
            },
            'suggest_scenes': {
                'base_cost': 180,
                'per_100_chars': 12,
                'output_multiplier': 1.8
            },
            'generate_story': {
                'base_cost': 300,
                'per_100_chars': 25,
                'output_multiplier': 3.0
            },
            'analyze_scene': {
                'base_cost': 80,
                'per_100_chars': 8,
                'output_multiplier': 1.2
            },
            'character_development': {
                'base_cost': 120,
                'per_100_chars': 10,
                'output_multiplier': 1.4
            },
            'plot_suggestions': {
                'base_cost': 160,
                'per_100_chars': 15,
                'output_multiplier': 1.6
            },
            'dialogue_enhancement': {
                'base_cost': 90,
                'per_100_chars': 8,
                'output_multiplier': 1.1
            },
            'style_analysis': {
                'base_cost': 70,
                'per_100_chars': 6,
                'output_multiplier': 1.0
            }
        }
        
        # Multipliers for different target lengths
        self.length_multipliers = {
            'short': 0.8,
            'medium': 1.0,
            'long': 1.5,
            'very_long': 2.0
        }
        
        # Claude model token limits and pricing (per 1M tokens)
        self.model_limits = {
            'claude-3-5-sonnet-20241022': {
                'max_tokens': 200000,
                'input_cost': 3.00,   # $3 per 1M input tokens
                'output_cost': 15.00  # $15 per 1M output tokens
            },
            'claude-3-haiku-20240307': {
                'max_tokens': 200000,
                'input_cost': 0.25,   # $0.25 per 1M input tokens
                'output_cost': 1.25   # $1.25 per 1M output tokens
            }
        }
    
    def estimate_operation_cost(self, operation_type: str, input_text: str, 
                              target_length: str = 'medium') -> int:
        """
        Estimate token cost for a specific AI operation
        
        Args:
            operation_type: Type of operation (e.g., 'analyze_idea')
            input_text: Input text to be processed
            target_length: Expected output length ('short', 'medium', 'long')
        
        Returns:
            Estimated token cost as integer
        """
        if operation_type not in self.operation_costs:
            logger.warning(f"Unknown operation type: {operation_type}")
            return self._estimate_generic_cost(input_text)
        
        config = self.operation_costs[operation_type]
        
        # Calculate input cost
        input_chars = len(input_text)
        input_cost = config['base_cost']
        input_cost += (input_chars // 100) * config['per_100_chars']
        
        # Calculate estimated output cost
        output_cost = input_cost * config['output_multiplier']
        
        # Apply length multiplier
        length_mult = self.length_multipliers.get(target_length, 1.0)
        total_cost = int((input_cost + output_cost) * length_mult)
        
        # Add safety margin (10%)
        total_cost = int(total_cost * 1.1)
        
        logger.info(f"Estimated cost for {operation_type}: {total_cost} tokens")
        return total_cost
    
    def _estimate_generic_cost(self, input_text: str) -> int:
        """Fallback estimation for unknown operations"""
        chars = len(input_text)
        base_cost = 100
        variable_cost = (chars // 100) * 10
        return int((base_cost + variable_cost) * 1.5)  # Conservative estimate
    
    def estimate_claude_tokens(self, text: str) -> int:
        """
        Estimate token count for Claude API
        Uses approximation: 1 token ≈ 4 characters for English text
        
        Args:
            text: Text to estimate tokens for
        
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Remove extra whitespace
        clean_text = ' '.join(text.split())
        
        # Rough approximation: 1 token ≈ 4 characters
        # This varies by language and content, but gives a reasonable estimate
        estimated_tokens = len(clean_text) // 4
        
        # Add safety margin for complex content
        if self._has_complex_content(clean_text):
            estimated_tokens = int(estimated_tokens * 1.2)
        
        return max(estimated_tokens, 1)  # Minimum 1 token
    
    def _has_complex_content(self, text: str) -> bool:
        """Check if text has complex content that might use more tokens"""
        # Check for code, special characters, multiple languages, etc.
        complex_indicators = [
            r'[{}[\]()&<>]',  # Code-like characters
            r'[^\x00-\x7F]',  # Non-ASCII characters
            r'\n\s*\n',       # Multiple line breaks
            r'https?://',     # URLs
            r'[A-Z]{2,}',     # Acronyms
        ]
        
        for pattern in complex_indicators:
            if re.search(pattern, text):
                return True
        
        return False
    
    def estimate_project_analysis_cost(self, project, scenes: List = None) -> Dict:
        """
        Estimate costs for various project analysis operations
        
        Args:
            project: Project model instance
            scenes: Optional list of scene model instances
        
        Returns:
            Dictionary with cost estimates for different operations
        """
        # Gather project content
        project_text = f"{project.title}\n{project.description or ''}\n{project.original_idea or ''}"
        
        # Add scenes content if provided
        if scenes:
            scenes_text = "\n".join([
                f"{scene.title}\n{scene.description or ''}\n{scene.content or ''}"
                for scene in scenes
            ])
            full_text = f"{project_text}\n{scenes_text}"
        else:
            full_text = project_text
        
        # Estimate costs for different operations
        estimates = {
            'structure_analysis': self.estimate_operation_cost('analyze_structure', full_text),
            'scene_suggestions': self.estimate_operation_cost('suggest_scenes', project_text),
            'character_development': self.estimate_operation_cost('character_development', full_text),
            'plot_enhancement': self.estimate_operation_cost('plot_suggestions', full_text),
            'style_analysis': self.estimate_operation_cost('style_analysis', full_text, 'short'),
            'full_story_generation': self.estimate_operation_cost('generate_story', full_text, 'long')
        }
        
        # Calculate total for all operations
        estimates['total_all_operations'] = sum(estimates.values())
        
        return estimates
    
    def estimate_scene_operations_cost(self, scene) -> Dict:
        """
        Estimate costs for scene-specific operations
        
        Args:
            scene: Scene model instance
        
        Returns:
            Dictionary with cost estimates for scene operations
        """
        scene_text = f"{scene.title}\n{scene.description or ''}\n{scene.content or ''}"
        
        estimates = {
            'scene_analysis': self.estimate_operation_cost('analyze_scene', scene_text),
            'dialogue_enhancement': self.estimate_operation_cost('dialogue_enhancement', scene_text),
            'character_development': self.estimate_operation_cost('character_development', scene_text, 'short'),
            'pacing_analysis': self.estimate_operation_cost('style_analysis', scene_text),
        }
        
        estimates['total_scene_operations'] = sum(estimates.values())
        
        return estimates
    
    def calculate_actual_usage(self, input_tokens: int, output_tokens: int, 
                             model: str = 'claude-3-5-sonnet-20241022') -> Dict:
        """
        Calculate actual token usage and cost
        
        Args:
            input_tokens: Actual input tokens used
            output_tokens: Actual output tokens used
            model: Claude model used
        
        Returns:
            Dictionary with usage statistics and costs
        """
        if model not in self.model_limits:
            logger.warning(f"Unknown model: {model}")
            model = 'claude-3-5-sonnet-20241022'  # Default
        
        model_config = self.model_limits[model]
        
        # Calculate costs (in dollars)
        input_cost = (input_tokens / 1_000_000) * model_config['input_cost']
        output_cost = (output_tokens / 1_000_000) * model_config['output_cost']
        total_cost = input_cost + output_cost
        
        # Convert to our internal token units (simplified: 1 token = 1 unit)
        total_tokens = input_tokens + output_tokens
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'input_cost_usd': round(input_cost, 6),
            'output_cost_usd': round(output_cost, 6),
            'total_cost_usd': round(total_cost, 6),
            'model': model
        }
    
    def check_operation_feasibility(self, operation_type: str, input_text: str, 
                                  user_tokens_remaining: int, target_length: str = 'medium') -> Dict:
        """
        Check if user can afford an operation and provide recommendations
        
        Args:
            operation_type: Type of AI operation
            input_text: Input text for the operation
            user_tokens_remaining: User's remaining token balance
            target_length: Expected output length
        
        Returns:
            Dictionary with feasibility analysis and recommendations
        """
        estimated_cost = self.estimate_operation_cost(operation_type, input_text, target_length)
        
        can_afford = user_tokens_remaining >= estimated_cost
        
        result = {
            'can_afford': can_afford,
            'estimated_cost': estimated_cost,
            'tokens_remaining': user_tokens_remaining,
            'tokens_after': user_tokens_remaining - estimated_cost if can_afford else user_tokens_remaining
        }
        
        if not can_afford:
            result['shortage'] = estimated_cost - user_tokens_remaining
            result['recommendations'] = self._get_token_recommendations(estimated_cost, user_tokens_remaining)
        
        return result
    
    def _get_token_recommendations(self, needed_tokens: int, available_tokens: int) -> List[str]:
        """Generate recommendations for users who need more tokens"""
        shortage = needed_tokens - available_tokens
        recommendations = []
        
        if shortage <= 500:
            recommendations.append("Consider upgrading to Pro plan for more tokens")
        elif shortage <= 2000:
            recommendations.append("Upgrade to Pro plan or purchase additional tokens")
        else:
            recommendations.append("Consider Enterprise plan for high-volume usage")
        
        # Suggest alternative operations
        recommendations.append("Try shorter analysis operations to use fewer tokens")
        recommendations.append("Break large content into smaller sections")
        
        return recommendations
    
    def get_operation_info(self, operation_type: str) -> Dict:
        """
        Get detailed information about an operation type
        
        Args:
            operation_type: Type of operation to get info for
        
        Returns:
            Dictionary with operation details
        """
        if operation_type not in self.operation_costs:
            return {
                'exists': False,
                'message': f"Unknown operation type: {operation_type}"
            }
        
        config = self.operation_costs[operation_type]
        
        return {
            'exists': True,
            'operation_type': operation_type,
            'base_cost': config['base_cost'],
            'variable_cost_per_100_chars': config['per_100_chars'],
            'output_multiplier': config['output_multiplier'],
            'description': self._get_operation_description(operation_type),
            'typical_use_cases': self._get_operation_use_cases(operation_type)
        }
    
    def _get_operation_description(self, operation_type: str) -> str:
        """Get human-readable description of operation"""
        descriptions = {
            'analyze_idea': 'Analyze a story idea for potential, themes, and development suggestions',
            'create_project_from_idea': 'Create a full project structure from a basic story idea',
            'analyze_structure': 'Analyze story structure, pacing, and narrative flow',
            'suggest_scenes': 'Generate scene suggestions and story outline',
            'generate_story': 'Generate complete story content from scenes and outline',
            'analyze_scene': 'Analyze individual scene for content, pacing, and effectiveness',
            'character_development': 'Provide character development suggestions and analysis',
            'plot_suggestions': 'Generate plot ideas and story advancement suggestions',
            'dialogue_enhancement': 'Improve dialogue quality and character voice',
            'style_analysis': 'Analyze writing style, tone, and literary techniques'
        }
        
        return descriptions.get(operation_type, 'AI-powered content analysis and generation')
    
    def _get_operation_use_cases(self, operation_type: str) -> List[str]:
        """Get typical use cases for operation"""
        use_cases = {
            'analyze_idea': [
                'Initial story concept evaluation',
                'Theme identification',
                'Market potential assessment'
            ],
            'create_project_from_idea': [
                'Quick project setup',
                'Story structure generation',
                'Character and setting creation'
            ],
            'analyze_structure': [
                'Story pacing analysis',
                'Plot hole identification',
                'Narrative flow improvement'
            ],
            'suggest_scenes': [
                'Scene planning',
                'Story outline development',
                'Plot point identification'
            ],
            'generate_story': [
                'First draft creation',
                'Story completion',
                'Content generation from outline'
            ]
        }
        
        return use_cases.get(operation_type, ['General AI assistance'])
    
    def get_all_operations(self) -> List[str]:
        """Get list of all supported operation types"""
        return list(self.operation_costs.keys())