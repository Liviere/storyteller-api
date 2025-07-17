"""
LLM Router

API endpoints for Large Language Model operations.
Provides endpoints for story generation, analysis, and other LLM-powered features.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..llm.services import get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


# Request/Response Models
class StoryGenerationRequest(BaseModel):
    """Request model for story generation"""
    prompt: str = Field(..., min_length=10, max_length=2000, description="Story prompt or theme")
    genre: str = Field(default="fiction", description="Literary genre")
    length: str = Field(default="short", description="Story length (short, medium, long)")
    style: str = Field(default="engaging", description="Writing style")
    model_name: Optional[str] = Field(default=None, description="Specific model to use")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: Optional[int] = Field(default=None, ge=100, le=4096, description="Maximum tokens")


class StoryGenerationResponse(BaseModel):
    """Response model for story generation"""
    story: str
    metadata: Dict[str, Any]
    success: bool = True


class StoryAnalysisRequest(BaseModel):
    """Request model for story analysis"""
    content: str = Field(..., min_length=50, max_length=10000, description="Story content to analyze")
    analysis_type: str = Field(default="full", description="Type of analysis (sentiment, genre, full)")
    model_name: Optional[str] = Field(default=None, description="Specific model to use")


class StoryAnalysisResponse(BaseModel):
    """Response model for story analysis"""
    analysis: str
    analysis_type: str
    metadata: Dict[str, Any]
    success: bool = True


class StorySummaryRequest(BaseModel):
    """Request model for story summarization"""
    content: str = Field(..., min_length=100, max_length=20000, description="Story content to summarize")
    summary_length: str = Field(default="brief", description="Length of summary (brief, detailed)")
    focus: str = Field(default="main plot and characters", description="What to focus on in summary")
    model_name: Optional[str] = Field(default=None, description="Specific model to use")


class StorySummaryResponse(BaseModel):
    """Response model for story summarization"""
    summary: str
    metadata: Dict[str, Any]
    success: bool = True


class StoryImprovementRequest(BaseModel):
    """Request model for story improvement"""
    content: str = Field(..., min_length=50, max_length=15000, description="Story content to improve")
    improvement_type: str = Field(default="general", description="Type of improvement (general, grammar, style)")
    focus_area: str = Field(default="overall quality", description="Specific area to focus on")
    target_audience: str = Field(default="general readers", description="Target audience")
    target_style: Optional[str] = Field(default=None, description="Target style for style transformation")
    model_name: Optional[str] = Field(default=None, description="Specific model to use")


class StoryImprovementResponse(BaseModel):
    """Response model for story improvement"""
    improved_story: str
    original_story: str
    metadata: Dict[str, Any]
    success: bool = True


class ModelsListResponse(BaseModel):
    """Response model for available models list"""
    models: Dict[str, bool]
    success: bool = True


class LLMStatsResponse(BaseModel):
    """Response model for LLM usage statistics"""
    stats: Dict[str, Any]
    success: bool = True


# Dependency to get LLM service
def get_llm_service_dependency():
    """Dependency to get LLM service instance"""
    return get_llm_service()


###################################
#            Endpoints            #
###################################

@router.post("/generate", response_model=StoryGenerationResponse)
async def generate_story(
    request: StoryGenerationRequest,
    llm_service = Depends(get_llm_service_dependency)
):
    """
    Generate a new story based on prompt and parameters.
    
    This endpoint creates an original story using AI models based on the provided
    prompt, genre, and style preferences.
    """
    try:
        # Extract model parameters
        model_params = {}
        if request.temperature is not None:
            model_params["temperature"] = request.temperature
        if request.max_tokens is not None:
            model_params["max_tokens"] = request.max_tokens
        
        # Generate story
        result = await llm_service.generate_story(
            prompt=request.prompt,
            genre=request.genre,
            length=request.length,
            style=request.style,
            model_name=request.model_name,
            **model_params
        )
        
        return StoryGenerationResponse(
            story=result["story"],
            metadata=result["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Story generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Story generation failed: {str(e)}"
        )


@router.post("/analyze", response_model=StoryAnalysisResponse)
async def analyze_story(
    request: StoryAnalysisRequest,
    llm_service = Depends(get_llm_service_dependency)
):
    """
    Analyze story content for various aspects.
    
    Provides sentiment analysis, genre classification, or comprehensive story analysis.
    """
    try:
        # Validate analysis type
        valid_types = ["sentiment", "genre", "full"]
        if request.analysis_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid analysis type. Must be one of: {valid_types}"
            )
        
        # Analyze story
        result = await llm_service.analyze_story(
            content=request.content,
            analysis_type=request.analysis_type,
            model_name=request.model_name
        )
        
        return StoryAnalysisResponse(
            analysis=result["analysis"],
            analysis_type=result["analysis_type"],
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Story analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Story analysis failed: {str(e)}"
        )


@router.post("/summarize", response_model=StorySummaryResponse)
async def summarize_story(
    request: StorySummaryRequest,
    llm_service = Depends(get_llm_service_dependency)
):
    """
    Create a summary of story content.
    
    Generates concise summaries focusing on main plot points and characters.
    """
    try:
        # Validate summary length
        valid_lengths = ["brief", "detailed"]
        if request.summary_length not in valid_lengths:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid summary length. Must be one of: {valid_lengths}"
            )
        
        # Summarize story
        result = await llm_service.summarize_story(
            content=request.content,
            summary_length=request.summary_length,
            focus=request.focus,
            model_name=request.model_name
        )
        
        return StorySummaryResponse(
            summary=result["summary"],
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Story summarization failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Story summarization failed: {str(e)}"
        )


@router.post("/improve", response_model=StoryImprovementResponse)
async def improve_story(
    request: StoryImprovementRequest,
    llm_service = Depends(get_llm_service_dependency)
):
    """
    Improve story content.
    
    Enhances stories through grammar correction, style transformation, 
    or general quality improvements.
    """
    try:
        # Validate improvement type
        valid_types = ["general", "grammar", "style"]
        if request.improvement_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid improvement type. Must be one of: {valid_types}"
            )
        
        # Prepare additional parameters for style transformation
        kwargs = {}
        if request.improvement_type == "style" and request.target_style:
            kwargs["target_style"] = request.target_style
        
        # Improve story
        result = await llm_service.improve_story(
            content=request.content,
            improvement_type=request.improvement_type,
            focus_area=request.focus_area,
            target_audience=request.target_audience,
            model_name=request.model_name,
            **kwargs
        )
        
        return StoryImprovementResponse(
            improved_story=result["improved_story"],
            original_story=result["original_story"],
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Story improvement failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Story improvement failed: {str(e)}"
        )


@router.get("/models", response_model=ModelsListResponse)
async def list_available_models(
    llm_service = Depends(get_llm_service_dependency)
):
    """
    Get list of available LLM models.
    
    Returns all configured models and their availability status.
    """
    try:
        models = llm_service.get_available_models()
        return ModelsListResponse(models=models)
        
    except Exception as e:
        logger.error(f"Failed to get available models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available models: {str(e)}"
        )


@router.get("/stats", response_model=LLMStatsResponse)
async def get_llm_statistics(
    llm_service = Depends(get_llm_service_dependency)
):
    """
    Get LLM usage statistics.
    
    Returns usage metrics including request counts, tokens used, and error rates.
    """
    try:
        stats = llm_service.get_usage_stats()
        return LLMStatsResponse(stats=stats)
        
    except Exception as e:
        logger.error(f"Failed to get LLM statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get LLM statistics: {str(e)}"
        )


@router.get("/health")
async def health_check(
    llm_service = Depends(get_llm_service_dependency)
):
    """
    Health check endpoint for LLM services.
    
    Verifies that LLM services are operational and models are accessible.
    """
    try:
        models = llm_service.get_available_models()
        available_count = sum(1 for available in models.values() if available)
        total_count = len(models)
        
        return {
            "status": "healthy" if available_count > 0 else "degraded",
            "available_models": available_count,
            "total_models": total_count,
            "models": models
        }
        
    except Exception as e:
        logger.error(f"LLM health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "available_models": 0,
            "total_models": 0
        }
