"""
LLM Service Module

Main service class that provides high-level interface for all LLM operations.
This is the primary entry point for the API to interact with LLM capabilities.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from .chains import (
    create_story_generation_chain,
    create_story_analysis_chain,
    create_story_summary_chain,
    create_story_improvement_chain,
    create_story_translation_chain,
    create_story_creative_chain
)
from .config import llm_config
from .models import get_model_factory

logger = logging.getLogger(__name__)


class LLMService:
    """
    Main LLM Service providing high-level interface for story-related AI operations.
    
    This service handles:
    - Story generation and continuation
    - Content analysis and categorization
    - Sentiment analysis
    - Story improvement and style transformation
    - Translation and summarization
    - Creative operations (alternative endings, dialogue)
    """
    
    def __init__(self):
        self.config = llm_config
        self.model_factory = get_model_factory()
        self._usage_stats = {
            "requests_count": 0,
            "total_tokens": 0,
            "errors_count": 0,
            "last_request": None
        }
    
    async def generate_story(
        self,
        prompt: str,
        genre: str = "fiction",
        length: str = "short",
        style: str = "engaging",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a new story based on prompt and parameters.
        
        Args:
            prompt: The story prompt or theme
            genre: Literary genre (fantasy, sci-fi, mystery, etc.)
            length: Story length (short, medium, long)
            style: Writing style (engaging, descriptive, dialogue-heavy, etc.)
            model_name: Specific model to use (optional)
            **kwargs: Additional model parameters
            
        Returns:
            Dict containing the generated story and metadata
        """
        try:
            self._log_request("generate_story", locals())
            
            chain = create_story_generation_chain(model_name, **kwargs)
            story = await chain.generate_story(
                genre=genre,
                theme=prompt,
                length=length,
                style=style,
                additional_params=json.dumps(kwargs) if kwargs else "none"
            )
            
            result = {
                "story": story,
                "metadata": {
                    "genre": genre,
                    "length": length,
                    "style": style,
                    "model_used": model_name or self.config.get_task_model("story_generation"),
                    "generation_time": datetime.utcnow().isoformat(),
                    "word_count": len(story.split()) if story else 0
                }
            }
            
            self._update_usage_stats(success=True)
            return result
            
        except Exception as e:
            self._handle_error("generate_story", e)
            raise
    
    async def analyze_story(
        self,
        content: str,
        analysis_type: str = "full",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze story content for various aspects.
        
        Args:
            content: Story content to analyze
            analysis_type: Type of analysis (sentiment, genre, full)
            model_name: Specific model to use (optional)
            **kwargs: Additional model parameters
            
        Returns:
            Dict containing analysis results
        """
        try:
            self._log_request("analyze_story", locals())
            
            chain = create_story_analysis_chain(model_name, **kwargs)
            
            if analysis_type == "sentiment":
                analysis = await chain.analyze_sentiment(content)
            elif analysis_type == "genre":
                analysis = await chain.classify_genre(content)
            elif analysis_type == "full":
                analysis = await chain.analyze_story(content)
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
            
            result = {
                "analysis": analysis,
                "analysis_type": analysis_type,
                "metadata": {
                    "content_length": len(content),
                    "word_count": len(content.split()),
                    "model_used": model_name or self.config.get_task_model("analysis"),
                    "analysis_time": datetime.utcnow().isoformat()
                }
            }
            
            self._update_usage_stats(success=True)
            return result
            
        except Exception as e:
            self._handle_error("analyze_story", e)
            raise
    
    async def summarize_story(
        self,
        content: str,
        summary_length: str = "brief",
        focus: str = "main plot and characters",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a summary of story content.
        
        Args:
            content: Story content to summarize
            summary_length: Length of summary (brief, detailed)
            focus: What to focus on in summary
            model_name: Specific model to use (optional)
            **kwargs: Additional model parameters
            
        Returns:
            Dict containing summary and metadata
        """
        try:
            self._log_request("summarize_story", locals())
            
            chain = create_story_summary_chain(model_name, **kwargs)
            summary = await chain.summarize_story(content, summary_length, focus)
            
            result = {
                "summary": summary,
                "metadata": {
                    "original_length": len(content),
                    "original_word_count": len(content.split()),
                    "summary_word_count": len(summary.split()) if summary else 0,
                    "compression_ratio": len(summary) / len(content) if content and summary else 0,
                    "summary_length": summary_length,
                    "focus": focus,
                    "model_used": model_name or self.config.get_task_model("summarization"),
                    "summary_time": datetime.utcnow().isoformat()
                }
            }
            
            self._update_usage_stats(success=True)
            return result
            
        except Exception as e:
            self._handle_error("summarize_story", e)
            raise
    
    async def improve_story(
        self,
        content: str,
        improvement_type: str = "general",
        focus_area: str = "overall quality",
        target_audience: str = "general readers",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Improve story content.
        
        Args:
            content: Story content to improve
            improvement_type: Type of improvement (general, grammar, style)
            focus_area: Specific area to focus on
            target_audience: Target audience for improvements
            model_name: Specific model to use (optional)
            **kwargs: Additional model parameters
            
        Returns:
            Dict containing improved story and metadata
        """
        try:
            self._log_request("improve_story", locals())
            
            chain = create_story_improvement_chain(model_name, **kwargs)
            
            if improvement_type == "grammar":
                improved = await chain.correct_grammar(content)
            elif improvement_type == "style":
                style = kwargs.get("target_style", "more engaging")
                improved = await chain.transform_style(content, style)
            else:  # general improvement
                improved = await chain.improve_story(content, focus_area, target_audience)
            
            result = {
                "improved_story": improved,
                "original_story": content,
                "metadata": {
                    "improvement_type": improvement_type,
                    "focus_area": focus_area,
                    "target_audience": target_audience,
                    "original_word_count": len(content.split()),
                    "improved_word_count": len(improved.split()) if improved else 0,
                    "model_used": model_name or self.config.get_task_model("improvement"),
                    "improvement_time": datetime.utcnow().isoformat()
                }
            }
            
            self._update_usage_stats(success=True)
            return result
            
        except Exception as e:
            self._handle_error("improve_story", e)
            raise
    
    async def translate_story(
        self,
        content: str,
        target_language: str,
        preserve_style: bool = True,
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Translate story to target language.
        
        Args:
            content: Story content to translate
            target_language: Target language for translation
            preserve_style: Whether to preserve original style
            model_name: Specific model to use (optional)
            **kwargs: Additional model parameters
            
        Returns:
            Dict containing translated story and metadata
        """
        try:
            self._log_request("translate_story", locals())
            
            chain = create_story_translation_chain(model_name, **kwargs)
            preserve_text = "maintain original tone and style" if preserve_style else "adapt freely"
            
            translated = await chain.translate_story(content, target_language, preserve_text)
            
            result = {
                "translated_story": translated,
                "original_story": content,
                "metadata": {
                    "target_language": target_language,
                    "preserve_style": preserve_style,
                    "original_word_count": len(content.split()),
                    "translated_word_count": len(translated.split()) if translated else 0,
                    "model_used": model_name or self.config.get_task_model("translation"),
                    "translation_time": datetime.utcnow().isoformat()
                }
            }
            
            self._update_usage_stats(success=True)
            return result
            
        except Exception as e:
            self._handle_error("translate_story", e)
            raise
    
    async def create_alternative_ending(
        self,
        content: str,
        ending_type: str = "happy",
        tone: str = "uplifting",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an alternative ending for a story.
        
        Args:
            content: Original story content
            ending_type: Type of ending (happy, sad, twist, open)
            tone: Tone for the ending
            model_name: Specific model to use (optional)
            **kwargs: Additional model parameters
            
        Returns:
            Dict containing alternative ending and metadata
        """
        try:
            self._log_request("create_alternative_ending", locals())
            
            chain = create_story_creative_chain(model_name, **kwargs)
            ending = await chain.create_alternative_ending(content, ending_type, tone)
            
            result = {
                "alternative_ending": ending,
                "original_story": content,
                "metadata": {
                    "ending_type": ending_type,
                    "tone": tone,
                    "original_word_count": len(content.split()),
                    "ending_word_count": len(ending.split()) if ending else 0,
                    "model_used": model_name or self.config.get_task_model("story_generation"),
                    "creation_time": datetime.utcnow().isoformat()
                }
            }
            
            self._update_usage_stats(success=True)
            return result
            
        except Exception as e:
            self._handle_error("create_alternative_ending", e)
            raise
    
    async def continue_story(
        self,
        existing_story: str,
        direction: str = "natural progression",
        length: str = "medium",
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Continue an existing story.
        
        Args:
            existing_story: The story to continue
            direction: Direction for continuation
            length: Length of continuation
            model_name: Specific model to use (optional)
            **kwargs: Additional model parameters
            
        Returns:
            Dict containing story continuation and metadata
        """
        try:
            self._log_request("continue_story", locals())
            
            chain = create_story_creative_chain(model_name, **kwargs)
            continuation = await chain.continue_story(existing_story, direction, length)
            
            result = {
                "continuation": continuation,
                "original_story": existing_story,
                "metadata": {
                    "direction": direction,
                    "length": length,
                    "original_word_count": len(existing_story.split()),
                    "continuation_word_count": len(continuation.split()) if continuation else 0,
                    "model_used": model_name or self.config.get_task_model("story_generation"),
                    "continuation_time": datetime.utcnow().isoformat()
                }
            }
            
            self._update_usage_stats(success=True)
            return result
            
        except Exception as e:
            self._handle_error("continue_story", e)
            raise
    
    def get_available_models(self) -> Dict[str, bool]:
        """Get list of available models"""
        return self.model_factory.get_available_models()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self._usage_stats.copy()
    
    def _log_request(self, operation: str, params: Dict[str, Any]):
        """Log request for monitoring"""
        if self.config.enable_monitoring:
            # Remove sensitive data for logging
            safe_params = {k: v for k, v in params.items() if k not in ['self', 'kwargs']}
            logger.info(f"LLM operation: {operation}, params: {safe_params}")
    
    def _update_usage_stats(self, success: bool = True):
        """Update usage statistics"""
        self._usage_stats["requests_count"] += 1
        self._usage_stats["last_request"] = datetime.utcnow().isoformat()
        if not success:
            self._usage_stats["errors_count"] += 1
    
    def _handle_error(self, operation: str, error: Exception):
        """Handle and log errors"""
        logger.error(f"LLM operation '{operation}' failed: {str(error)}")
        self._update_usage_stats(success=False)


# Global service instance
llm_service = LLMService()


def get_llm_service() -> LLMService:
    """Get global LLM service instance"""
    return llm_service
