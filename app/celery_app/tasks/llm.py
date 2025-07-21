"""
Celery tasks for LLM operations
"""

import asyncio
from typing import Dict, Any, Optional
from app.celery_app.celery import celery_app
from app.llm.services import get_llm_service


@celery_app.task(bind=True, name="llm.generate_story", queue="llm")
def generate_story_task(
    self,
    prompt: str,
    genre: str = "fiction",
    length: str = "short",
    style: str = "engaging",
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate a story asynchronously
    
    Args:
        prompt: Story prompt or theme
        genre: Literary genre
        length: Story length (short, medium, long)
        style: Writing style
        model_name: Specific model to use
        temperature: Model temperature
        max_tokens: Maximum tokens
        
    Returns:
        Dictionary with generated story and metadata
    """
    try:
        llm_service = get_llm_service()
        
        # Extract model parameters
        model_params = {}
        if temperature is not None:
            model_params["temperature"] = temperature
        if max_tokens is not None:
            model_params["max_tokens"] = max_tokens

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                llm_service.generate_story(
                    prompt=prompt,
                    genre=genre,
                    length=length,
                    style=style,
                    model_name=model_name,
                    **model_params,
                )
            )
        finally:
            loop.close()

        return {
            "story": result["story"],
            "metadata": result["metadata"],
            "success": True
        }

    except Exception as exc:
        print(f"Story generation failed: {str(exc)}")
        self.retry(countdown=60, max_retries=2, exc=exc)


@celery_app.task(bind=True, name="llm.analyze_story", queue="llm")
def analyze_story_task(
    self,
    content: str,
    analysis_type: str = "full",
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze story content asynchronously
    
    Args:
        content: Story content to analyze
        analysis_type: Type of analysis (sentiment, genre, full)
        model_name: Specific model to use
        
    Returns:
        Dictionary with analysis results and metadata
    """
    try:
        # Validate analysis type
        valid_types = ["sentiment", "genre", "full"]
        if analysis_type not in valid_types:
            raise ValueError(f"Invalid analysis type. Must be one of: {valid_types}")

        llm_service = get_llm_service()

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                llm_service.analyze_story(
                    content=content,
                    analysis_type=analysis_type,
                    model_name=model_name,
                )
            )
        finally:
            loop.close()

        return {
            "analysis": result["analysis"],
            "analysis_type": result["analysis_type"],
            "metadata": result["metadata"],
            "success": True
        }

    except Exception as exc:
        print(f"Story analysis failed: {str(exc)}")
        self.retry(countdown=60, max_retries=2, exc=exc)


@celery_app.task(bind=True, name="llm.summarize_story", queue="llm")
def summarize_story_task(
    self,
    content: str,
    summary_length: str = "brief",
    focus: str = "main plot and characters",
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Summarize story content asynchronously
    
    Args:
        content: Story content to summarize
        summary_length: Length of summary (brief, detailed)
        focus: What to focus on in summary
        model_name: Specific model to use
        
    Returns:
        Dictionary with summary and metadata
    """
    try:
        # Validate summary length
        valid_lengths = ["brief", "detailed"]
        if summary_length not in valid_lengths:
            raise ValueError(f"Invalid summary length. Must be one of: {valid_lengths}")

        llm_service = get_llm_service()

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                llm_service.summarize_story(
                    content=content,
                    summary_length=summary_length,
                    focus=focus,
                    model_name=model_name,
                )
            )
        finally:
            loop.close()

        return {
            "summary": result["summary"],
            "metadata": result["metadata"],
            "success": True
        }

    except Exception as exc:
        print(f"Story summarization failed: {str(exc)}")
        self.retry(countdown=60, max_retries=2, exc=exc)


@celery_app.task(bind=True, name="llm.improve_story", queue="llm")
def improve_story_task(
    self,
    content: str,
    improvement_type: str = "general",
    focus_area: str = "overall quality",
    target_audience: str = "general readers",
    target_style: Optional[str] = None,
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Improve story content asynchronously
    
    Args:
        content: Story content to improve
        improvement_type: Type of improvement (general, grammar, style)
        focus_area: Specific area to focus on
        target_audience: Target audience
        target_style: Target style for style transformation
        model_name: Specific model to use
        
    Returns:
        Dictionary with improved story and metadata
    """
    try:
        # Validate improvement type
        valid_types = ["general", "grammar", "style"]
        if improvement_type not in valid_types:
            raise ValueError(f"Invalid improvement type. Must be one of: {valid_types}")

        llm_service = get_llm_service()

        # Prepare additional parameters for style transformation
        kwargs = {}
        if improvement_type == "style" and target_style:
            kwargs["target_style"] = target_style

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                llm_service.improve_story(
                    content=content,
                    improvement_type=improvement_type,
                    focus_area=focus_area,
                    target_audience=target_audience,
                    model_name=model_name,
                    **kwargs,
                )
            )
        finally:
            loop.close()

        return {
            "improved_story": result["improved_story"],
            "original_story": result["original_story"],
            "metadata": result["metadata"],
            "success": True
        }

    except Exception as exc:
        print(f"Story improvement failed: {str(exc)}")
        self.retry(countdown=60, max_retries=2, exc=exc)
