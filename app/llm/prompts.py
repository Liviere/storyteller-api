"""
LLM Prompts Templates

Contains predefined prompt templates for various story-related tasks.
Uses LangChain's PromptTemplate for consistent and reusable prompts.
"""

from typing import Any, Dict, cast

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


class StoryPrompts:
    """Collection of prompt templates for story-related tasks"""

    ###################################
    #    Story Generation Prompts     #
    ###################################

    STORY_GENERATION = PromptTemplate(
        input_variables=["genre", "theme", "length", "style", "additional_params"],
        template="""You are a creative storyteller. Write an engaging {length} story in the {genre} genre.

Theme: {theme}
Style: {style}
Additional requirements: {additional_params}

Create a compelling narrative with:
- Interesting characters
- Clear plot structure
- Engaging dialogue
- Vivid descriptions
- Appropriate pacing for the genre

Story:""",
    )

    STORY_CONTINUATION = PromptTemplate(
        input_variables=["existing_story", "direction", "length"],
        template="""Continue the following story in a natural and engaging way.

Existing story:
{existing_story}

Direction for continuation: {direction}
Target length: {length}

Continue the story maintaining the same tone, style, and character consistency:""",
    )

    ###################################
    #        Analysis Prompts         #
    ###################################

    SENTIMENT_ANALYSIS = PromptTemplate(
        input_variables=["content"],
        template="""Analyze the emotional tone and sentiment of the following story content.

Content:
{content}

Provide analysis in the following format:
- Overall Sentiment: [Positive/Negative/Neutral/Mixed]
- Emotional Tone: [describe the predominant emotions]
- Mood: [describe the general mood/atmosphere]
- Intensity: [Low/Medium/High]
- Key Emotional Elements: [list main emotional themes]

Analysis:""",
    )

    GENRE_CLASSIFICATION = PromptTemplate(
        input_variables=["content"],
        template="""Analyze the following story content and classify its literary genre.

Content:
{content}

Choose the most appropriate primary genre from: Fantasy, Science Fiction, Mystery, Romance, Horror, Thriller, Historical Fiction, Contemporary Fiction, Young Adult, Children's Literature, Comedy, Drama, Adventure, Biography, Non-fiction.

Also identify any secondary genres or subgenres that apply.

Classification:
Primary Genre: 
Secondary Genres: 
Confidence Level: 
Reasoning:""",
    )

    STORY_ANALYSIS = PromptTemplate(
        input_variables=["content"],
        template="""Provide a comprehensive analysis of the following story.

Story:
{content}

Analyze the following aspects:
1. Plot Structure: Beginning, middle, end, conflicts, resolution
2. Characters: Main characters, development, relationships
3. Setting: Time, place, atmosphere
4. Themes: Main themes and messages
5. Writing Style: Narrative voice, tone, literary devices
6. Strengths: What works well in the story
7. Areas for Improvement: Suggestions for enhancement

Analysis:""",
    )

    ###################################
    #       Improvement Prompts       #
    ###################################

    STORY_IMPROVEMENT = PromptTemplate(
        input_variables=["content", "focus_area", "target_audience"],
        template="""Improve the following story focusing on: {focus_area}

Original Story:
{content}

Target Audience: {target_audience}

Rewrite the story with improvements in:
- {focus_area}
- Overall readability and engagement
- Character development and dialogue
- Plot pacing and structure
- Descriptive language and imagery

Improved Story:""",
    )

    GRAMMAR_CORRECTION = PromptTemplate(
        input_variables=["content"],
        template="""Correct any grammar, spelling, and punctuation errors in the following text while preserving the original meaning and style.

Original text:
{content}

Corrected text:""",
    )

    STYLE_TRANSFORMATION = PromptTemplate(
        input_variables=["content", "target_style", "preserve_elements"],
        template="""Transform the following story to match the {target_style} writing style.

Original Story:
{content}

Target Style: {target_style}
Elements to preserve: {preserve_elements}

Rewrite the story in the new style while maintaining the core plot and characters:""",
    )

    ###################################
    #         Summary Prompts         #
    ###################################

    STORY_SUMMARY = PromptTemplate(
        input_variables=["content", "summary_length", "focus"],
        template="""Create a {summary_length} summary of the following story.

Story:
{content}

Focus on: {focus}

Include the main plot points, key characters, and central themes. Make it engaging and informative.

Summary:""",
    )

    CHARACTER_SUMMARY = PromptTemplate(
        input_variables=["content", "character_name"],
        template="""Create a character profile for {character_name} based on the following story.

Story:
{content}

Character Profile for {character_name}:
- Physical Description:
- Personality Traits:
- Role in Story:
- Character Arc:
- Key Relationships:
- Notable Quotes or Actions:""",
    )

    ####################################
    #        Translation Prompts       #
    ####################################

    STORY_TRANSLATION = PromptTemplate(
        input_variables=["content", "target_language", "preserve_style"],
        template="""Translate the following story to {target_language}.

Original Story:
{content}

Translation requirements:
- Preserve the narrative style and tone
- Maintain cultural context where appropriate
- Keep character names unless culturally adapted versions exist
- Preserve literary devices and wordplay where possible
- Style preservation: {preserve_style}

Translated Story:""",
    )

    ####################################
    #         Creative Prompts         #
    ####################################

    STORY_ALTERNATIVE_ENDING = PromptTemplate(
        input_variables=["content", "ending_type", "tone"],
        template="""Create an alternative {ending_type} ending for the following story.

Original Story:
{content}

New ending should be:
- {ending_type} in nature
- {tone} in tone
- Consistent with the established characters and world
- Satisfying and well-resolved

Alternative Ending:""",
    )

    CHARACTER_DIALOGUE = PromptTemplate(
        input_variables=[
            "character_name",
            "character_traits",
            "situation",
            "other_character",
        ],
        template="""Write dialogue for {character_name} in the following situation.

Character: {character_name}
Character Traits: {character_traits}
Situation: {situation}
Speaking to: {other_character}

Write natural, character-appropriate dialogue that reveals personality and advances the scene:""",
    )


class ChatPrompts:
    """Chat-based prompt templates for conversational interactions"""

    STORY_CONSULTANT = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a professional story consultant and creative writing mentor. 
        You help writers develop their stories by providing constructive feedback, 
        creative suggestions, and technical guidance. You are encouraging, insightful, 
        and always aim to help improve the writer's craft.""",
            ),
            ("human", "{user_input}"),
        ]
    )

    GENRE_EXPERT = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert in literary genres with deep knowledge of 
        genre conventions, reader expectations, and market trends. You help writers 
        understand and effectively use genre elements in their stories.""",
            ),
            ("human", "{user_input}"),
        ]
    )


def get_prompt_template(prompt_name: str) -> PromptTemplate:
    """
    Get a prompt template by name

    Args:
        prompt_name: Name of the prompt template

    Returns:
        PromptTemplate instance

    Raises:
        AttributeError: If prompt template doesn't exist
    """
    return cast(PromptTemplate, getattr(StoryPrompts, prompt_name.upper()))


def get_chat_prompt_template(prompt_name: str) -> ChatPromptTemplate:
    """
    Get a chat prompt template by name

    Args:
        prompt_name: Name of the chat prompt template

    Returns:
        ChatPromptTemplate instance

    Raises:
        AttributeError: If chat prompt template doesn't exist
    """
    return cast(ChatPromptTemplate, getattr(ChatPrompts, prompt_name.upper()))


# Available prompt templates
AVAILABLE_PROMPTS = {
    "story_generation": StoryPrompts.STORY_GENERATION,
    "story_continuation": StoryPrompts.STORY_CONTINUATION,
    "sentiment_analysis": StoryPrompts.SENTIMENT_ANALYSIS,
    "genre_classification": StoryPrompts.GENRE_CLASSIFICATION,
    "story_analysis": StoryPrompts.STORY_ANALYSIS,
    "story_improvement": StoryPrompts.STORY_IMPROVEMENT,
    "grammar_correction": StoryPrompts.GRAMMAR_CORRECTION,
    "style_transformation": StoryPrompts.STYLE_TRANSFORMATION,
    "story_summary": StoryPrompts.STORY_SUMMARY,
    "character_summary": StoryPrompts.CHARACTER_SUMMARY,
    "story_translation": StoryPrompts.STORY_TRANSLATION,
    "story_alternative_ending": StoryPrompts.STORY_ALTERNATIVE_ENDING,
    "character_dialogue": StoryPrompts.CHARACTER_DIALOGUE,
}

AVAILABLE_CHAT_PROMPTS = {
    "story_consultant": ChatPrompts.STORY_CONSULTANT,
    "genre_expert": ChatPrompts.GENRE_EXPERT,
}
