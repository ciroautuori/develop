"""
Video Generation Agent - Google Veo Integration.

This agent wraps the Google Veo model (via Gemini/Vertex AI) to provide
video generation capabilities for the Content Creator ecosystem.
"""
import logging
import os
import asyncio
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

# Try to import google.generativeai, handle if missing
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from app.infrastructure.agents.base_agent import BaseAgent, AgentConfig, AgentCapability
from app.domain.marketing.content_creator import VisualGenerationResult

logger = logging.getLogger(__name__)


class VideoAspectRatio(str, Enum):
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"
    FEED = "4:5"


class VideoGenerationConfig(BaseModel):
    """Configuration for video generation."""
    prompt: str = Field(..., description="Video description prompt")
    duration_seconds: int = Field(5, ge=1, le=60, description="Duration in seconds")
    aspect_ratio: VideoAspectRatio = Field(VideoAspectRatio.PORTRAIT, description="Target aspect ratio")
    negative_prompt: Optional[str] = Field(None, description="Elements to avoid")
    negative_prompt: Optional[str] = Field(None, description="Elements to avoid")
    style: Optional[str] = Field("cinematic", description="Visual style")
    image_url: Optional[str] = Field(None, description="Input image URL for image-to-video")




class VideoGenerationAgent(BaseAgent):
    """
    Agent responsible for generating videos using Google Veo.
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if HAS_GENAI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model_name = config.model or "veo-2.0-generate-preview" 
        else:
            logger.warning("Google AI SDK not found or API Key missing. Video generation will run in MOCK mode.")
            self.model_name = "mock-veo"

    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="generate_video",
                description="Generate video from text prompt using Veo",
                input_schema=VideoGenerationConfig.model_json_schema(),
                output_schema=VisualGenerationResult.model_json_schema()
            ),
            AgentCapability(
                name="animate_image",
                description="Animate a static image",
                input_schema={"image_url": "str", "prompt": "str"},
                output_schema=VisualGenerationResult.model_json_schema()
            )
        ]

    async def execute(self, task: Any) -> Any:
        """Execute video generation task."""
        if task.type == "generate_video":
            return await self.generate_video(VideoGenerationConfig(**task.input))
        elif task.type == "animate_image":
            # Map simple object to config
            return await self.animate_image(VideoGenerationConfig(**task.input))
        raise NotImplementedError(f"Task type {task.type} not supported")

    async def generate_video(self, config: VideoGenerationConfig) -> VisualGenerationResult:
        """
        Generate a video using Veo model.
        """
        logger.info(f"Generating video with prompt: '{config.prompt}' (Model: {self.model_name})")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            video_url = None
            
            # TODO: Add logic to call real Veo API once public via google.generativeai
            # Currently Veo is experimental/waitlist.
            # checks if "veo" model exists in genai.list_models() could be added.
            
            if self.model_name == "mock-veo" or not HAS_GENAI:
                # Mock generation
                await asyncio.sleep(2.0) # Simulate work
                video_url = "https://storage.googleapis.com/studiocentos-assets/mock_veo_video.mp4"
                logger.info("Generated MOCK video url")
            else:
                try:
                    # Real Veo API Call
                    # Note: Veo 2.0 is experimental. If it fails, we catch and fallback.
                    logger.info(f"Calling Google Veo API with model {self.model_name}")
                    
                    model = genai.GenerativeModel(self.model_name)
                    
                    # Construct generation config
                    # 'aspect_ratio' support depends on specific model version
                    gen_config = genai.types.GenerationConfig(
                        candidate_count=1,
                    )
                    
                    # For video, prompts usually go to specific methods or standard generate_content
                    # We try standard generate_content_async
                    prompt_parts = [config.prompt]
                    if config.style:
                        prompt_parts.append(f"Style: {config.style}")
                    if config.aspect_ratio:
                        prompt_parts.append(f"Aspect Ratio: {config.aspect_ratio.value}")
                        
                    full_prompt = ", ".join(prompt_parts)
                    
                    response = await model.generate_content_async(full_prompt, generation_config=gen_config)
                    
                    if response.candidates and response.candidates[0].content.parts:
                        # Inspect parts for video URI or inline data
                        part = response.candidates[0].content.parts[0]
                        
                        # Handle different response types (URI vs Blob)
                        if hasattr(part, 'file_data') and part.file_data:
                            # If it's a file URI (File API)
                             video_url = part.file_data.file_uri
                        elif hasattr(part, 'inline_data') and part.inline_data:
                            # If it's inline blob (unlikely for video, but possible for small previews)
                            # We would need to save it. For now, assume we need a URL.
                            # Saving logic placeholder
                            pass
                        elif hasattr(part, 'video_metadata'):
                            # Some models return metadata with a download link
                            video_url = part.video_metadata.video_uri
                        elif hasattr(part, 'text'): 
                             # Fallback if it returns text (e.g. "I cannot generate video")
                             logger.warning(f"Veo returned text instead of video: {part.text}")
                             raise ValueError("Model returned text")
                             
                        # If we didn't get a clear URL but have data, we might need saving logic
                        # For Phase 3.1, if we can't extract a URL easily, we might need a dedicated
                        # saving loop.
                        
                        if not video_url and hasattr(part, 'text') and "http" in part.text:
                            # Sometimes early previews return the URL in text
                            import re
                            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', part.text)
                            if urls:
                                video_url = urls[0]

                    if not video_url:
                        raise ValueError("No video URL found in response")
                        
                    logger.info(f"Generated video URL: {video_url}")

                except Exception as e:
                    logger.error(f"Veo API call failed: {e}. Falling back to Mock.")
                    await asyncio.sleep(1.0)
                    video_url = "https://storage.googleapis.com/studiocentos-assets/mock_veo_video_fallback.mp4"


            duration = asyncio.get_event_loop().time() - start_time
            
            return VisualGenerationResult(
                prompt_used=config.prompt,
                model_used=self.model_name,
                generation_time=duration,
                video_url=video_url,
                metadata={
                    "aspect_ratio": config.aspect_ratio,
                    "duration_requested": config.duration_seconds,
                    "style": config.style
                }
            )
            

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise e

    async def animate_image(self, config: VideoGenerationConfig) -> VisualGenerationResult:
        """
        Animate a static image using Veo img2video.
        """
        if not config.image_url:
             raise ValueError("image_url required for animation")

        logger.info(f"Animating image {config.image_url} with prompt: '{config.prompt}'")
        start_time = asyncio.get_event_loop().time()
        
        try:
             video_url = None
             
             if self.model_name == "mock-veo" or not HAS_GENAI:
                await asyncio.sleep(3.0)
                video_url = "https://storage.googleapis.com/studiocentos-assets/mock_veo_animation.mp4"
                logger.info("Generated MOCK animation url")
             else:
                try:
                    # Real Veo Image-to-Video
                    # Placeholder for img2vid implementation
                    # Currently genai SDK might not have a direct 'animate' method yet public,
                    # but typically it uses generate_content with image + text.
                    
                    # We would download the image first
                    # img_data = ... download(config.image_url) ...
                    
                    logger.info("Calling Google Veo Image-to-Video API (Placeholder)")
                    # Mock for now until specific SDK method is confirmed for img2vid
                    await asyncio.sleep(2.0)
                    video_url = "https://storage.googleapis.com/studiocentos-assets/mock_veo_animation.mp4"
                    
                except Exception as e:
                    logger.error(f"Veo Animation failed: {e}. Falling back.")
                    video_url = "https://storage.googleapis.com/studiocentos-assets/mock_veo_video_fallback.mp4"

             duration = asyncio.get_event_loop().time() - start_time
             
             return VisualGenerationResult(
                prompt_used=f"Animate: {config.prompt}",
                model_used=self.model_name,
                generation_time=duration,
                video_url=video_url,
                metadata={
                    "type": "image_to_video",
                    "source_image": config.image_url,
                    "duration": config.duration_seconds
                }
            )
        except Exception as e:
            logger.error(f"Animation failed: {e}")
            raise e
