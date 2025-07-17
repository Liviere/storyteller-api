"""
LangChain Chains for Story Processing

Contains predefined chains for common story-related tasks.
Each chain combines prompts with models for specific functionality.
"""

import logging
from typing import Optional
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel

from .prompts import AVAILABLE_PROMPTS
from .models import get_model_factory

logger = logging.getLogger(__name__)


class BaseStoryChain:
    """Base class for story processing chains"""
    
    def __init__(self, model_name: Optional[str] = None, **model_params):
        self.model_factory = get_model_factory()
        self.model_name = model_name
        self.model_params = model_params
        self._chain = None
    
    def _get_model(self, task: str) -> BaseChatModel:
        """Get model for the chain"""
        if self.model_name:
            model = self.model_factory.create_model(self.model_name, **self.model_params)
        else:
            model = self.model_factory.get_model_for_task(task, **self.model_params)
        
        if not model:
            raise ValueError(f"Could not create model for task: {task}")
        return model
    
    async def arun(self, **kwargs) -> str:
        """Run the chain asynchronously"""
        if not self._chain:
            raise NotImplementedError("Chain not implemented")
        
        try:
            result = await self._chain.ainvoke(kwargs)
            return result
        except Exception as e:
            logger.error(f"Chain execution failed: {str(e)}")
            raise


class StoryGenerationChain(BaseStoryChain):
    """Chain for generating stories"""
    
    def __init__(self, model_name: Optional[str] = None, **model_params):
        super().__init__(model_name, **model_params)
        self._build_chain()
    
    def _build_chain(self):
        """Build the story generation chain"""
        model = self._get_model("story_generation")
        prompt = AVAILABLE_PROMPTS["story_generation"]
        
        self._chain = (
            prompt 
            | model 
            | StrOutputParser()
        )
    
    async def generate_story(
        self, 
        genre: str, 
        theme: str, 
        length: str = "short",
        style: str = "engaging",
        additional_params: str = "none"
    ) -> str:
        """Generate a story based on parameters"""
        return await self.arun(
            genre=genre,
            theme=theme,
            length=length,
            style=style,
            additional_params=additional_params
        )


class StoryAnalysisChain(BaseStoryChain):
    """Chain for analyzing stories"""
    
    def __init__(self, model_name: Optional[str] = None, **model_params):
        super().__init__(model_name, **model_params)
        self._build_chains()
    
    def _build_chains(self):
        """Build analysis chains"""
        model = self._get_model("analysis")
        
        # Sentiment analysis chain
        self._sentiment_chain = (
            AVAILABLE_PROMPTS["sentiment_analysis"] 
            | model 
            | StrOutputParser()
        )
        
        # Genre classification chain
        self._genre_chain = (
            AVAILABLE_PROMPTS["genre_classification"] 
            | model 
            | StrOutputParser()
        )
        
        # Full story analysis chain
        self._analysis_chain = (
            AVAILABLE_PROMPTS["story_analysis"] 
            | model 
            | StrOutputParser()
        )
    
    async def analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of story content"""
        return await self._sentiment_chain.ainvoke({"content": content})
    
    async def classify_genre(self, content: str) -> str:
        """Classify genre of story content"""
        return await self._genre_chain.ainvoke({"content": content})
    
    async def analyze_story(self, content: str) -> str:
        """Perform comprehensive story analysis"""
        return await self._analysis_chain.ainvoke({"content": content})


class StorySummaryChain(BaseStoryChain):
    """Chain for creating story summaries"""
    
    def __init__(self, model_name: Optional[str] = None, **model_params):
        super().__init__(model_name, **model_params)
        self._build_chain()
    
    def _build_chain(self):
        """Build the summary chain"""
        model = self._get_model("summarization")
        prompt = AVAILABLE_PROMPTS["story_summary"]
        
        self._chain = (
            prompt 
            | model 
            | StrOutputParser()
        )
    
    async def summarize_story(
        self, 
        content: str, 
        summary_length: str = "brief",
        focus: str = "main plot and characters"
    ) -> str:
        """Create a story summary"""
        return await self.arun(
            content=content,
            summary_length=summary_length,
            focus=focus
        )


class StoryImprovementChain(BaseStoryChain):
    """Chain for improving stories"""
    
    def __init__(self, model_name: Optional[str] = None, **model_params):
        super().__init__(model_name, **model_params)
        self._build_chains()
    
    def _build_chains(self):
        """Build improvement chains"""
        model = self._get_model("improvement")
        
        # General improvement chain
        self._improvement_chain = (
            AVAILABLE_PROMPTS["story_improvement"] 
            | model 
            | StrOutputParser()
        )
        
        # Grammar correction chain
        self._grammar_chain = (
            AVAILABLE_PROMPTS["grammar_correction"] 
            | model 
            | StrOutputParser()
        )
        
        # Style transformation chain
        self._style_chain = (
            AVAILABLE_PROMPTS["style_transformation"] 
            | model 
            | StrOutputParser()
        )
    
    async def improve_story(
        self, 
        content: str, 
        focus_area: str = "overall quality",
        target_audience: str = "general readers"
    ) -> str:
        """Improve a story"""
        return await self._improvement_chain.ainvoke({
            "content": content,
            "focus_area": focus_area,
            "target_audience": target_audience
        })
    
    async def correct_grammar(self, content: str) -> str:
        """Correct grammar and spelling"""
        return await self._grammar_chain.ainvoke({"content": content})
    
    async def transform_style(
        self, 
        content: str, 
        target_style: str,
        preserve_elements: str = "plot and characters"
    ) -> str:
        """Transform writing style"""
        return await self._style_chain.ainvoke({
            "content": content,
            "target_style": target_style,
            "preserve_elements": preserve_elements
        })


class StoryTranslationChain(BaseStoryChain):
    """Chain for translating stories"""
    
    def __init__(self, model_name: Optional[str] = None, **model_params):
        super().__init__(model_name, **model_params)
        self._build_chain()
    
    def _build_chain(self):
        """Build the translation chain"""
        model = self._get_model("translation")
        prompt = AVAILABLE_PROMPTS["story_translation"]
        
        self._chain = (
            prompt 
            | model 
            | StrOutputParser()
        )
    
    async def translate_story(
        self, 
        content: str, 
        target_language: str,
        preserve_style: str = "maintain original tone and style"
    ) -> str:
        """Translate a story to target language"""
        return await self.arun(
            content=content,
            target_language=target_language,
            preserve_style=preserve_style
        )


class StoryCreativeChain(BaseStoryChain):
    """Chain for creative story operations"""
    
    def __init__(self, model_name: Optional[str] = None, **model_params):
        super().__init__(model_name, **model_params)
        self._build_chains()
    
    def _build_chains(self):
        """Build creative chains"""
        model = self._get_model("story_generation")
        
        # Alternative ending chain
        self._ending_chain = (
            AVAILABLE_PROMPTS["story_alternative_ending"] 
            | model 
            | StrOutputParser()
        )
        
        # Character dialogue chain
        self._dialogue_chain = (
            AVAILABLE_PROMPTS["character_dialogue"] 
            | model 
            | StrOutputParser()
        )
        
        # Story continuation chain
        self._continuation_chain = (
            AVAILABLE_PROMPTS["story_continuation"] 
            | model 
            | StrOutputParser()
        )
    
    async def create_alternative_ending(
        self, 
        content: str, 
        ending_type: str = "happy",
        tone: str = "uplifting"
    ) -> str:
        """Create an alternative ending"""
        return await self._ending_chain.ainvoke({
            "content": content,
            "ending_type": ending_type,
            "tone": tone
        })
    
    async def generate_dialogue(
        self, 
        character_name: str, 
        character_traits: str,
        situation: str,
        other_character: str = "another person"
    ) -> str:
        """Generate character dialogue"""
        return await self._dialogue_chain.ainvoke({
            "character_name": character_name,
            "character_traits": character_traits,
            "situation": situation,
            "other_character": other_character
        })
    
    async def continue_story(
        self, 
        existing_story: str, 
        direction: str = "natural progression",
        length: str = "medium"
    ) -> str:
        """Continue an existing story"""
        return await self._continuation_chain.ainvoke({
            "existing_story": existing_story,
            "direction": direction,
            "length": length
        })


# Chain factory functions
def create_story_generation_chain(model_name: Optional[str] = None, **model_params) -> StoryGenerationChain:
    """Create a story generation chain"""
    return StoryGenerationChain(model_name, **model_params)


def create_story_analysis_chain(model_name: Optional[str] = None, **model_params) -> StoryAnalysisChain:
    """Create a story analysis chain"""
    return StoryAnalysisChain(model_name, **model_params)


def create_story_summary_chain(model_name: Optional[str] = None, **model_params) -> StorySummaryChain:
    """Create a story summary chain"""
    return StorySummaryChain(model_name, **model_params)


def create_story_improvement_chain(model_name: Optional[str] = None, **model_params) -> StoryImprovementChain:
    """Create a story improvement chain"""
    return StoryImprovementChain(model_name, **model_params)


def create_story_translation_chain(model_name: Optional[str] = None, **model_params) -> StoryTranslationChain:
    """Create a story translation chain"""
    return StoryTranslationChain(model_name, **model_params)


def create_story_creative_chain(model_name: Optional[str] = None, **model_params) -> StoryCreativeChain:
    """Create a story creative chain"""
    return StoryCreativeChain(model_name, **model_params)
